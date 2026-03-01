#!/bin/bash

# comments テーブルの古いレコードを archived_comments テーブルに移行するスクリプト
# バッファプール不足によるパフォーマンス問題の根本対策として、古いコメントを
# 参照頻度の低い別テーブルに退避し、comments テーブルを小さく保つ。
#
# 設計方針:
#   - archived_comments は comments と同じスキーマを持つが、API からは参照されない
#   - 過去ログは JKCommentCrawler (KakologArchives) に保存済みのため、データは保全されている
#   - 多重実行・途中中断・再実行に対して安全（冪等性を保証）
#
# 実行前の確認事項:
#   - mysqldump.sh で事前にバックアップを取得しておくこと
#   - アクセスが少ない深夜〜早朝（JST 01:00〜03:30 ごろ）に実行することを推奨
#   - ARCHIVE_BEFORE_DATE より前のコメントが全て archived_comments に移動される
#
# 使い方:
#   cd /home/ubuntu/NX-Jikkyo/server
#   ./misc/ArchiveComments.sh

set -euo pipefail

# スクリプトの場所から NX-Jikkyo ルートディレクトリに移動
cd "$(dirname "$(readlink -f "$0")")/../.."

# アーカイブ対象の境界日付（この日付より前のコメントをアーカイブする）
ARCHIVE_BEFORE_DATE="${ARCHIVE_BEFORE_DATE:-2025-07-01}"

# バッチサイズ（1回の INSERT/DELETE で処理する行数）
# 本番運用時の安定性とスループットのバランスとして 20,000 件をデフォルトにする
BATCH_SIZE="${BATCH_SIZE:-20000}"
# COPY/DELETE で個別にバッチサイズを調整したい場合は、それぞれ上書きできるようにする
COPY_BATCH_SIZE="${COPY_BATCH_SIZE:-${BATCH_SIZE}}"
DELETE_BATCH_SIZE="${DELETE_BATCH_SIZE:-${BATCH_SIZE}}"

# バッチ間のスリープ時間（秒）
# 同時稼働中の書き込み/読み込みへの影響を緩和するため、短い待機を入れる
SLEEP_INTERVAL="${SLEEP_INTERVAL:-0.1}"

# .env ファイルから MySQL のルートパスワードを取得
MYSQL_ROOT_PASSWORD=$(grep -oP '(?<=MYSQL_PASSWORD=).+' .env)
MYSQL_DATABASE=$(grep -oP '(?<=MYSQL_DATABASE=).+' .env)
MYSQL_DATABASE="${MYSQL_DATABASE_OVERRIDE:-${MYSQL_DATABASE}}"

# MySQL コマンドのエイリアス
MYSQL() {
    docker exec -i -e MYSQL_PWD="${MYSQL_ROOT_PASSWORD}" nx-jikkyo-mysql mysql -u root "${MYSQL_DATABASE}" "$@"
}

# 進捗表示用のヘルパー関数
log_timestamp() { date '+%Y/%m/%d %H:%M:%S.%3N'; }
log_line() {
    local level="$1"
    local message="$2"
    local level_prefix
    level_prefix=$(printf '%-10s' "${level}:")
    echo "[$(log_timestamp)] ${level_prefix} ${message}"
}
print_step() {
    log_line 'INFO' '======================================'
    log_line 'INFO' "  $*"
    log_line 'INFO' '======================================'
}
print_info() { log_line 'INFO' "$*"; }
print_warn() { log_line 'WARNING' "$*"; }
print_done() { log_line 'DONE' "$*"; }

current_epoch_milliseconds() { date '+%s%3N'; }
format_duration_milliseconds() {
    local duration_milliseconds="$1"
    local total_seconds=$((duration_milliseconds / 1000))
    local milliseconds=$((duration_milliseconds % 1000))
    local hours=$((total_seconds / 3600))
    local minutes=$(((total_seconds % 3600) / 60))
    local seconds=$((total_seconds % 60))
    printf '%02d:%02d:%02d.%03d' "${hours}" "${minutes}" "${seconds}" "${milliseconds}"
}
format_rows_per_second() {
    local rows="$1"
    local elapsed_milliseconds="$2"

    if [ "${elapsed_milliseconds}" -le "0" ]; then
        echo 'N/A'
        return
    fi
    awk "BEGIN { printf \"%.2f\", ${rows} / (${elapsed_milliseconds} / 1000.0) }"
}

