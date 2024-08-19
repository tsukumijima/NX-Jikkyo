<template>
    <div class="route-container">
        <HeaderBar />
        <main>
            <Navigation />
            <div class="px-5 py-8" style="width: 100%; max-width: 850px; margin: 0 auto; line-height: 1.65;">
                <blockquote class="font-weight-bold" style="font-size: 15px;">
                    【📢重要なお知らせ】 NX-Jikkyo で <a class="link" href="https://x.com/TVRemotePlus/status/1821214317385282033" target="_blank">08/22 までの繋ぎ</a> で運用されている <a class="link" href="https://originalnews.nico/464285" target="_blank">暫定復旧版ニコニコ実況</a> に投稿されたコメントをリアルタイム表示できるようになりました！！🎉🎊 コメントリストではコメント取得元に応じてそれぞれ <code>[ニコ実]</code> or <code>[NX]</code> のラベルがつきます (各 NX-Jikkyo 対応アプリでは別途対応されない限り区別されません) 。<br>
                    <div class="mt-1">
                        NX-Jikkyo 対応アプリ (jkcommentviewer・TVTest (NicoJK)・KonomiTV など) は更新不要です。過去ログを含め、ニコニコ実況と NX-Jikkyo の双方に投稿されたコメントを一緒に楽しめます！🎧 <a class="link" href="/about/#faq" target="_blank">詳しくはこちら！</a>
                    </div>
                    <div class="mt-2" style="font-weight: 400 !important">
                        08/22 のニコニコ実況の本復旧後、<strong>NX-Jikkyo では本家ニコニコ実況へのコメント投稿機能をリリース予定です！！</strong><br>
                        <strong>本家ニコニコ実況へのコメント投稿にはニコニコアカウントとの連携が必要です。</strong>設定でコメント投稿先を切り替えれば、今まで通り NX-Jikkyo のコメントサーバーへのコメント投稿もできます (ログイン不要) 。
                    </div>
                </blockquote>
                <blockquote class="mt-5">
                    <strong>NX-Jikkyo を「<a class="link" href="https://support.google.com/chrome/answer/9658361" target="_blank">ホーム画面に追加</a>」することで、PC のデスクトップやスマホのホーム画面から普通のアプリのように起動できます！特にスマホで実況している方におすすめです。</strong>
                </blockquote>
                <h1 class="mt-5">NX-Jikkyo とは</h1>
                <p class="mt-4 text-text-darken-1">
                    <strong>NX-Jikkyo は、<a class="link" href="https://blog.nicovideo.jp/niconews/225099.html" target="_blank">サイバー攻撃の影響で 2024/06/08 ~ 08/05 まで鯖落ちしていた</a> ニコニコ実況に代わる、ニコニコ実況民のための避難所であり、<a class="link" href="https://github.com/tsukumijima/NX-Jikkyo/blob/master/server/app/routers/websocket.py" target="_blank">ニコニコ生放送互換の WebSocket API</a> を備えるコメントサーバーです。</strong>2024/06/10 から運営しています。<br>
                </p>
                <p class="mt-2 text-text-darken-1">
                    ニコニコ実況が復旧した現在では、<strong>「ニコニコ実況の Web 版非公式コメントビューア」＋「公式にない実況チャンネルを補完するコメントサーバー」</strong>として運営を続けています。<br>
                    <strong>お気に入りのアプリを使い続けながら、今まで通りテレビを楽しく快適に実況できます！</strong>
                </p>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong><a class="link" href="https://twitter.com/TVRemotePlus" target="_blank">Twitter@TVRemotePlus</a> やハッシュタグ <a class="link" href="https://x.com/search?q=%23NXJikkyo%20from%3ATVRemotePlus&src=typed_query&f=live" target="_blank">#NXJikkyo</a> では NX-Jikkyo の最新情報を発信しています！<br>ぜひチェックしてみてください🙏<br>
                    また <a class="link" href="https://www.amazon.co.jp/hz/wishlist/ls/3AZ4RI13SW2PV?tag=tsukumijima-22" target="_blank">干し芋 or アマギフ</a> をいただけると大変モチベが上がるのでよければぜひ🙇🙏 <a class="link" href="https://www.amazon.co.jp/hz/wishlist/ls/3AZ4RI13SW2PV?tag=tsukumijima-22" target="_blank">干し芋のリスト</a> は不定期で更新してます。<br></strong>
                    <div class="mt-2"></div>
                    あと何かショッピングする際は、<strong>ぜひ <a class="link" href="https://www.amazon.co.jp/dp/B0C1YY8GSB/?tag=tsukumijima-22" target="_blank">このアフィリンク</a> を通して Amazon でお買い物いただけると大変助かります🙏</strong>
                    （リンクと関係ない商品で大丈夫です！購入額の数%が <a class="link" href="https://affiliate.amazon.co.jp/help/node/topic/GRXPHT8U84RAYDXZ" target="_blank">紹介料</a> として私の収入になります）<br>
                    <div class="mt-2"></div>
                    <div style="font-size: 12.5px; line-height: 1.65;">このサイトは、Amazon.co.jp を宣伝しリンクすることによってサイトが紹介料を獲得できる手段を提供することを目的に設定されたアフィリエイトプログラムである、Amazon アソシエイト・プログラムの参加者です。</div>
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong><a class="link" href="https://air.fem.jp/jkcommentviewer/" target="_blank">jkcommentviewer v2.3.7.3</a> 以降で、ニコニコ実況の代わりに NX-Jikkyo のコメントをリアルタイム表示できるようになりました！！🎉🎊<br></strong>
                    <a class="link" href="https://air.fem.jp/jkcommentviewer/" target="_blank">jkcommentviewer</a> + ニコニコ実況ユーザーの方は [基本設定] → [オプション] → [チャンネルリストの勢いを NX-Jikkyo から取得する] をオンにすると今まで通り実況コメントを表示できるようになるのでアプデ推奨です🙏<br>
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong><a class="link" href="https://github.com/DBCTRADO/TVTest" target="_blank">TVTest</a> のニコニコ実況表示プラグイン <a class="link" href="https://github.com/xtne6f/NicoJK/releases" target="_blank">NicoJK master-240613</a> 以降で、ニコニコ実況の代わりに NX-Jikkyo のコメントをリアルタイム表示できるようになりました！！🎉🎊<br></strong>
                    <a class="link" href="https://github.com/DBCTRADO/TVTest" target="_blank">TVTest</a> + ニコニコ実況ユーザーの方は NicoJK.ini を編集して NX-Jikkyo を有効にすると今まで通り実況コメントを表示できるようになるのでアプデ推奨です🙏<br>
                    <strong>NicoJK の更新方法の詳細は <a class="link" href="https://blog.tsukumijima.net/article/nx-jikkyo-released/#toc4" target="_blank">こちら</a> の記事に載せていますのでぜひ一読を🙇</strong>
                    <div class="mt-1"></div>
                    また <a class="link" href="https://github.com/noriokun4649/TVTComment" target="_blank">TVTComment</a> プラグインでも v3.0.1 以降で NX-Jikkyo 対応が追加されています！
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong><a class="link" href="https://github.com/tsukumijima/KonomiTV/releases" target="_blank">KonomiTV 0.10.1</a> 以降で、ニコニコ実況の代わりに NX-Jikkyo のコメントをリアルタイム表示できるようになりました！！🎉🎊<br></strong>
                    <a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank">KonomiTV</a> + ニコニコ実況ユーザーの方は [サーバー設定] → [ニコニコ実況の代わりに NX-Jikkyo からリアルタイムに実況コメントを取得する] をオンにすると今まで通り実況コメントを表示できるようになるのでアプデ推奨です🙏<br>
                </blockquote>
                <h2 class="mt-5">開発経緯</h2>
                <p class="mt-3 text-text-darken-1">
                    個人的にもニコニコ実況がすぐに復活してくれればそれが一番良かったのですが、<strong>2024/06/14 当時の <a class="link" href="https://blog.nicovideo.jp/niconews/225099.html" target="_blank">ニコニコインフォの報告</a> によれば、ニコニコ実況 (ニコニコ生放送:チャンネル生放送) の復旧は最短でも8月以降になりそうな、極めて厳しい状況でした。</strong><br>
                    2020年12月までのニコニコ実況は独立していましたが、<a class="link" href="https://blog.nicovideo.jp/niconews/143148.html" target="_blank">Adobe Flash 廃止に伴いニコ生のチャンネル生放送として統合されてしまいました。</a><br>
                    よってニコ生本体が完全復旧しない限り、ニコニコ実況も当分復旧しそうにない状況でした。<br>
                </p>
                <p class="mt-2 text-text-darken-1">
                    ニコニコ実況が使えない時間が続けば続くほど、リアルタイムに実況できないのはもちろんのこと、録画でニコニコ実況の過去ログを見て作品を楽しむライフワークもできなくなってしまいます。<br>
                    1ヶ月以上もテレビを実況できない生活は相当に受け入れ難いものです。
                </p>
                <p class="mt-5 text-text-darken-1">
                    <strong>そこで突貫工事ではありますが、ニコニコ生放送互換のサードパーティーツールが比較的対応しやすい技術仕様で、ニコニコ実況が使えない間のつなぎとしてテレビを実況できる、このサイトを開発しました。</strong><br>
                </p>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong>ソースコードは <a class="link" href="https://github.com/tsukumijima/NX-Jikkyo" target="_blank">GitHub</a> で公開しています。<a class="link" href="/api/v1/docs" target="_blank">API ドキュメント</a> もあります。</strong><br>
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
                <hr class="mt-5">
                <p class="mt-5 text-text-darken-1">
                    <strong>このサイトを公開した最大の理由は、十数年にも及ぶニコニコ実況の歴史上異常事態である、2ヶ月近くに渡りテレビの過去ログコメントが完全に断たれる事態をなんとしてでも避けたかったからです。</strong>
                </p>
                <p class="mt-3 text-text-darken-1">
                    もちろん元々15時間で突貫で作ったサイトなので公開最初はバグも多かったですし、大量のコメントの負荷に耐えきれないこともありました。<br>
                    しかし、コメントが全く残らないよりはマシだと考え、日々サーバー負荷を改善しながら運営しています。
                </p>
                <blockquote class="mt-5 text-text-darken-1">
                    <strong>NX-Jikkyo に書き込んでいただいたコメントの過去ログは、順次 <a class="link" href="https://jikkyo.tsukumijima.net" target="_blank">ニコニコ実況 過去ログ API</a> で取得できるよう反映されています！ご安心ください…！</strong>
                </blockquote>
                <blockquote class="mt-5 text-text-darken-1">
                    …ちなみに、NX-Jikkyo というサイト名は突貫開発をやる中でたまたま適当にひらめいた名前で、特に深い意味はありません。
                    もう少しかっこいい名前が出てくれば良かったのですが、「Jikkyo」と入れないと何のサービスか分かりづらそうというのもあり…。<br>
                    あとコメントプレイヤーの背景は、私が過去に一眼レフで撮った写真から、選りすぐりの一枚をランダムでピックアップ表示しています。
                </blockquote>
                <h2 class="mt-5" id="faq" style="scroll-margin-top: 70px;">FAQ</h2>
                <ul class="pl-5 mt-3 text-text-darken-1" style="line-height: 1.65">
                    <li class="mt-3">
                        <strong>Q. いわゆる「コミュニティ実況」と NX-Jikkyo の関係について教えてください。</strong>
                    </li>
                    <li class="mt-2">
                        <strong>A. 詳しくは <a class="link" href="https://github.com/tsukumijima/JKCommentCrawler#%E3%81%84%E3%82%8F%E3%82%86%E3%82%8B%E3%82%B3%E3%83%9F%E3%83%A5%E3%83%8B%E3%83%86%E3%82%A3%E5%AE%9F%E6%B3%81%E3%81%A8-nx-jikkyo-%E3%81%AE%E9%96%A2%E4%BF%82%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6" target="_blank">こちらの記事</a> をご覧ください。</strong><br>
                    </li>
                </ul>
                <hr class="mt-4">
                <ul class="pl-5 mt-4 text-text-darken-1" style="line-height: 1.65">
                    <li class="mt-3">
                        <strong>Q. この NX-Jikkyo に投稿されたコメントは <a class="link" href="/log/" target="_blank">過去ログ再生</a> や <a class="link" href="https://jikkyo.tsukumijima.net" target="_blank">ニコニコ実況 過去ログ API</a> に反映されますか？</strong>
                    </li>
                    <li class="mt-2">
                        <strong>A. 本家ニコニコ実況と NX-Jikkyo 両方に投稿されたコメントを時系列で一緒にまとめた上で、随時収集・反映されています。</strong>
                        <ul class="pl-5 mt-1">
                            <li class="mt-1">過去ログの収集には <a class="link" href="https://github.com/tsukumijima/JKCommentCrawler" target="_blank">JKCommentCrawler</a> を利用しています。</li>
                            <li class="mt-1">もし明らかに何かコメントされているはずの時間帯で1件も過去ログがない場合は、<strong>当該期間の過去ログを正常に収集できていない可能性があります。</strong><br>
                                気づき次第 <a class="link" href="https://x.com/TVRemotePlus" target="_blank">Twitter</a> や <a class="link" href="https://forms.gle/C4jnW2jGX4H5AApSA" target="_blank">フィードバックフォーム</a> からご報告いただけると大変助かります。</li>
                        </ul>
                    </li>
                </ul>
                <hr class="mt-4">
                <ul class="pl-5 mt-4 text-text-darken-1" style="line-height: 1.65">
                    <li class="mt-3">
                        <strong>Q. NX-Jikkyo では、どのように <a class="link" href="https://jk.nicovideo.jp" target="_blank">ニコニコ実況</a> に投稿されたコメントをリアルタイム表示していますか？技術的な詳細を教えてください。</strong>
                    </li>
                    <li class="mt-2">
                        <strong>A. ニコニコ実況の各チャンネルに投稿されたコメントを NX-Jikkyo のサーバー側でリアルタイム受信し、随時 NX-Jikkyo のデータベースに通常のコメントとして「投稿」することで実現しています。</strong><br>
                        <ul class="pl-5 mt-1">
                            <li class="mt-1">ほぼすべてのコメントをリアルタイム表示できるよう努力していますが、<strong>NX-Jikkyo サーバーの再起動中や負荷状況によっては、瞬間的に一部のコメントが反映されない（取りこぼす）ことがあります。</strong><br>
                            過去ログ再生時（<a class="link" href="https://jikkyo.tsukumijima.net/" target="_blank">ニコニコ実況 過去ログ API</a> を含む）は、リアルタイムでは取りこぼしてしまったコメントも含む、本家ニコニコ実況と NX-Jikkyo 両方に投稿されたすべてのコメントを表示・再生できます。</li>
                            <li class="mt-1">ニコニコ実況に投稿されたコメントかどうかは、ユーザー ID に Prefix <code>nicolive:</code> が付与されているかどうかで判定できます。</li>
                            <li class="mt-1">ニコニコ実況のコメントをどのように表示する (分けて表示する or 区別せずに表示する or 表示しない) かは、各 NX-Jikkyo 対応サードパーティーアプリの方針にお任せします。</li>
                            <li class="mt-1"><a class="link" href="https://jikkyo.tsukumijima.net/" target="_blank">ニコニコ実況 過去ログ API</a> のレスポンスにはユーザー ID の Prefix が付かず、代わりに NX-Jikkyo に投稿されたコメントのみ <code>nx_jikkyo="1"</code> が付加されます。詳細は API ドキュメントをご確認ください。</li>
                        </ul>
                    </li>
                </ul>
                <hr class="mt-4">
                <ul class="pl-5 mt-4 text-text-darken-1" style="line-height: 1.65">
                    <li class="mt-3">
                        <strong>Q. なぜ復旧後の <a class="link" href="https://live.nicovideo.jp/" target="_blank">ニコニコ生放送</a> (ニコニコ実況) にまだ対応できていないサードパーティーアプリ (ニコ生コメントビューア・ニコニコ実況クライアントなど) が多いんですか？</strong>
                    </li>
                    <li class="mt-1">
                        <strong>A. サイバー攻撃以前のニコニコ生放送とはコメントサーバーの API 互換性がなく（要は全くの別物）、移行するには多大な改修コストがかかるためです。</strong>
                        <ul class="pl-5 mt-1">
                            <li class="mt-1">元々ニコニコ生放送にはオンプレから AWS へのサーバー移行計画があり、その際にクラウドネイティブに新規開発した新コメントサーバー (NDGR) で従来のコメントサーバー (niwavided) を置き換える予定でした。今回のサイバー攻撃により AWS 移行が当初よりも前倒しで進められた影響で、復旧後のニコニコ生放送では、コメントサーバーが NDGR 新コメントサーバーに置き換えられています。</li>
                            <li class="mt-1">したがって、<strong>サードパーティーアプリで復旧後のニコニコ実況に対応するには、必然的に NDGR 新コメントサーバーへの対応が必要になります。</strong>しかし、技術的には全くの別物で改修コストも高く、簡単に移行できるようなものではありません。<br>
                            一部のニコ生/ニコ実対応サードパーティアプリ開発者には、ニコニコ運営から NDGR 新コメントサーバー移行のための情報提供が行われています。しかし突然の変更だったため、対応が追いついていなかったり、技術的難易度の高さから対応が進んでいない状況です。</li>
                            <li class="mt-1"><strong><u>NX-Jikkyo では、niwavided 旧コメントサーバーの WebSocket API にしか対応できていない (NDGR 新コメントサーバーへの対応が難しい) NX-Jikkyo 対応サードパーティーアプリ向けに、ニコニコ実況の復旧後もサービスを継続しています。</u></strong><br>
                            NX-Jikkyo は、niwavided 旧コメントサーバーの WebSocket API と互換性があります。<br>
                            ニコ生統合後の新ニコニコ実況対応クライアントであれば、ニコ生視聴ページに埋め込まれている JSON (embedded-data) 内の <code>site.relive.webSocketUrl</code> から取得していた接続先 WebSocket の URL を <code>wss://nx-jikkyo.tsukumijima.net/api/v1/channels/(jk1,jk9,jk141, etc.)/ws/watch</code> に差し替えるだけで、NX-Jikkyo に対応できるはずです。</li>
                            <li class="mt-1">ニコニコ生放送で現在運用されている新コメントサーバーからのコメント取得処理は <a class="link" href="https://github.com/tsukumijima/NDGRClient" target="_blank">NDGRClient</a> としてライブラリ化しています (README に新コメントサーバーの技術詳細も載せています) 。コマンドラインツールも用意していますので、興味があればぜひお試しください。</li>
                        </ul>
                    </li>
                </ul>
                <h2 class="mt-5">動作環境</h2>
                <div class="mt-3">
                    <strong>PC: Google Chrome</strong><br>
                    <ul class="pl-5 mt-3 text-text-darken-1">
                        <li>Firefox でも動作するはずですが、コメント描画が重めなことが確認されています。<br>
                            動作確認も基本行っておらず、積極的なサポートはしていません。Chrome を使うことをおすすめします。</li>
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
                    2024/06/10 (Last Update: 2024/08/19)<br>
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

import { onMounted } from 'vue';
import { useRoute } from 'vue-router';

import HeaderBar from '@/components/HeaderBar.vue';
import Navigation from '@/components/Navigation.vue';
import Utils from '@/utils';


const route = useRoute();

onMounted(async () => {
    // URLのハッシュを取得
    const hash = route.hash;
    if (hash) {
        // ハッシュに対応する要素を取得
        const element = document.querySelector(hash);
        console.log(element);
        if (element) {
            // 要素が見つかった場合、その要素までスクロール
            await Utils.sleep(0.1);
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }
});


</script>
