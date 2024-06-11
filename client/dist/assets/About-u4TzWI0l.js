import{H as a,N as e}from"./Navigation-D4dokYb9.js";import{d,o as s,c as o,a as t,b as r,l,_ as n}from"./index-BqaE-WNP.js";import"./ssrBoot-j-PIDGq_.js";const c={class:"route-container"},k=l('<div class="px-5 py-8" style="width:100%;max-width:800px;margin:0 auto;line-height:1.65;" data-v-f266d866><h1 data-v-f266d866>NX-Jikkyo とは</h1><p class="mt-4 text-text-darken-1" data-v-f266d866><strong data-v-f266d866>NX-Jikkyo は、<a class="link" href="https://blog.nicovideo.jp/niconews/225099.html" target="_blank" data-v-f266d866>サイバー攻撃で期間未定の鯖落ち中</a> のニコニコ実況に代わる、ニコニコ実況民のための避難所であり、<a class="link" href="https://github.com/tsukumijima/NX-Jikkyo/blob/master/server/app/routers/comments.py" target="_blank" data-v-f266d866>ニコニコ生放送互換の WebSocket API</a> を備えるコメントサーバーです。</strong><br data-v-f266d866></p><hr class="mt-5" data-v-f266d866><p class="mt-5 text-text-darken-1" data-v-f266d866> 個人的にもニコニコ実況がすぐに復活してくれればそれが一番良いのですが、この感じだと残念ながら数週間はサーバーダウンが続きそうに思えます。<br data-v-f266d866> 2020年12月までのニコニコ実況は独立していたのですが、<a class="link" href="https://blog.nicovideo.jp/niconews/143148.html" target="_blank" data-v-f266d866>Adobe Flash 廃止に伴いニコ生のチャンネル生放送として統合されてしまいました。</a><br data-v-f266d866> よってニコ生本体が完全復旧しない限り、ニコニコ実況も当分復旧しそうにない状況です。 </p><p class="mt-2 text-text-darken-1" data-v-f266d866> ニコニコ実況が使えない時間が続けば続くほど、リアルタイムに実況できないのはもちろんのこと、録画でニコニコ実況の過去ログを見て作品を楽しむライフワークもできなくなってしまいます。<br data-v-f266d866> 3日程度ならともかく、数週間続く可能性を鑑みるとかなり受け入れ難いものです。 </p><hr class="mt-5" data-v-f266d866><p class="mt-5 text-text-darken-1" data-v-f266d866><strong data-v-f266d866>そこで突貫工事ではありますが、ニコニコ生放送互換のサードパーティーツールが比較的対応しやすい技術仕様で、ニコニコ実況が使えない間のつなぎとしてテレビを実況できる、このサイトを開発しました。</strong><br data-v-f266d866></p><blockquote class="mt-5 text-text-darken-1" data-v-f266d866><strong data-v-f266d866>ぜひこのサイトをまだ知らないニコニコ実況難民の方に広めていただけると嬉しいです！</strong><br data-v-f266d866> コメントサーバーの負荷問題は……なんとかします…！ </blockquote><blockquote class="mt-5 text-text-darken-1" data-v-f266d866> ソースコードは <a class="link" href="https://github.com/tsukumijima/NX-Jikkyo" target="_blank" data-v-f266d866>GitHub</a> で公開しています。<a class="link" href="/api/v1/docs" target="_blank" data-v-f266d866>API ドキュメント</a> もあります。<br data-v-f266d866> WebSocket API のドキュメントは <a class="link" href="https://github.com/tiangolo/fastapi" target="_blank" data-v-f266d866>FastAPI</a> が API ドキュメントを自動生成してくれないため現状ありませんが、ニコ生の WebSocket API のドロップイン代替として機能するはずです。<br data-v-f266d866></blockquote><blockquote class="mt-5 text-text-darken-1" data-v-f266d866> 勘の良い方はおそらくお気づきの通り、このサイトは私が長年開発している <a class="link" href="https://github.com/tsukumijima/KonomiTV" target="_blank" data-v-f266d866>KonomiTV</a> の大半のソースコードを流用して開発しています。<br data-v-f266d866> 一部 UI が不自然な箇所がありますが、元々 KonomiTV のプレイヤーロジックはそのまま動画再生処理だけを強引に無効化し、コメント再生だけを行わせているためです。 </blockquote><blockquote class="mt-5 text-text-darken-1" data-v-f266d866> ニコニコ実況の復活後のこのサイトの処遇はまだ決めていません。引き続き需要があれば、あるいはサーバー負荷の問題がなければ残す可能性も十分あります。 </blockquote><p class="mt-5 text-text-darken-1" data-v-f266d866> 投稿いただいたコメントは自動的にデータベースに記録されます。書き込んだ瞬間だけでなく、後からでも過去ログを見れるように考慮して設計しています。<br data-v-f266d866></p><p class="mt-2 text-text-darken-1" data-v-f266d866> またシステム簡素化のため、意図的にアカウント不要で書き込めるようにしています（データベースに個人情報が保存されることは絶対にありません）。<br data-v-f266d866> 気軽にお使いいただけますが、マナーを守ってのご利用をお願いします。 </p><hr class="mt-5" data-v-f266d866><p class="mt-5 text-text-darken-1" data-v-f266d866><strong data-v-f266d866>このサイトを公開した最大の理由は、十数年にも及ぶニコニコ実況の歴史上異常事態である、数週間に渡りテレビの過去ログコメントが完全に断たれる事態をなんとしてでも避けたいからです。</strong><br data-v-f266d866> もちろん15時間で突貫で作ったサイトなのでバグも多いでしょうし、大量のコメントの負荷には耐えきれないかもしれません。しかし、コメントが全く残らないよりはマシだと考えています。 </p><p class="mt-2 text-text-darken-1" data-v-f266d866> まだ手間的に間に合ってはいないのですが、<strong data-v-f266d866>少なくともニコニコ実況が復活するまでに書き込んでいただいた過去ログは、後日私 (tsukumi) が責任を持って <a class="link" href="https://jikkyo.tsukumijima.net" target="_blank" data-v-f266d866>ニコニコ実況 過去ログ API</a> で閲覧可能な過去ログとしてインポート・マージする予定です。</strong></p><blockquote class="mt-5 text-text-darken-1" data-v-f266d866> …ちなみに、NX-Jikkyo というサイト名は突貫開発をやる中でたまたま適当にひらめいた名前で、特に深い意味はありません。<br data-v-f266d866> もう少しかっこいい名前が出てくれば良かったのですが、「Jikkyo」と入れないと何のサービスか分かりづらそうというのもあり…。 </blockquote><p class="mt-5 text-text-darken-1 text-right" data-v-f266d866> 2024/06/10 (Last Update: 2024/06/11)<br data-v-f266d866><a class="link" href="https://blog.tsukumijima.net" target="_blank" data-v-f266d866>tsukumi</a> (<a class="link" href="https://twitter.com/TVRemotePlus" target="_blank" data-v-f266d866>Twitter@TVRemotePlus</a>) </p></div>',1),i=d({__name:"About",setup(f){return(v,m)=>(s(),o("div",c,[t(a),r("main",null,[t(e),k])]))}}),h=n(i,[["__scopeId","data-v-f266d866"]]);export{h as default};
