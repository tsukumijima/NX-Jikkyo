
import { ref, provide, inject, watch, InjectionKey, Ref } from 'vue';

import { dayjs } from '@/utils';


/** localStorage に保存する過去ログ再生フォームの状態 */
export interface IKakologFormState {
    jikkyo_channel_id: string;
    start_date: string;
    start_time: string;
    end_date: string;
    end_time: string;
}

interface KakologState {
    jikkyo_channel_id: Ref<string>;
    start_date: Ref<string>;
    start_time: Ref<string>;
    end_date: Ref<string>;
    end_time: Ref<string>;
    is_restored_from_local_storage: Ref<boolean>;
}

const KAKOLOG_FORM_LOCAL_STORAGE_KEY = 'NX-Jikkyo-Kakolog-Form';

const KakologStateKey: InjectionKey<KakologState> = Symbol('KakologState');

/**
 * 過去ログ再生フォームのデフォルト値（終了=現在時刻の分切り捨て、開始=1時間前）を返す
 * @returns デフォルトのフォーム状態
 */
function getDefaultKakologFormState(): IKakologFormState {

    const now = dayjs().minute(0).second(0);
    const start = now.subtract(1, 'hour');

    return {
        jikkyo_channel_id: 'jk1',
        start_date: start.format('YYYY-MM-DD'),
        start_time: start.format('HH:mm'),
        end_date: now.format('YYYY-MM-DD'),
        end_time: now.format('HH:mm'),
    };
}

/**
 * 過去ログ再生フォームの状態が有効かどうかを検証する
 * @param form 検証対象のフォーム状態
 * @returns 有効な場合は null、無効な場合はエラーメッセージ
 */
export function validateKakologFormState(form: IKakologFormState): string | null {

    const start_datetime = dayjs(`${form.start_date} ${form.start_time}`);
    const end_datetime = dayjs(`${form.end_date} ${form.end_time}`);

    // 日時パース失敗
    if (start_datetime.isValid() === false || end_datetime.isValid() === false) {
        return '開始日時または終了日時が無効です。';
    }

    // 12時間以上
    if (end_datetime.diff(start_datetime, 'hour') >= 12) {
        return '一度に再生できる過去ログは12時間以内です。';
    }

    // 終了が開始より前
    if (end_datetime < start_datetime) {
        return '指定された終了日時が開始日時より前です。';
    }

    // 終了が未来
    if (end_datetime > dayjs()) {
        return '指定された終了日時が未来の日付です。';
    }

    // 開始と終了が同一
    if (start_datetime.isSame(end_datetime)) {
        return '指定された開始日時と終了日時が同じです。';
    }

    return null;
}

/**
 * 過去ログ再生フォームの状態が有効かどうかを返す
 * @param form 検証対象のフォーム状態
 * @returns 有効な場合は true
 */
export function isValidKakologFormState(form: IKakologFormState): boolean {
    return validateKakologFormState(form) === null;
}

/**
 * localStorage から過去ログ再生フォームの状態を読み込む
 * @returns 有効な保存値、または null
 */
function loadKakologFormStateFromLocalStorage(): IKakologFormState | null {

    const raw = localStorage.getItem(KAKOLOG_FORM_LOCAL_STORAGE_KEY);
    if (raw === null) {
        return null;
    }

    try {
        const parsed = JSON.parse(raw) as Partial<IKakologFormState>;

        // 必須フィールドが揃っているか確認
        if (
            typeof parsed.jikkyo_channel_id !== 'string' ||
            typeof parsed.start_date !== 'string' ||
            typeof parsed.start_time !== 'string' ||
            typeof parsed.end_date !== 'string' ||
            typeof parsed.end_time !== 'string'
        ) {
            return null;
        }

        const form: IKakologFormState = {
            jikkyo_channel_id: parsed.jikkyo_channel_id,
            start_date: parsed.start_date,
            start_time: parsed.start_time,
            end_date: parsed.end_date,
            end_time: parsed.end_time,
        };

        // 保存値が現在のバリデーション規則を満たさない場合は復元しない
        if (isValidKakologFormState(form) === false) {
            return null;
        }

        return form;
    } catch {
        return null;
    }
}

/**
 * 過去ログ再生フォームの状態を localStorage に保存する
 * @param form 保存するフォーム状態
 */
function saveKakologFormStateToLocalStorage(form: IKakologFormState): void {
    localStorage.setItem(KAKOLOG_FORM_LOCAL_STORAGE_KEY, JSON.stringify(form));
}

/**
 * ref 群から過去ログ再生フォームの状態オブジェクトを組み立てる
 * @param state KakologState の ref 群
 * @returns フォーム状態
 */
function getKakologFormStateFromRefs(state: KakologState): IKakologFormState {
    return {
        jikkyo_channel_id: state.jikkyo_channel_id.value,
        start_date: state.start_date.value,
        start_time: state.start_time.value,
        end_date: state.end_date.value,
        end_time: state.end_time.value,
    };
}

/**
 * フォーム状態を ref 群に反映する
 * @param state KakologState の ref 群
 * @param form 反映するフォーム状態
 */
function applyKakologFormStateToRefs(state: KakologState, form: IKakologFormState): void {
    state.jikkyo_channel_id.value = form.jikkyo_channel_id;
    state.start_date.value = form.start_date;
    state.start_time.value = form.start_time;
    state.end_date.value = form.end_date;
    state.end_time.value = form.end_time;
}

/**
 * 過去ログ再生フォームの状態を現在日時ベースのデフォルト値にリセットする
 * @param state KakologState の ref 群
 */
export function resetKakologFormStateToCurrentDateTime(state: KakologState): void {

    const default_form = getDefaultKakologFormState();
    applyKakologFormStateToRefs(state, default_form);
    state.is_restored_from_local_storage.value = false;

    // リセット後の値を即座に保存
    saveKakologFormStateToLocalStorage(default_form);
}

export function provideKakologState() {

    const saved_form = loadKakologFormStateFromLocalStorage();
    const initial_form = saved_form ?? getDefaultKakologFormState();

    const state: KakologState = {
        jikkyo_channel_id: ref(initial_form.jikkyo_channel_id),
        start_date: ref(initial_form.start_date),
        start_time: ref(initial_form.start_time),
        end_date: ref(initial_form.end_date),
        end_time: ref(initial_form.end_time),
        is_restored_from_local_storage: ref(saved_form !== null),
    };

    // フォーム変更を debounce して localStorage に保存
    let save_timeout_id: ReturnType<typeof setTimeout> | null = null;
    watch(
        () => getKakologFormStateFromRefs(state),
        (form) => {
            if (save_timeout_id !== null) {
                clearTimeout(save_timeout_id);
            }
            save_timeout_id = setTimeout(() => {
                // 無効な途中入力は保存しない
                if (isValidKakologFormState(form) === true) {
                    saveKakologFormStateToLocalStorage(form);
                }
            }, 300);
        },
    );

    provide(KakologStateKey, state);
}

export function useKakologState() {
    const state = inject(KakologStateKey);
    if (!state) {
        throw new Error('KakologState not provided');
    }
    return state;
}
