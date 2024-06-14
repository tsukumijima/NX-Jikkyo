import{H as t,N as e}from"./Navigation-D786-yQw.js";import{d as s,o as f,c as o,a,b as r,i as l,_ as k}from"./index-CXtg-imp.js";import"./ssrBoot-CPVzlbDG.js";const i={class:"route-container"},n=l('<div class="px-5 py-8" style="width:100%;max-width:850px;margin:0 auto;line-height:1.65;" data-v-f6f085a6><h1 data-v-f6f085a6>NX-Jikkyo とは</h1><p class="mt-4 text-text-darken-1" data-v-f6f085a6><strong data-v-f6f085a6>NX-Jikkyo は、<a class="link" href="https://blog.nicovideo.jp/niconews/225099.html" target="_blank" data-v-f6f085a6>サイバー攻撃で期間未定の鯖落ち中</a> のニコニコ実況に代わる、ニコニコ実況民のための避難所であり、<a class="link" href="https://github.com/tsukumijima/NX-Jikkyo/blob/master/server/app/routers/websocket.py" target="_blank" data-v-f6f085a6>ニコニコ生放送互換の WebSocket API</a> を備えるコメントサーバーです。</strong><br data-v-f6f085a6></p><blockquote class="mt-5 text-text-darken-1" data-v-f6f085a6><strong data-v-f6f085a6><a class="link" href="https://twitter.com/TVRemotePlus" target="_blank" data-v-f6f085a6>Twitter@TVRemotePlus</a> やハッシュタグ <a class="link" href="https://x.com/search?q=%23NXJikkyo&amp;src=typed_query" target="_blank" data-v-f6f085a6>#NXJikkyo</a> では NX-Jikkyo の最新情報を発信しています！<br data-v-f6f085a6>ぜひチェックしてみてください🙏</strong></blockquote><blockquote class="mt-5 text-text-darken-1" data-v-f6f085a6><strong data-v-f6f085a6><a class="link" href="https://github.com/tsukumijima/KonomiTV/releases/tag/v0.10.1" target="_blank" data-v-f6f085a6>KonomiTV 0.10.1</a> にて、ニコニコ実況の代わりに NX-Jikkyo からリアルタイムに実況コメントを取得する設定が追加されました！<br data-v-f6f085a6></strong><a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank" data-v-f6f085a6>KonomiTV</a> + ニコニコ実況ユーザーの方はサーバー設定から NX-Jikkyo を有効にすると再び実況コメントを表示できるようになるのでアプデ推奨です🙏<br data-v-f6f085a6></blockquote><blockquote class="mt-5 text-text-darken-1" data-v-f6f085a6><strong data-v-f6f085a6><a class="link" href="https://github.com/DBCTRADO/TVTest" target="_blank" data-v-f6f085a6>TVTest</a> のニコニコ実況表示プラグイン <a class="link" href="https://github.com/xtne6f/NicoJK/releases/tag/master-240613" target="_blank" data-v-f6f085a6>NicoJK master-240613</a> にて、ニコニコ実況の代わりに NX-Jikkyo からリアルタイムに実況コメントを取得する設定が追加されました！<br data-v-f6f085a6></strong><a class="link" href="https://github.com/DBCTRADO/TVTest" target="_blank" data-v-f6f085a6>TVTest</a> + ニコニコ実況ユーザーの方は NicoJK.ini を編集して NX-Jikkyo を有効にすると再び実況コメントを表示できるようになるのでアプデ推奨です🙏<br data-v-f6f085a6> NicoJK の更新方法の詳細は <a class="link" href="https://blog.tsukumijima.net/article/nx-jikkyo-released/" target="_blank" data-v-f6f085a6>こちら</a> に記載しています。 </blockquote><h2 class="mt-5" data-v-f6f085a6>開発経緯</h2><p class="mt-3 text-text-darken-1" data-v-f6f085a6> 個人的にもニコニコ実況がすぐに復活してくれればそれが一番良いのですが、この感じだと残念ながら数週間はサーバーダウンが続きそうに思えます。<br data-v-f6f085a6> 2020年12月までのニコニコ実況は独立していたのですが、<a class="link" href="https://blog.nicovideo.jp/niconews/143148.html" target="_blank" data-v-f6f085a6>Adobe Flash 廃止に伴いニコ生のチャンネル生放送として統合されてしまいました。</a><br data-v-f6f085a6> よってニコ生本体が完全復旧しない限り、ニコニコ実況も当分復旧しそうにない状況です。 </p><p class="mt-2 text-text-darken-1" data-v-f6f085a6> ニコニコ実況が使えない時間が続けば続くほど、リアルタイムに実況できないのはもちろんのこと、録画でニコニコ実況の過去ログを見て作品を楽しむライフワークもできなくなってしまいます。<br data-v-f6f085a6> 3日程度ならともかく、数週間続く可能性を鑑みるとかなり受け入れ難いものです。 </p><p class="mt-5 text-text-darken-1" data-v-f6f085a6><strong data-v-f6f085a6>そこで突貫工事ではありますが、ニコニコ生放送互換のサードパーティーツールが比較的対応しやすい技術仕様で、ニコニコ実況が使えない間のつなぎとしてテレビを実況できる、このサイトを開発しました。</strong><br data-v-f6f085a6></p><blockquote class="mt-5 text-text-darken-1" data-v-f6f085a6><strong data-v-f6f085a6>ぜひこのサイトをまだ NX-Jikkyo を知らないニコニコ実況難民の方に広めていただけると嬉しいです！</strong><br data-v-f6f085a6> コメントサーバーの負荷問題は……なんとかします…！現時点での最大瞬間ユーザー数の数倍程度なら今のサーバーでも捌けそうな状況です。<br data-v-f6f085a6></blockquote><blockquote class="mt-5 text-text-darken-1" data-v-f6f085a6><strong data-v-f6f085a6>NX-Jikkyo を「<a class="link" href="https://support.google.com/chrome/answer/9658361" target="_blank" data-v-f6f085a6>ホーム画面に追加</a>」することで、PC のデスクトップやスマホのホーム画面から普通のアプリのように起動できます！特にスマホで実況している方におすすめです。</strong></blockquote><blockquote class="mt-5 text-text-darken-1" data-v-f6f085a6> ソースコードは <a class="link" href="https://github.com/tsukumijima/NX-Jikkyo" target="_blank" data-v-f6f085a6>GitHub</a> で公開しています。<a class="link" href="/api/v1/docs" target="_blank" data-v-f6f085a6>API ドキュメント</a> もあります。<br data-v-f6f085a6> WebSocket API のドキュメントは <a class="link" href="https://github.com/tiangolo/fastapi" target="_blank" data-v-f6f085a6>FastAPI</a> が API ドキュメントを自動生成してくれないため現状ありませんが、ニコ生の WebSocket API のドロップイン代替として機能するはずです。<br data-v-f6f085a6><div class="mt-1" data-v-f6f085a6></div> 勘の良い方はおそらくお気づきの通り、このサイトは私が長年開発している <a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank" data-v-f6f085a6>KonomiTV</a> の大半のソースコードを流用して開発しています。<br data-v-f6f085a6> 一部 UI が不自然な箇所がありますが、元々 KonomiTV のプレイヤーロジックはそのまま動画再生処理だけを強引に無効化し、コメント再生だけを行わせているためです。 </blockquote><h2 class="mt-5" data-v-f6f085a6>運用方針</h2><p class="mt-3 text-text-darken-1" data-v-f6f085a6> 投稿いただいたコメントは自動的にデータベースに記録されます。書き込んだ瞬間だけでなく、後からでも過去ログを見れるように考慮して設計しています。<br data-v-f6f085a6></p><p class="mt-2 text-text-darken-1" data-v-f6f085a6> またシステム簡素化のため、意図的にアカウント不要で書き込めるようにしています（データベースに個人情報が保存されることは絶対にありません）。<br data-v-f6f085a6> 気軽にお使いいただけますが、マナーを守ってのご利用をお願いします。 </p><blockquote class="mt-5 text-text-darken-1" data-v-f6f085a6> ニコニコ実況の復活後のこのサイトの処遇は未定です。ニコニコ実況復活後も引き続き需要があれば、あるいはサーバー負荷的に大丈夫そうなら、継続する可能性も十分あります。 </blockquote><hr class="mt-5" data-v-f6f085a6><p class="mt-5 text-text-darken-1" data-v-f6f085a6><strong data-v-f6f085a6>このサイトを公開した最大の理由は、十数年にも及ぶニコニコ実況の歴史上異常事態である、数週間に渡りテレビの過去ログコメントが完全に断たれる事態をなんとしてでも避けたいからです。</strong><br data-v-f6f085a6> もちろん元々15時間で突貫で作ったサイトなのでバグも多いでしょうし、大量のコメントの負荷には耐えきれないかもしれません（随時改善中です）。しかし、コメントが全く残らないよりはマシだと考えています。 </p><p class="mt-2 text-text-darken-1" data-v-f6f085a6> まだ手間的に間に合ってはいないのですが、<strong data-v-f6f085a6>少なくともニコニコ実況が復活するまでに書き込んでいただいた過去ログは、後日私 (tsukumi) が責任を持って <a class="link" href="https://jikkyo.tsukumijima.net" target="_blank" data-v-f6f085a6>ニコニコ実況 過去ログ API</a> で閲覧可能な過去ログとしてインポート・マージする予定です。ご安心ください！</strong></p><blockquote class="mt-5 text-text-darken-1" data-v-f6f085a6> …ちなみに、NX-Jikkyo というサイト名は突貫開発をやる中でたまたま適当にひらめいた名前で、特に深い意味はありません。<br data-v-f6f085a6> もう少しかっこいい名前が出てくれば良かったのですが、「Jikkyo」と入れないと何のサービスか分かりづらそうというのもあり…。 </blockquote><p class="mt-5 text-text-darken-1 text-right" data-v-f6f085a6> 2024/06/10 (Last Update: 2024/06/14)<br data-v-f6f085a6><a class="link" href="https://blog.tsukumijima.net" target="_blank" data-v-f6f085a6>tsukumi</a> (<a class="link" href="https://twitter.com/TVRemotePlus" target="_blank" data-v-f6f085a6>Twitter@TVRemotePlus</a>) </p></div>',1),d=s({__name:"About",setup(c){return(v,m)=>(f(),o("div",i,[a(t),r("main",null,[a(e),n])]))}}),u=k(d,[["__scopeId","data-v-f6f085a6"]]);export{u as default};
