import{N as d,ca as C,U as g,Q as T,u as x}from"./index-DINBJEET.js";class j{static getChannelType(e){return e.length<=4?"GR":"BS"}static getChannelForceType(e){return e===null?"normal":e>=500?"festival":e>=200?"so-many":e>=100?"many":"normal"}static getChannelHashtag(e){const s={NHK総合:"#nhk",NHKEテレ:"#etv",HBC:"#hbc",札幌テレビ:"#stv",HTB:"#htv",TVh:"#tvh",北海道文化放送:"#uhb",RAB青森放送:"#rab",青森朝日放送:"#aba",ATV青森テレビ:"#atv",テレビ岩手:"#tvi",岩手朝日テレビ:"#iat",IBCテレビ:"#ibc",めんこいテレビ:"#mit",TBCテレビ:"#tbc",ミヤギテレビ:"#mmt",東日本放送:"#khb",仙台放送:"#oxtv",ABS秋田放送:"#abs",秋田朝日放送:"#aab",AKT秋田テレビ:"#akt",山形放送:"#ybc",山形テレビ:"#yts",TUY:"#tuy",さくらんぼテレビ:"#say",福島中央テレビ:"#fct",KFB福島放送:"#kfb",テレビユー福島:"#tuf",FTV福島テレビ:"#ftv",TeNY:"#TeNY",新潟テレビ21:"#uxtv",BSN:"#bsn",NST:"#nst",KNBテレビ:"#knb",チューリップテレビ:"#tut",富山テレビ放送:"#toyamatv",テレビ金沢:"#tv_kanazawa",HAB:"#hab",MRO:"#mro",石川テレビ:"#ishikawatv",福井放送:"#fbc",福井テレビ:"#fukuitv",山梨放送:"#ybs",UTYテレビ山梨:"#uty",テレビ信州:"#tsb",長野朝日放送:"#abn",SBC信越放送:"#sbc",長野放送:"#nbs","Daiichi-TV":"#sdt",静岡朝日テレビ:"#satv",SBS:"#sbs",テレビ静岡:"#sut",三重テレビ:"#mietv",ぎふチャン:"#gifuchan",BBCびわ湖放送:"#BBC_biwako",奈良テレビ:"#tvn",WTV:"#telewaka",RNC西日本テレビ:"#rnc",瀬戸内海放送:"#ksb",RSKテレビ:"#rsk",TSCテレビせとうち:"#tvsetouchi",OHK:"#ohk",RCCテレビ:"#rcc",広島テレビ:"#htv",広島ホームテレビ:"#hometv",テレビ新広島:"#tss",日本海テレビ:"#nkt",BSSテレビ:"#bss",さんいん中央テレビ:"#tsk",tysテレビ山口:"#tys",山口放送:"#kry",yab山口朝日:"#yab",四国放送:"#jrt",高知放送:"#rkc",テレビ高知:"#kutv",高知さんさんテレビ:"#kss",南海放送:"#rnb",愛媛朝日テレビ:"#eat",あいテレビ:"#itv",テレビ愛媛:"#ebc",KBCテレビ:"#kbc",RKB毎日放送:"#rkb",FBS福岡放送:"#fbs",TVQ九州放送:"#tvq",テレビ西日本:"#tnc",STSサガテレビ:"#sagatv",NBC長崎放送:"#nbc",長崎国際テレビ:"#nib",NCC長崎文化放送:"#ncc",テレビ長崎:"#ktn",RKK熊本放送:"#rkk",くまもと県民:"#kkt",KAB熊本朝日放送:"#kab",テレビ熊本:"#tku",OBS大分放送:"#obs",TOSテレビ大分:"#tos",OAB大分朝日放送:"#oab",MRT宮崎放送:"#mrt",テレビ宮崎:"#umk",MBC南日本放送:"#mbc",鹿児島讀賣テレビ:"#kyt",KKB鹿児島放送:"#kkb",鹿児島テレビ放送:"#kts",RBCテレビ:"#rbc",琉球朝日放送:"#qab",沖縄テレビ:"#otv",日テレ:"#ntv",読売テレビ:"#ytv",中京テレビ:"#chukyotv",テレビ朝日:"#tvasahi",ABCテレビ:"#abc","メ~テレ":"#nagoyatv","メ〜テレ":"#nagoyatv",TBSチャンネル:null,TBS:"#tbs",MBS:"#mbs",CBC:"#cbc",テレビ東京:"#tvtokyo",テレ東:"#tvtokyo",テレビ大阪:"#tvo",テレビ愛知:"#tva",フジテレビ:"#fujitv",関西テレビ:"#kantele",東海テレビ:"#tokaitv","TOKYO MX":"#tokyomx",tvk:"#tvk",チバテレ:"#chibatv",テレ玉:"#teletama",群馬テレビ:"#gtv",とちぎテレビ:"#tochitere",とちテレ:"#tochitere",サンテレビ:"#suntv",KBS京都:"#kbs",NHKBS1:"#nhkbs1",NHKBSプレミアム:"#nhkbsp",NHKBS:"#nhkbs",BS日テレ:"#bsntv",BS朝日:"#bsasahi","BS-TBS":"#bstbs",BSテレ東:"#bstvtokyo",BSフジ:"#bsfuji",BS11:"#bs11",BS12:"#bs12",BS松竹東急:"#bs260ch",BSJapanext:"#bsjapanext",BSよしもと:"#bsyoshimoto","AT-X":"#at_x"},n=Object.keys(s).find(o=>e.startsWith(o));return n?s[n]:null}}const k={id:"jk0",channel_id:"jk0",network_id:0,service_id:0,event_id:0,title:"取得中…",description:"取得中…",detail:{},start_time:"2000-01-01T00:00:00+09:00",end_time:"2000-01-01T00:00:00+09:00",duration:0,is_free:!0,genres:[],video_type:"映像1080i(1125i)、アスペクト比16:9 パンベクトルなし",video_codec:"MPEG-2",video_resolution:"1080i",primary_audio_type:"2/0モード(ステレオ)",primary_audio_language:"日本語",primary_audio_sampling_rate:"48kHz",secondary_audio_type:null,secondary_audio_language:null,secondary_audio_sampling_rate:null},m={id:"jk0",display_channel_id:"gr000",network_id:0,service_id:0,transport_stream_id:null,remocon_id:0,channel_number:"---",type:"GR",name:"取得中…",jikkyo_force:null,is_subchannel:!1,is_radiochannel:!1,is_watchable:!0,is_display:!0,viewer_count:0,program_present:k,program_following:k};class A{static async fetchAll(){const e=await d.get("/channels");if(e.type==="error")return d.showGenericError(e,"チャンネル情報を取得できませんでした。"),null;const s={GR:[],BS:[],CS:[],CATV:[],SKY:[],STARDIGIO:[]},n=new Date;return e.data.filter(t=>t.threads.some(a=>new Date(a.start_at)<=n&&n<=new Date(a.end_at))).forEach(t=>{var c,u,l,f,y,b,v,w,S,B;const a=t.threads.find(h=>new Date(h.start_at)<=n&&n<=new Date(h.end_at)),_=t.threads.findIndex(h=>new Date(h.start_at)<=n&&n<=new Date(h.end_at)),i=_!==-1&&_+1<t.threads.length?t.threads[_+1]:null,p={id:t.id,display_channel_id:t.id,network_id:-1,service_id:-1,transport_stream_id:-1,remocon_id:(()=>{if(t.id.length<=4)return parseInt(t.id.replaceAll("jk",""));switch(t.id){case"jk101":return 1;case"jk141":return 4;case"jk151":return 5;case"jk161":return 6;case"jk171":return 7;case"jk181":return 8;case"jk191":return 9;case"jk211":return 11;case"jk222":return 12;default:return-1}})(),channel_number:t.id.length<=4?("00"+t.id.replaceAll("jk","")).slice(-2)+"1":t.id.replaceAll("jk",""),type:t.id.length<=4?"GR":"BS",name:t.name,jikkyo_force:a?a.jikkyo_force:null,is_display:!0,is_subchannel:!1,is_radiochannel:!1,is_watchable:!0,viewer_count:a?a.comments:0,program_present:a?{id:a.id.toString(),channel_id:t.id,network_id:-1,service_id:-1,event_id:-1,title:((c=t.program_present)==null?void 0:c.title)||a.title,description:`<div class="font-weight-bold">🎧実況枠: ${a.title}</div>`,detail:{"NX-Jikkyo について":`NX-Jikkyo は、放送中のテレビ番組や起きているイベントに対して、みんなでコメントをし盛り上がりを共有する、リアルタイムコミュニケーションサービスです。
ニコニコ実況に投稿されたコメントも、リアルタイムで表示されます。

ひとりだけど、ひとりじゃない。
テレビの映像は流れませんが、好きな番組をテレビで見ながら、プレイヤーに流れるコメントでワイワイ楽しめます。
ぜひ感想などを気軽にコメントしてお楽しみください。`},start_time:((u=t.program_present)==null?void 0:u.start_at)||a.start_at,end_time:((l=t.program_present)==null?void 0:l.end_at)||a.end_at,duration:((f=t.program_present)==null?void 0:f.duration)||a.duration,is_free:!1,genres:(y=t.program_present)!=null&&y.genre?[{major:t.program_present.genre,middle:""}]:[],video_type:"",video_codec:"",video_resolution:"",primary_audio_type:"",primary_audio_language:"",primary_audio_sampling_rate:"",secondary_audio_type:null,secondary_audio_language:null,secondary_audio_sampling_rate:null}:null,program_following:i?{id:i.id.toString(),channel_id:t.id,network_id:-1,service_id:-1,event_id:-1,title:((b=t.program_following)==null?void 0:b.title)||i.title,description:i.description,detail:{},start_time:((v=t.program_following)==null?void 0:v.start_at)||i.start_at,end_time:((w=t.program_following)==null?void 0:w.end_at)||i.end_at,duration:((S=t.program_following)==null?void 0:S.duration)||i.duration,is_free:!1,genres:(B=t.program_following)!=null&&B.genre?[{major:t.program_following.genre,middle:""}]:[],video_type:"",video_codec:"",video_resolution:"",primary_audio_type:"",primary_audio_language:"",primary_audio_sampling_rate:"",secondary_audio_type:null,secondary_audio_language:null,secondary_audio_sampling_rate:null}:null};t.id.length<=4?s.GR.push(p):s.BS.push(p)}),s}static async fetch(e){const s=await d.get(`/channels/${e}`);return s.type==="error"?(d.showGenericError(s,"チャンネル情報を取得できませんでした。"),null):s.data}static async fetchWebSocketInfo(e){if(!C("NX-Niconico-User"))return{watch_session_url:`${g.api_base_url.replaceAll("http","ws")}/channels/${e}/ws/watch`,nicolive_watch_session_url:null,nicolive_watch_session_error:null,comment_session_url:`${g.api_base_url.replaceAll("http","ws")}/channels/${e}/ws/comment`,is_nxjikkyo_exclusive:!1};const n=await d.get(`/channels/${e}/jikkyo`);return n.type==="error"?(d.showGenericError(n,"コメント送受信用 WebSocket API の情報を取得できませんでした。"),null):n.data}}const K=T("channels",{state:()=>({channels_list:{GR:[],BS:[],CS:[],CATV:[],SKY:[],STARDIGIO:[]},is_channels_list_initial_updated:!1,last_updated_at:0,display_channel_id:"gr000",viewer_count:null,current_program_present:null,current_program_following:null}),getters:{channel(){if(this.is_channels_list_initial_updated===!1)return{previous:m,current:m,next:m};const r={...k,title:"チャンネル情報取得エラー",description:"このチャンネル ID のチャンネル情報は存在しません。"},e={...m,name:"チャンネル情報取得エラー",program_present:r,program_following:r},s=j.getChannelType(this.display_channel_id);if(s===null)return{previous:e,current:e,next:e};const n=this.channels_list[s],o=n.findIndex(i=>i.display_channel_id===this.display_channel_id);if(o===-1)return{previous:e,current:e,next:e};const t=(()=>{let i=o-1;for(;n.length;){if(i<=-1&&(i=n.length-1),n[i].is_display)return i;i--}return 0})(),a=(()=>{let i=o+1;for(;n.length;){if(i>=n.length&&(i=0),n[i].is_display)return i;i++}return 0})(),_=structuredClone(n[o]);return this.current_program_present!==null&&(_.program_present=this.current_program_present),this.current_program_following!==null&&(_.program_following=this.current_program_following),this.viewer_count!==null&&(_.viewer_count=this.viewer_count),{previous:n[t],current:_,next:n[a]}},channels_list_with_pinned(){var n,o,t,a,_,i,p;const r=x(),e=new Map;if(e.set("ピン留め",[]),e.set("地デジ",[]),this.is_channels_list_initial_updated===!1)return e;e.set("BS",[]),e.set("CS",[]),e.set("CATV",[]),e.set("SKY",[]),e.set("StarDigio",[]);const s=[];for(const[c,u]of Object.entries(this.channels_list))for(const l of u)if(r.settings.pinned_channel_ids.includes(l.id)&&s.push(l),l.is_display!==!1)switch(l.type){case"GR":{(n=e.get("地デジ"))==null||n.push(l);break}case"BS":{(o=e.get("BS"))==null||o.push(l);break}case"CS":{(t=e.get("CS"))==null||t.push(l);break}case"CATV":{(a=e.get("CATV"))==null||a.push(l);break}case"SKY":{(_=e.get("SKY"))==null||_.push(l);break}case"STARDIGIO":{(i=e.get("StarDigio"))==null||i.push(l);break}}(p=e.get("ピン留め"))==null||p.push(...s.sort((c,u)=>{const l=r.settings.pinned_channel_ids.indexOf(c.id),f=r.settings.pinned_channel_ids.indexOf(u.id);return l-f}));for(const[c,u]of e)c!=="ピン留め"&&u.length===0&&e.delete(c);return e.size===1&&e.has("ピン留め")&&e.delete("ピン留め"),e},channels_list_with_pinned_for_watch(){var e;const r=new Map([...this.channels_list_with_pinned]);return this.is_channels_list_initial_updated===!1||((e=r.get("ピン留め"))==null?void 0:e.length)===0&&r.delete("ピン留め"),r}},actions:{getChannelByRemoconID(r,e){return this.channels_list[r].find(o=>o.remocon_id===e)??null},async update(r=!1){const e=async()=>{const s=await A.fetchAll();s!==null&&(this.channels_list=g.deepObjectFreeze(s),this.is_channels_list_initial_updated===!1&&(this.is_channels_list_initial_updated=!0),this.last_updated_at=g.time())};if(this.is_channels_list_initial_updated===!0&&r===!1){g.time()-this.last_updated_at>60&&e();return}await e()}}}),R=K;export{j as C,m as I,A as a,R as u};
