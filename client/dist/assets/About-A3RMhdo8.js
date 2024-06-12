import{H as t,N as e}from"./Navigation-CLz4UYIz.js";import{d,o as s,c as o,a,b as r,l,_ as k}from"./index-5d4hat96.js";import"./ssrBoot-CrDY9QHc.js";const n={class:"route-container"},i=l('<div class="px-5 py-8" style="width:100%;max-width:850px;margin:0 auto;line-height:1.65;" data-v-95a899d4><h1 data-v-95a899d4>NX-Jikkyo とは</h1><p class="mt-4 text-text-darken-1" data-v-95a899d4><strong data-v-95a899d4>NX-Jikkyo は、<a class="link" href="https://blog.nicovideo.jp/niconews/225099.html" target="_blank" data-v-95a899d4>サイバー攻撃で期間未定の鯖落ち中</a> のニコニコ実況に代わる、ニコニコ実況民のための避難所であり、<a class="link" href="https://github.com/tsukumijima/NX-Jikkyo/blob/master/server/app/routers/comments.py" target="_blank" data-v-95a899d4>ニコニコ生放送互換の WebSocket API</a> を備えるコメントサーバーです。</strong><br data-v-95a899d4></p><blockquote class="mt-5 text-text-darken-1" data-v-95a899d4><strong data-v-95a899d4><a class="link" href="https://twitter.com/TVRemotePlus" target="_blank" data-v-95a899d4>Twitter@TVRemotePlus</a> やハッシュタグ <a class="link" href="https://x.com/search?q=%23NXJikkyo&amp;src=typed_query" target="_blank" data-v-95a899d4>#NXJikkyo</a> では NX-Jikkyo の最新情報を発信しています！<br data-v-95a899d4>ぜひチェックしてみてください🙏</strong></blockquote><blockquote class="mt-5 text-text-darken-1" data-v-95a899d4><strong data-v-95a899d4><a class="link" href="https://github.com/tsukumijima/KonomiTV/releases/tag/v0.10.1" target="_blank" data-v-95a899d4>KonomiTV 0.10.1</a> にて、ニコニコ実況の代わりに NX-Jikkyo からリアルタイムに実況コメントを取得する設定が追加されました！<br data-v-95a899d4></strong><a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank" data-v-95a899d4>KonomiTV</a> + ニコニコ実況ユーザーの方はサーバー設定から NX-Jikkyo を有効にすると再び実況コメントを表示できるようになるのでアプデ推奨です🙏<br data-v-95a899d4></blockquote><h2 class="mt-5" data-v-95a899d4>開発経緯</h2><p class="mt-3 text-text-darken-1" data-v-95a899d4> 個人的にもニコニコ実況がすぐに復活してくれればそれが一番良いのですが、この感じだと残念ながら数週間はサーバーダウンが続きそうに思えます。<br data-v-95a899d4> 2020年12月までのニコニコ実況は独立していたのですが、<a class="link" href="https://blog.nicovideo.jp/niconews/143148.html" target="_blank" data-v-95a899d4>Adobe Flash 廃止に伴いニコ生のチャンネル生放送として統合されてしまいました。</a><br data-v-95a899d4> よってニコ生本体が完全復旧しない限り、ニコニコ実況も当分復旧しそうにない状況です。 </p><p class="mt-2 text-text-darken-1" data-v-95a899d4> ニコニコ実況が使えない時間が続けば続くほど、リアルタイムに実況できないのはもちろんのこと、録画でニコニコ実況の過去ログを見て作品を楽しむライフワークもできなくなってしまいます。<br data-v-95a899d4> 3日程度ならともかく、数週間続く可能性を鑑みるとかなり受け入れ難いものです。 </p><p class="mt-5 text-text-darken-1" data-v-95a899d4><strong data-v-95a899d4>そこで突貫工事ではありますが、ニコニコ生放送互換のサードパーティーツールが比較的対応しやすい技術仕様で、ニコニコ実況が使えない間のつなぎとしてテレビを実況できる、このサイトを開発しました。</strong><br data-v-95a899d4></p><blockquote class="mt-5 text-text-darken-1" data-v-95a899d4><strong data-v-95a899d4>ぜひこのサイトをまだ NX-Jikkyo を知らないニコニコ実況難民の方に広めていただけると嬉しいです！</strong><br data-v-95a899d4> コメントサーバーの負荷問題は……なんとかします…！現時点での最大瞬間ユーザー数の数倍程度なら今のサーバーでも捌けそうな状況です。<br data-v-95a899d4></blockquote><blockquote class="mt-5 text-text-darken-1" data-v-95a899d4><strong data-v-95a899d4>NX-Jikkyo を「<a class="link" href="https://support.google.com/chrome/answer/9658361" target="_blank" data-v-95a899d4>ホーム画面に追加</a>」することで、PC のデスクトップやスマホのホーム画面から普通のアプリのように起動できます！特にスマホで実況している方におすすめです。</strong></blockquote><blockquote class="mt-5 text-text-darken-1" data-v-95a899d4> ソースコードは <a class="link" href="https://github.com/tsukumijima/NX-Jikkyo" target="_blank" data-v-95a899d4>GitHub</a> で公開しています。<a class="link" href="/api/v1/docs" target="_blank" data-v-95a899d4>API ドキュメント</a> もあります。<br data-v-95a899d4> WebSocket API のドキュメントは <a class="link" href="https://github.com/tiangolo/fastapi" target="_blank" data-v-95a899d4>FastAPI</a> が API ドキュメントを自動生成してくれないため現状ありませんが、ニコ生の WebSocket API のドロップイン代替として機能するはずです。<br data-v-95a899d4><div class="mt-1" data-v-95a899d4></div> 勘の良い方はおそらくお気づきの通り、このサイトは私が長年開発している <a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank" data-v-95a899d4>KonomiTV</a> の大半のソースコードを流用して開発しています。<br data-v-95a899d4> 一部 UI が不自然な箇所がありますが、元々 KonomiTV のプレイヤーロジックはそのまま動画再生処理だけを強引に無効化し、コメント再生だけを行わせているためです。 </blockquote><h2 class="mt-5" data-v-95a899d4>運用方針</h2><p class="mt-3 text-text-darken-1" data-v-95a899d4> 投稿いただいたコメントは自動的にデータベースに記録されます。書き込んだ瞬間だけでなく、後からでも過去ログを見れるように考慮して設計しています。<br data-v-95a899d4></p><p class="mt-2 text-text-darken-1" data-v-95a899d4> またシステム簡素化のため、意図的にアカウント不要で書き込めるようにしています（データベースに個人情報が保存されることは絶対にありません）。<br data-v-95a899d4> 気軽にお使いいただけますが、マナーを守ってのご利用をお願いします。 </p><blockquote class="mt-5 text-text-darken-1" data-v-95a899d4> ニコニコ実況の復活後のこのサイトの処遇は未定です。ニコニコ実況復活後も引き続き需要があれば、あるいはサーバー負荷的に大丈夫そうなら、継続する可能性も十分あります。 </blockquote><hr class="mt-5" data-v-95a899d4><p class="mt-5 text-text-darken-1" data-v-95a899d4><strong data-v-95a899d4>このサイトを公開した最大の理由は、十数年にも及ぶニコニコ実況の歴史上異常事態である、数週間に渡りテレビの過去ログコメントが完全に断たれる事態をなんとしてでも避けたいからです。</strong><br data-v-95a899d4> もちろん15時間で突貫で作ったサイトなのでバグも多いでしょうし、大量のコメントの負荷には耐えきれないかもしれません。しかし、コメントが全く残らないよりはマシだと考えています。 </p><p class="mt-2 text-text-darken-1" data-v-95a899d4> まだ手間的に間に合ってはいないのですが、<strong data-v-95a899d4>少なくともニコニコ実況が復活するまでに書き込んでいただいた過去ログは、後日私 (tsukumi) が責任を持って <a class="link" href="https://jikkyo.tsukumijima.net" target="_blank" data-v-95a899d4>ニコニコ実況 過去ログ API</a> で閲覧可能な過去ログとしてインポート・マージする予定です。ご安心ください！</strong></p><blockquote class="mt-5 text-text-darken-1" data-v-95a899d4> …ちなみに、NX-Jikkyo というサイト名は突貫開発をやる中でたまたま適当にひらめいた名前で、特に深い意味はありません。<br data-v-95a899d4> もう少しかっこいい名前が出てくれば良かったのですが、「Jikkyo」と入れないと何のサービスか分かりづらそうというのもあり…。 </blockquote><p class="mt-5 text-text-darken-1 text-right" data-v-95a899d4> 2024/06/10 (Last Update: 2024/06/11)<br data-v-95a899d4><a class="link" href="https://blog.tsukumijima.net" target="_blank" data-v-95a899d4>tsukumi</a> (<a class="link" href="https://twitter.com/TVRemotePlus" target="_blank" data-v-95a899d4>Twitter@TVRemotePlus</a>) </p></div>',1),c=d({__name:"About",setup(m){return(v,b)=>(s(),o("div",n,[a(t),r("main",null,[a(e),i])]))}}),g=k(c,[["__scopeId","data-v-95a899d4"]]);export{g as default};
