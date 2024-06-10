<template>
    <div class="route-container">
        <HeaderBar />
        <main>
            <Navigation />
            <div class="px-5 py-8" style="width: 100%; max-width: 800px; margin: 0 auto; line-height: 1.65;">
                <h1>NX-Jikkyo とは</h1>
                <p class="mt-4 text-text-darken-1">
                    <strong>NX-Jikkyo は、<a class="link" href="https://blog.nicovideo.jp/niconews/225099.html" target="_blank">サイバー攻撃で期間未定の鯖落ち中</a> のニコニコ実況に代わる、ニコニコ実況民のための避難所であり、<a class="link" href="https://github.com/tsukumijima/NX-Jikkyo/blob/master/server/app/routers/comments.py" target="_blank">ニコニコ生放送互換の WebSocket API</a> を備えるコメントサーバーです。</strong><br>
                </p>
                <p class="mt-5 text-text-darken-1">
                    個人的にもニコニコ実況がすぐに復活してくれればそれが一番良いのですが、この感じだと残念ながら数週間はサーバーダウンが続きそうに思えます。<br>
                    2020年12月までのニコニコ実況は独立していたのですが、<a class="link" href="https://blog.nicovideo.jp/niconews/143148.html" target="_blank">Adobe Flash 廃止に伴いニコ生のチャンネル生放送として統合されてしまいました。</a><br>
                    よってニコ生本体が完全復旧しない限り、ニコニコ実況も当分復旧しそうにない状況です。
                </p>
                <p class="mt-2 text-text-darken-1">
                    ニコニコ実況が使えない時間が続けば続くほど、リアルタイムに実況できないのはもちろんのこと、録画でニコニコ実況の過去ログを見て作品を楽しむライフワークもできなくなってしまいます。<br>
                    3日程度ならともかく、数週間続く可能性を鑑みるとかなり受け入れ難いものです。
                </p>
                <p class="mt-5 text-text-darken-1">
                    <strong>そこで突貫工事ではありますが、ニコニコ生放送互換のサードパーティーツールが比較的対応しやすい技術仕様で、ニコニコ実況が使えない間のつなぎとしてテレビを実況できる、このサイトを開発しました。</strong>ソースコードは <a class="link" href="https://github.com/tsukumijima/NX-Jikkyo" target="_blank">GitHub</a> で公開しています。<br>
                </p>
                <blockquote class="mt-5 text-text-darken-1">
                    勘の良い方はおそらくお気づきの通り、このサイトは私が長年開発している <a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank">KonomiTV</a> の大半のソースコードを流用して開発しています。<br>
                    一部 UI が不自然な箇所がありますが、元々 KonomiTV のプレイヤーロジックはそのまま動画再生処理だけを強引に無効化し、コメント再生だけを行わせているためです。
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    ニコニコ実況の復活後のこのサイトの処遇はまだ決めていません。引き続き需要があれば、あるいはサーバー負荷の問題がなければ残す可能性も十分あります。
                </blockquote>
                <p class="mt-5 text-text-darken-1">
                    投稿いただいたコメントは自動的にデータベースに記録されます。書き込んだ瞬間だけでなく、後からでも過去ログを見れるように考慮して設計しています。<br>
                </p>
                <p class="mt-2 text-text-darken-1">
                    またシステム簡素化のため、意図的にアカウント不要で書き込めるようにしています（データベースに個人情報が保存されることは絶対にありません）。<br>
                    気軽にお使いいただけますが、マナーを守ってのご利用をお願いします。
                </p>
                <p class="mt-5 text-text-darken-1">
                    <strong>このサイトを公開した最大の理由は、十数年にも及ぶニコニコ実況の歴史上異常事態である、数週間に渡りテレビの過去ログコメントが完全に断たれる事態をなんとしてでも避けたいからです。</strong><br>
                    もちろん15時間で突貫で作ったサイトなのでバグも多いでしょうし、大量のコメントの負荷には耐えきれないかもしれません。しかし、コメントが全く残らないよりはマシだと考えています。
                </p>
                <p class="mt-2 text-text-darken-1">
                    まだ手間的に間に合ってはいないのですが、<strong>少なくともニコニコ実況が復活するまでに書き込んでいただいた過去ログは、後日私 (tsukumi) が責任を持って <a class="link" href="https://jikkyo.tsukumijima.net" target="_blank">ニコニコ実況 過去ログ API</a> で閲覧可能な過去ログとしてインポート・マージする予定です。</strong>
                </p>
                <blockquote class="mt-5 text-text-darken-1">
                    …ちなみに、NX-Jikkyo というサイト名は突貫開発をやる中でたまたま適当にひらめいた名前で、特に深い意味はありません。<br>
                    もう少しかっこいい名前が出てくれば良かったのですが、「Jikkyo」と入れないと何のサービスか分かりづらそうというのもあり…。
                </blockquote>
                <p class="mt-5 text-text-darken-1 text-right">
                    2024/06/10 <a class="link" href="https://blog.tsukumijima.net" target="_blank">tsukumi</a> (<a class="link" href="https://twitter.com/TVRemotePlus" target="_blank">Twitter@TVRemotePlus</a>)
                </p>
            </div>
        </main>
    </div>
</template>
<script lang="ts" setup>

import HeaderBar from '@/components/HeaderBar.vue';
import Navigation from '@/components/Navigation.vue';

</script>
<style lang="scss" scoped>

blockquote {
    border-left: 2px solid #e5e5d1;
    padding-left: 12px;
}

</style>
