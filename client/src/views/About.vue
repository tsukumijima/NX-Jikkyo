<template>
    <div class="route-container">
        <HeaderBar />
        <main>
            <Navigation />
            <div class="px-5 py-8" style="width: 100%; max-width: 850px; margin: 0 auto; line-height: 1.65;">
                <h1>NX-Jikkyo とは</h1>
                <p class="mt-4 text-text-darken-1">
                    <strong>NX-Jikkyo は、<a class="link" href="https://blog.nicovideo.jp/niconews/225099.html" target="_blank">サイバー攻撃で最低7月末まで鯖落ち中</a> のニコニコ実況に代わる、ニコニコ実況民のための避難所であり、<a class="link" href="https://github.com/tsukumijima/NX-Jikkyo/blob/master/server/app/routers/websocket.py" target="_blank">ニコニコ生放送互換の WebSocket API</a> を備えるコメントサーバーです。</strong><br>
                    お気に入りのソフトを使い続けながら、今まで通りテレビを楽しく実況できます。<br>
                </p>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong><a class="link" href="https://twitter.com/TVRemotePlus" target="_blank">Twitter@TVRemotePlus</a> やハッシュタグ <a class="link" href="https://x.com/search?q=%23NXJikkyo&src=typed_query" target="_blank">#NXJikkyo</a> では NX-Jikkyo の最新情報を発信しています！<br>ぜひチェックしてみてください🙏<br>
                    また <a class="link" href="https://www.amazon.co.jp/hz/wishlist/ls/3AZ4RI13SW2PV?tag=tsukumijima-22" target="_blank">干し芋 or アマギフ</a> をいただけると大変モチベが上がるのでよければぜひ🙇🙏 <a class="link" href="https://www.amazon.co.jp/hz/wishlist/ls/3AZ4RI13SW2PV?tag=tsukumijima-22" target="_blank">干し芋のリスト</a> は不定期で更新してます。<br></strong>
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong><a class="link" href="https://air.fem.jp/jkcommentviewer/" target="_blank">jkcommentviewer v2.3.7.3</a> 以降で、ニコニコ実況の代わりに NX-Jikkyo のコメントをリアルタイム表示できるようになりました！！🎉🎊<br></strong>
                    <a class="link" href="https://air.fem.jp/jkcommentviewer/" target="_blank">jkcommentviewer</a> + ニコニコ実況ユーザーの方は [基本設定] → [オプション] → [チャンネルリストの勢いを NX-Jikkyo から取得する] をオンにすると今まで通り実況コメントを表示できるようになるのでアプデ推奨です🙏<br>
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong><a class="link" href="https://github.com/DBCTRADO/TVTest" target="_blank">TVTest</a> のニコニコ実況表示プラグイン <a class="link" href="https://github.com/xtne6f/NicoJK/releases/tag/master-240613" target="_blank">NicoJK master-240613</a> 以降で、ニコニコ実況の代わりに NX-Jikkyo のコメントをリアルタイム表示できるようになりました！！🎉🎊<br></strong>
                    <a class="link" href="https://github.com/DBCTRADO/TVTest" target="_blank">TVTest</a> + ニコニコ実況ユーザーの方は NicoJK.ini を編集して NX-Jikkyo を有効にすると今まで通り実況コメントを表示できるようになるのでアプデ推奨です🙏<br>
                    <strong>NicoJK の更新方法の詳細は <a class="link" href="https://blog.tsukumijima.net/article/nx-jikkyo-released/#toc4" target="_blank">こちら</a> の記事に載せていますのでぜひ一読を🙇</strong>
                    <div class="mt-1"></div>
                    また <a class="link" href="https://github.com/noriokun4649/TVTComment" target="_blank">TVTComment</a> プラグインでも v3.0.1 以降で NX-Jikkyo 対応が追加されています！
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong><a class="link" href="https://github.com/tsukumijima/KonomiTV/releases/tag/v0.10.1" target="_blank">KonomiTV 0.10.1</a> 以降で、ニコニコ実況の代わりに NX-Jikkyo のコメントをリアルタイム表示できるようになりました！！🎉🎊<br></strong>
                    <a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank">KonomiTV</a> + ニコニコ実況ユーザーの方は [サーバー設定] → [ニコニコ実況の代わりに NX-Jikkyo からリアルタイムに実況コメントを取得する] をオンにすると今まで通り実況コメントを表示できるようになるのでアプデ推奨です🙏<br>
                </blockquote>
                <h2 class="mt-5">開発経緯</h2>
                <p class="mt-3 text-text-darken-1">
                    個人的にもニコニコ実況がすぐに復活してくれればそれが一番良かったのですが、<strong>2024/06/14 時点での <a class="link" href="https://blog.nicovideo.jp/niconews/225099.html" target="_blank">ニコニコインフォの報告</a> によれば、ニコニコ実況 (ニコニコ生放送公式チャンネル) の復旧は最短でも8月以降になりそうな極めて厳しい状況です。</strong><br>
                    2020年12月までのニコニコ実況は独立していたのですが、<a class="link" href="https://blog.nicovideo.jp/niconews/143148.html" target="_blank">Adobe Flash 廃止に伴いニコ生のチャンネル生放送として統合されてしまいました。</a><br>
                    よってニコ生本体が完全復旧しない限り、ニコニコ実況も当分復旧しそうにありません。<br>
                </p>
                <p class="mt-2 text-text-darken-1">
                    ニコニコ実況が使えない時間が続けば続くほど、リアルタイムに実況できないのはもちろんのこと、録画でニコニコ実況の過去ログを見て作品を楽しむライフワークもできなくなってしまいます。<br>
                    1ヶ月以上もテレビを実況できない生活は相当に受け入れ難いものです。
                </p>
                <p class="mt-5 text-text-darken-1">
                    <strong>そこで突貫工事ではありますが、ニコニコ生放送互換のサードパーティーツールが比較的対応しやすい技術仕様で、ニコニコ実況が使えない間のつなぎとしてテレビを実況できる、このサイトを開発しました。</strong><br>
                </p>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong>ぜひこのサイトをまだ NX-Jikkyo を知らないニコニコ実況難民の方に広めていただけると嬉しいです！</strong><br>
                    コメントサーバーの負荷問題は……なんとかします…！現時点での最大瞬間ユーザー数の数倍程度なら今のサーバーでも捌けそうな状況です。<br>
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong>NX-Jikkyo を「<a class="link" href="https://support.google.com/chrome/answer/9658361" target="_blank">ホーム画面に追加</a>」することで、PC のデスクトップやスマホのホーム画面から普通のアプリのように起動できます！特にスマホで実況している方におすすめです。</strong>
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    ソースコードは <a class="link" href="https://github.com/tsukumijima/NX-Jikkyo" target="_blank">GitHub</a> で公開しています。<a class="link" href="/api/v1/docs" target="_blank">API ドキュメント</a> もあります。<br>
                    WebSocket API のドキュメントは <a class="link" href="https://github.com/tiangolo/fastapi" target="_blank">FastAPI</a> が API ドキュメントを自動生成してくれないため現状ありませんが、ニコ生の WebSocket API のドロップイン代替として機能するはずです。<br>
                    <div class="mt-1"></div>
                    勘の良い方はおそらくお気づきの通り、このサイトは私が長年開発している <a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank">KonomiTV</a> の大半のソースコードを流用して開発しています。<br>
                    一部 UI が不自然な箇所がありますが、元々 KonomiTV のプレイヤーロジックはそのまま動画再生処理だけを強引に無効化し、コメント再生だけを行わせているためです。
                </blockquote>
                <h2 class="mt-5">運用方針</h2>
                <p class="mt-3 text-text-darken-1">
                    投稿いただいたコメントは自動的にデータベースに記録されます。書き込んだ瞬間だけでなく、後からでも過去ログを見れるように考慮して設計しています。<br>
                </p>
                <p class="mt-2 text-text-darken-1">
                    またシステム簡素化のため、意図的にアカウント不要で書き込めるようにしています（データベースに個人情報が保存されることは絶対にありません）。<br>
                    気軽にお使いいただけますが、マナーを守ってのご利用をお願いします。
                </p>
                <blockquote class="mt-5 text-text-darken-1">
                    ニコニコ実況の復活後のこのサイトの処遇は未定です。ニコニコ実況復活後も引き続き需要があれば、あるいはサーバー負荷的に大丈夫そうなら、継続する可能性も十分あります。
                </blockquote>
                <hr class="mt-5">
                <p class="mt-5 text-text-darken-1">
                    <strong>このサイトを公開した最大の理由は、十数年にも及ぶニコニコ実況の歴史上異常事態である、1ヶ月以上に渡りテレビの過去ログコメントが完全に断たれる事態をなんとしてでも避けたいからです。</strong><br>
                    もちろん元々15時間で突貫で作ったサイトなのでバグも多いでしょうし、大量のコメントの負荷には耐えきれないかもしれません（随時改善中です）。しかし、コメントが全く残らないよりはマシだと考えています。
                </p>
                <blockquote class="mt-2 text-text-darken-1">
                    <strong>NX-Jikkyo に書き込んでいただいたコメントの過去ログは、順次 <a class="link" href="https://jikkyo.tsukumijima.net" target="_blank">ニコニコ実況 過去ログ API</a> で取得できるよう反映されています！ご安心ください…！</strong>
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    …ちなみに、NX-Jikkyo というサイト名は突貫開発をやる中でたまたま適当にひらめいた名前で、特に深い意味はありません。<br>
                    もう少しかっこいい名前が出てくれば良かったのですが、「Jikkyo」と入れないと何のサービスか分かりづらそうというのもあり…。
                </blockquote>
                <h2 class="mt-5">動作環境</h2>
                <div class="mt-3">
                    <strong>PC: Google Chrome</strong><br>
                    <ul class="pl-5 mt-3 text-text-darken-1">
                        <li>Firefox でも動作するはずですが、コメント描画が重めなことが確認されています。</li>
                        <li>動作確認も基本行っておらず、積極的なサポートはしていません。Chrome を使うことをおすすめします。</li>
                        <li>Mac Safari はサポートしていません。Mac でも Chrome を使ってください。</li>
                    </ul>
                </div>
                <div class="mt-3">
                    <strong>Android: Google Chrome</strong><br>
                    <ul class="pl-5 mt-3 text-text-darken-1">
                        <li>Android の Firefox はサポートしていません。</li>
                    </ul>
                </div>
                <div class="mt-3">
                    <strong>iPhone (iOS) / iPad (iPadOS): Safari</strong><br>
                    <ul class="pl-5 mt-3 text-text-darken-1">
                        <li>iOS / iPadOS 17.1 以降のみに対応しています。</li>
                        <li>動作確認は iOS / iPadOS 17.1 以降で行っています。</li>
                        <li>iOS / iPadOS の Chrome (WKWebView) はサポートしていません。</li>
                        <li>Safari は全体的にバグが多く開発が大変なため、全体的にあまり動作確認を行えていません。修正できていない不具合があるかもしれません。</li>
                    </ul>
                </div>
                <p class="mt-5 text-text-darken-1 text-right">
                    2024/06/10 (Last Update: 2024/06/20)<br>
                    <a class="link" href="https://blog.tsukumijima.net" target="_blank">tsukumi</a>
                    (<a class="link" href="https://twitter.com/TVRemotePlus" target="_blank">Twitter@TVRemotePlus</a> /
                    <a class="link" href="https://blog.tsukumijima.net/" target="_blank">Blog</a> /
                    <a class="link" href="https://github.com/tsukumijima" target="_blank">GitHub</a>)
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
    border-left: 3px solid rgb(var(--v-theme-secondary));
    background-color: rgb(var(--v-theme-background-lighten-1));
    padding: 12px 16px;
    border-radius: 4px;
}
hr {
    border-color: rgb(var(--v-theme-text-darken-2));
}

</style>
