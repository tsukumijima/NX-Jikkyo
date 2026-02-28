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
# 大きすぎると InnoDB のアンドゥログが肥大化するため 10,000 件が目安
BATCH_SIZE="${BATCH_SIZE:-10000}"
# COPY/DELETE で個別にバッチサイズを調整したい場合は、それぞれ上書きできるようにする
COPY_BATCH_SIZE="${COPY_BATCH_SIZE:-${BATCH_SIZE}}"
DELETE_BATCH_SIZE="${DELETE_BATCH_SIZE:-${BATCH_SIZE}}"

# バッチ間のスリープ時間（秒）
# 本番環境への I/O 負荷を抑えるために間隔を設ける
SLEEP_INTERVAL="${SLEEP_INTERVAL:-0.3}"

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
# archived_comments に未コピーの id のみを対象に、date < ARCHIVE_BEFORE_DATE の範囲で
# BATCH_SIZE 件ずつ INSERT する。途中で中断しても再実行すると続きから始まる。
print_step "Step 2: Copy comments to archived_comments (batch INSERT)"
copy_start_epoch_milliseconds=$(current_epoch_milliseconds)

already_copied=$(MYSQL -sN -e "SELECT COUNT(*) FROM archived_comments;")
already_copied=$(require_integer_result "${already_copied}" 'Step 2 already copied')
print_info "Already copied: ${already_copied} / ${target_count} rows"

batch_num=0
copied_so_far="${already_copied}"
while true; do
        # archived_comments に未コピーの行のみを抽出して INSERT する
        # こうすることで既存データ量に依存せず、再実行時も安全に追記できる
        result=$(MYSQL -sN << EOF
INSERT INTO archived_comments
    SELECT c.*
    FROM comments c
    LEFT JOIN archived_comments a ON a.id = c.id
    WHERE a.id IS NULL
      AND c.date < '${ARCHIVE_BEFORE_DATE}'
    ORDER BY c.id
    LIMIT ${COPY_BATCH_SIZE};
SELECT ROW_COUNT();
EOF
)
    inserted=$(echo "${result}" | tr -d '\r' | awk 'NF { last=$0 } END { print last }')
    inserted=$(require_integer_result "${inserted}" 'Step 2 ROW_COUNT')
    batch_num=$((batch_num + 1))
    if [ "${inserted}" -eq "0" ]; then
        break
    fi
    copied_so_far=$((copied_so_far + inserted))
    print_info "  Batch ${batch_num}: inserted ${inserted} rows (total copied: ${copied_so_far} / ${target_count})"
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
    batch_num=0
    deleted_total=0
    while true; do
        result=$(MYSQL -sN << EOF
DELETE FROM comments WHERE date < '${ARCHIVE_BEFORE_DATE}' ORDER BY id LIMIT ${DELETE_BATCH_SIZE};
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