# MySQL クエリ結果が非空かつ整数であることを検証し、値を返す
require_integer_result() {
    local value="$1"
    local context="$2"

    if [ -z "${value}" ]; then
        print_warn "${context}: empty result detected."
        exit 1
    fi
    if ! [[ "${value}" =~ ^-?[0-9]+$ ]]; then
        print_warn "${context}: non-integer result detected: ${value}"
        exit 1
    fi
    echo "${value}"
}

script_start_epoch_milliseconds=$(current_epoch_milliseconds)
print_info 'NX-Jikkyo comments archive migration script'
print_info "Archive target: comments.date < ${ARCHIVE_BEFORE_DATE}"

# Step 0: 現在の状態を確認して実行が必要かどうかを判定
print_step "Step 0: Pre-flight check"

comments_total=$(MYSQL -sN -e "SELECT COUNT(*) FROM comments;")
comments_total=$(require_integer_result "${comments_total}" 'Pre-flight comments total')
archive_exists=$(MYSQL -sN -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${MYSQL_DATABASE}' AND table_name='archived_comments';")
archive_exists=$(require_integer_result "${archive_exists}" 'Pre-flight archive table exists')
archive_count=0
if [ "${archive_exists}" -gt "0" ]; then
    archive_count=$(MYSQL -sN -e "SELECT COUNT(*) FROM archived_comments;")
    archive_count=$(require_integer_result "${archive_count}" 'Pre-flight archived_comments count')
fi
target_count=$(MYSQL -sN -e "SELECT COUNT(*) FROM comments WHERE date < '${ARCHIVE_BEFORE_DATE}';")
target_count=$(require_integer_result "${target_count}" 'Pre-flight archive target count')

print_info "comments total:         ${comments_total} rows"
print_info "archive target (< ${ARCHIVE_BEFORE_DATE}): ${target_count} rows"
if [ "${archive_exists}" -gt "0" ]; then
    print_info "archived_comments:      ${archive_count} rows (table exists)"
else
    print_info "archived_comments:      (table does not exist yet)"
fi

if [ "${target_count}" -eq "0" ]; then
    total_elapsed_milliseconds=$(( $(current_epoch_milliseconds) - script_start_epoch_milliseconds ))
    print_done "Migration already completed. Nothing to do. (elapsed: $(format_duration_milliseconds "${total_elapsed_milliseconds}"))"
    exit 0
fi

# Step 1: archived_comments テーブルを作成（存在しない場合のみ）
print_step "Step 1: Create archived_comments table"

if [ "${archive_exists}" -gt "0" ]; then
    print_info "Table already exists. Skipping creation."
else
    MYSQL -e "CREATE TABLE archived_comments LIKE comments;"
    # archived_comments は参照されないため、セカンダリインデックスは不要
    # PRIMARY KEY のみ保持することでアーカイブ自体のストレージも節約する
    MYSQL -e "ALTER TABLE archived_comments DROP INDEX idx_thread_id_id;"
    print_done "Table created (secondary index removed, PRIMARY KEY retained)."
fi

# Step 2: comments → archived_comments へのバッチ INSERT
# archived_comments の最大 id をチェックポイントとして、comments.id を前方にのみ走査する。
# これにより、毎バッチで先頭から再スキャンするコストを回避して、長時間実行時の劣化を防ぐ。
# 途中で中断しても、再実行時はチェックポイント以降から再開できる。
print_step "Step 2: Copy comments to archived_comments (batch INSERT)"
copy_start_epoch_milliseconds=$(current_epoch_milliseconds)

already_copied=$(MYSQL -sN -e "SELECT COUNT(*) FROM archived_comments;")
already_copied=$(require_integer_result "${already_copied}" 'Step 2 already copied')
print_info "Already copied: ${already_copied} / ${target_count} rows"
last_archived_id=$(MYSQL -sN -e "SELECT COALESCE(MAX(id), 0) FROM archived_comments;")
last_archived_id=$(require_integer_result "${last_archived_id}" 'Step 2 last archived id')
print_info "Resume checkpoint id:    ${last_archived_id}"

# チェックポイント以前の欠損を検出し、必要なら先に backfill する
if [ "${last_archived_id}" -gt "0" ]; then
    missing_before_checkpoint=$(MYSQL -sN << EOF
SELECT COUNT(*)
FROM comments c
LEFT JOIN archived_comments a ON a.id = c.id
WHERE c.id <= ${last_archived_id}
  AND c.date < '${ARCHIVE_BEFORE_DATE}'
  AND a.id IS NULL;
EOF
)
    missing_before_checkpoint=$(require_integer_result "${missing_before_checkpoint}" 'Step 2 missing rows before checkpoint')
    if [ "${missing_before_checkpoint}" -gt "0" ]; then
        print_warn "Detected ${missing_before_checkpoint} missing rows before checkpoint id. Running backfill before pre-clean."
        backfill_batch_num=0
        while true; do
            backfill_result=$(MYSQL -sN << EOF
INSERT INTO archived_comments
    SELECT c.*
    FROM comments c
    LEFT JOIN archived_comments a ON a.id = c.id
    WHERE c.id <= ${last_archived_id}
      AND c.date < '${ARCHIVE_BEFORE_DATE}'
      AND a.id IS NULL
    ORDER BY c.id
    LIMIT ${COPY_BATCH_SIZE};
SELECT ROW_COUNT();
EOF
)
            backfilled=$(echo "${backfill_result}" | tr -d '\r' | awk 'NF { print }' | sed -n '1p')
            backfilled=$(require_integer_result "${backfilled}" 'Step 2 backfill ROW_COUNT')
            backfill_batch_num=$((backfill_batch_num + 1))
            if [ "${backfilled}" -eq "0" ]; then
                break
            fi
            already_copied=$((already_copied + backfilled))
            copied_so_far="${already_copied}"
            print_info "  Backfill batch ${backfill_batch_num}: inserted ${backfilled} rows"
            sleep "${SLEEP_INTERVAL}"
        done
        print_done 'Backfill before checkpoint complete.'
    fi
fi

# 既に archived_comments にコピー済みの範囲を先に削除し、comments の肥大化を抑える
if [ "${last_archived_id}" -gt "0" ]; then
    print_info 'Pre-cleaning already copied rows from comments before copy loop...'
    preclean_batch_num=0
    preclean_deleted_total=0
    preclean_start_epoch_milliseconds=$(current_epoch_milliseconds)
    while true; do
        preclean_result=$(MYSQL -sN << EOF
DELETE FROM comments
WHERE id <= ${last_archived_id}
  AND date < '${ARCHIVE_BEFORE_DATE}'
ORDER BY id
LIMIT ${DELETE_BATCH_SIZE};
SELECT ROW_COUNT();
EOF
)
        preclean_deleted=$(echo "${preclean_result}" | tr -d '\r' | awk 'NF { print }' | sed -n '1p')
        preclean_deleted=$(require_integer_result "${preclean_deleted}" 'Step 2 pre-clean ROW_COUNT')
        preclean_batch_num=$((preclean_batch_num + 1))
        if [ "${preclean_deleted}" -eq "0" ]; then
            break
        fi
        preclean_deleted_total=$((preclean_deleted_total + preclean_deleted))
        print_info "  Pre-clean batch ${preclean_batch_num}: deleted ${preclean_deleted} rows (total: ${preclean_deleted_total})"
        sleep "${SLEEP_INTERVAL}"
    done
    preclean_elapsed_milliseconds=$(( $(current_epoch_milliseconds) - preclean_start_epoch_milliseconds ))
    preclean_rows_per_second=$(format_rows_per_second "${preclean_deleted_total}" "${preclean_elapsed_milliseconds}")
    print_done "Pre-clean complete. (elapsed: $(format_duration_milliseconds "${preclean_elapsed_milliseconds}"), throughput: ${preclean_rows_per_second} rows/s)"
fi

batch_num=0
copied_so_far="${already_copied}"
while true; do
    previous_last_archived_id="${last_archived_id}"
    # 前回までにコピー済みの最大 id より後ろだけを処理し、再スキャンを回避する
    result=$(MYSQL -sN << EOF
INSERT INTO archived_comments
    SELECT c.*
    FROM comments c
    WHERE c.id > ${last_archived_id}
      AND c.date < '${ARCHIVE_BEFORE_DATE}'
    ORDER BY c.id
    LIMIT ${COPY_BATCH_SIZE};
SELECT ROW_COUNT();
SELECT COALESCE(MAX(id), ${last_archived_id}) FROM archived_comments;
EOF
)
    inserted=$(echo "${result}" | tr -d '\r' | awk 'NF { print }' | sed -n '1p')
    inserted=$(require_integer_result "${inserted}" 'Step 2 ROW_COUNT')
    next_last_archived_id=$(echo "${result}" | tr -d '\r' | awk 'NF { print }' | sed -n '2p')
    next_last_archived_id=$(require_integer_result "${next_last_archived_id}" 'Step 2 checkpoint id')
    batch_num=$((batch_num + 1))
    if [ "${inserted}" -eq "0" ]; then
        break
    fi

    # 今回コピーした id 範囲を即時に削除し、comments の肥大化を抑え続ける
    interleaved_delete_result=$(MYSQL -sN << EOF
DELETE FROM comments
WHERE id > ${previous_last_archived_id}
  AND id <= ${next_last_archived_id}
  AND date < '${ARCHIVE_BEFORE_DATE}';
SELECT ROW_COUNT();
EOF
)
    interleaved_deleted=$(echo "${interleaved_delete_result}" | tr -d '\r' | awk 'NF { print }' | sed -n '1p')
    interleaved_deleted=$(require_integer_result "${interleaved_deleted}" 'Step 2 interleaved delete ROW_COUNT')

    last_archived_id="${next_last_archived_id}"
    copied_so_far=$((copied_so_far + inserted))
    print_info "  Batch ${batch_num}: inserted ${inserted} rows, deleted ${interleaved_deleted} rows (total copied: ${copied_so_far} / ${target_count}, checkpoint id: ${last_archived_id})"
    sleep "${SLEEP_INTERVAL}"
done
copy_elapsed_milliseconds=$(( $(current_epoch_milliseconds) - copy_start_epoch_milliseconds ))
copied_in_this_run=$((copied_so_far - already_copied))
copy_rows_per_second=$(format_rows_per_second "${copied_in_this_run}" "${copy_elapsed_milliseconds}")
print_done "Copy complete. (elapsed: $(format_duration_milliseconds "${copy_elapsed_milliseconds}"), throughput: ${copy_rows_per_second} rows/s)"

# Step 3: comments からアーカイブ対象をバッチ DELETE
# comments.date < ARCHIVE_BEFORE_DATE の行が 0 件になるまで BATCH_SIZE 件ずつ削除する。
# 既に全件削除済みの場合は何もしない（冪等）。
print_step "Step 3: Delete archived rows from comments (batch DELETE)"
delete_start_epoch_milliseconds=$(current_epoch_milliseconds)

remaining=$(MYSQL -sN -e "SELECT COUNT(*) FROM comments WHERE date < '${ARCHIVE_BEFORE_DATE}';")
remaining=$(require_integer_result "${remaining}" 'Step 3 remaining rows')
print_info "Rows remaining to delete: ${remaining}"

if [ "${remaining}" -eq "0" ]; then
    print_done "Delete already complete. Skipping."
else
    # コピー済み id 範囲だけを削除対象に絞ることで、不要な範囲スキャンを抑える
    max_archived_id_for_delete=$(MYSQL -sN -e "SELECT COALESCE(MAX(id), 0) FROM archived_comments;")
    max_archived_id_for_delete=$(require_integer_result "${max_archived_id_for_delete}" 'Step 3 max archived id')
    print_info "Delete upper bound id:   ${max_archived_id_for_delete}"
    missing_before_delete=$(MYSQL -sN << EOF
SELECT COUNT(*)
FROM comments c
LEFT JOIN archived_comments a ON a.id = c.id
WHERE c.id <= ${max_archived_id_for_delete}
  AND c.date < '${ARCHIVE_BEFORE_DATE}'
  AND a.id IS NULL;
EOF
)
    missing_before_delete=$(require_integer_result "${missing_before_delete}" 'Step 3 missing rows before delete')
    if [ "${missing_before_delete}" -gt "0" ]; then
        print_warn "Detected ${missing_before_delete} rows that are not archived in delete range. Abort to prevent data loss."
        exit 1
    fi

    batch_num=0
    deleted_total=0
    while true; do
        result=$(MYSQL -sN << EOF
DELETE FROM comments
WHERE id IN (
    SELECT delete_target_ids.id
    FROM (
        SELECT c.id
        FROM comments c
        INNER JOIN archived_comments a ON a.id = c.id
        WHERE c.id <= ${max_archived_id_for_delete}
          AND c.date < '${ARCHIVE_BEFORE_DATE}'
        ORDER BY c.id
        LIMIT ${DELETE_BATCH_SIZE}
    ) AS delete_target_ids
);
SELECT ROW_COUNT();
EOF
)
        deleted=$(echo "${result}" | tr -d '\r' | awk 'NF { last=$0 } END { print last }')
        deleted=$(require_integer_result "${deleted}" 'Step 3 ROW_COUNT')
        batch_num=$((batch_num + 1))
        if [ "${deleted}" -eq "0" ]; then
            break
        fi
        deleted_total=$((deleted_total + deleted))
        print_info "  Batch ${batch_num}: deleted ${deleted} rows"
        sleep "${SLEEP_INTERVAL}"
    done
    delete_elapsed_milliseconds=$(( $(current_epoch_milliseconds) - delete_start_epoch_milliseconds ))
    delete_rows_per_second=$(format_rows_per_second "${deleted_total}" "${delete_elapsed_milliseconds}")
    print_done "Delete complete. (elapsed: $(format_duration_milliseconds "${delete_elapsed_milliseconds}"), throughput: ${delete_rows_per_second} rows/s)"
fi

# Step 4: OPTIMIZE TABLE で削除後の空き領域をページから回収する
# テーブルを再構築するため時間がかかるが、バッファプール使用量を実際に削減するために必要
print_step "Step 4: OPTIMIZE TABLE comments"
optimize_start_epoch_milliseconds=$(current_epoch_milliseconds)

print_info "Running OPTIMIZE TABLE... (this may take several minutes)"
while IFS= read -r optimize_output_line; do
    if [ -n "${optimize_output_line}" ]; then
        print_info "  ${optimize_output_line}"
    fi
done < <(MYSQL -e "OPTIMIZE TABLE comments;")
optimize_elapsed_milliseconds=$(( $(current_epoch_milliseconds) - optimize_start_epoch_milliseconds ))
print_done "Optimize complete. (elapsed: $(format_duration_milliseconds "${optimize_elapsed_milliseconds}"))"

# 最終状態を確認して表示
print_step "Summary"
final_comments=$(MYSQL -sN -e "SELECT COUNT(*) FROM comments;")
final_archive=$(MYSQL -sN -e "SELECT COUNT(*) FROM archived_comments;")
final_comments=$(require_integer_result "${final_comments}" 'Summary comments total')
final_archive=$(require_integer_result "${final_archive}" 'Summary archived_comments total')
print_info "comments total (after):  ${final_comments} rows"
print_info "archived_comments total: ${final_archive} rows"
total_elapsed_milliseconds=$(( $(current_epoch_milliseconds) - script_start_epoch_milliseconds ))
print_done "Archive migration completed successfully. (elapsed: $(format_duration_milliseconds "${total_elapsed_milliseconds}"))"
