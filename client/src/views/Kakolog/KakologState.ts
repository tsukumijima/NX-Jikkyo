
import { ref, provide, inject, InjectionKey, Ref } from 'vue';

import { dayjs } from '@/utils';


interface KakologState {
    jikkyo_channel_id: Ref<string>
    start_date: Ref<string>
    start_time: Ref<string>
    end_date: Ref<string>
    end_time: Ref<string>
}

const KakologStateKey: InjectionKey<KakologState> = Symbol('KakologState');

export function provideKakologState() {
    const now = dayjs().minute(0).second(0);

    const state = {
        jikkyo_channel_id: ref('jk1'),
        // 開始日時（終了日時の1時間前）
        start_date: ref(now.subtract(1, 'hour').format('YYYY-MM-DD')),
        start_time: ref(now.subtract(1, 'hour').format('HH:mm')),
        // 終了日時（現在日時の分と秒を0にしたもの）
        end_date: ref(now.format('YYYY-MM-DD')),
        end_time: ref(now.format('HH:mm')),
    };

    provide(KakologStateKey, state);
}

export function useKakologState() {
    const state = inject(KakologStateKey);
    if (!state) {
        throw new Error('KakologState not provided');
    }
    return state;
}
