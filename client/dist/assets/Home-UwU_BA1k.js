import{d as U,U as F,P as H,m as $,M as B,u as M,_ as N,r as c,a as I,o as u,c as r,b as _,e as t,n as p,f as E,F as g,g as v,w as C,v as z,h as m,i as k,j as D,k as w,l as o,t as l,V as L,p as S,R as A,q as J,s as R}from"./index-C8X01GMO.js";import{S as X,a as q}from"./swiper-DvZLaToz.js";import{H as K,N as O}from"./Navigation-C5dy3zOE.js";import{C as Z,u as G}from"./ChannelsStore-DnMRQkmC.js";import{V as W}from"./ssrBoot-DwA1YKw2.js";const Q=U({name:"TV-Home",components:{HeaderBar:K,Navigation:O,Swiper:X,SwiperSlide:q},data(){return{Utils:Object.freeze(F),ChannelUtils:Object.freeze(Z),ProgramUtils:Object.freeze(H),active_tab_index:0,swiper_instance:null,scroll_abort_controller:new AbortController,is_loading:!0,interval_ids:[]}},computed:{...$(G,M)},watch:{active_tab_index(){var e,n;(e=this.swiper_instance)==null||e.updateAutoHeight(),(n=this.swiper_instance)==null||n.slideTo(this.active_tab_index,this.is_loading===!0?0:void 0)}},async mounted(){var n,h;this.settingsStore.settings.pinned_channel_ids.length===0&&(this.active_tab_index=1);const e=60-new Date().getSeconds();this.interval_ids.push(window.setTimeout(()=>{this.channelsStore.update(!0),this.interval_ids.push(window.setInterval(()=>this.channelsStore.update(!0),30*1e3))},e*1e3)),await this.channelsStore.update(),((n=this.channelsStore.channels_list_with_pinned.get("ピン留め"))==null?void 0:n.length)===0&&(this.active_tab_index=1),(h=this.swiper_instance)==null||h.updateAutoHeight(),window.addEventListener("scroll",()=>{var f;(f=this.swiper_instance)==null||f.updateAutoHeight()},{passive:!0,signal:this.scroll_abort_controller.signal}),await F.sleep(.01),this.is_loading=!1},beforeUnmount(){for(const e of this.interval_ids)window.clearInterval(e);this.scroll_abort_controller.abort(),this.scroll_abort_controller=new AbortController},methods:{addPinnedChannel(e){this.settingsStore.settings.pinned_channel_ids=[...this.settingsStore.settings.pinned_channel_ids,e.id],B.show(`${e.name}をピン留めしました。`)},removePinnedChannel(e){var n;this.settingsStore.settings.pinned_channel_ids=this.settingsStore.settings.pinned_channel_ids.filter(h=>h!==e.id),((n=this.channelsStore.channels_list_with_pinned.get("ピン留め"))==null?void 0:n.length)===0&&(this.active_tab_index=1),B.show(`${e.name}のピン留めを外しました。`)},isPinnedChannel(e){return this.settingsStore.settings.pinned_channel_ids.includes(e.id)}}}),a=e=>(J("data-v-fc65ddfe"),e=e(),R(),e),Y={class:"route-container"},ee=D('<div class="mt-5 mb-2 mx-4 text-center font-weight-bold" style="font-size:15px;" data-v-fc65ddfe><div data-v-fc65ddfe>ぜひこのサイトをまだ NX-Jikkyo を知らないニコニコ実況難民の方に広めていただけると嬉しいです！</div><div class="mt-1" data-v-fc65ddfe><a class="link" href="https://air.fem.jp/jkcommentviewer/" target="_blank" data-v-fc65ddfe>jkcommentviewer</a> / <a class="link" href="https://blog.tsukumijima.net/article/nx-jikkyo-released/#toc4" target="_blank" data-v-fc65ddfe>TVTest (NicoJK)</a> / <a class="link" href="https://github.com/tsukumijima/KonomiTV/releases/tag/v0.10.1" target="_blank" data-v-fc65ddfe>KonomiTV</a> 最新版で NX-Jikkyo に対応しました！！🎉🎊</div><div class="mt-1" data-v-fc65ddfe> 最新情報は <a class="link" href="https://x.com/search?q=%23NXJikkyo&amp;src=typed_query" target="_blank" data-v-fc65ddfe>Twitter</a> で発信中です📣　 <a class="link" href="https://www.amazon.co.jp/hz/wishlist/ls/3AZ4RI13SW2PV?tag=tsukumijima-22" target="_blank" data-v-fc65ddfe>干し芋 or アマギフいただけると大変モチベ上がるのでぜひ🙇🙏</a></div><div class="mt-1" data-v-fc65ddfe><a class="link" href="https://x.com/TVRemotePlus/status/1807923274061697127" target="_blank" data-v-fc65ddfe>サーバーをスペックアップしました！🎉</a> ぜひ <a class="link" href="https://www.amazon.co.jp/dp/B08MTGFV39/?tag=tsukumijima-22" target="_blank" data-v-fc65ddfe>このアフィリンク</a> から Amazon で何かお買い物して頂けると助かります🙏 </div></div>',1),te={class:"channels-tab"},se=a(()=>t("div",{class:"channels-tab__highlight"},null,-1)),ne={class:"channel__broadcaster"},ae=["src"],ie={class:"channel__broadcaster-content"},ue={class:"channel__broadcaster-name"},oe={class:"channel__broadcaster-status"},re=a(()=>t("svg",{class:"iconify iconify--fa-solid",width:"10.5px",height:"12px",viewBox:"0 0 448 512"},[t("path",{fill:"currentColor",d:"M323.56 51.2c-20.8 19.3-39.58 39.59-56.22 59.97C240.08 73.62 206.28 35.53 168 0C69.74 91.17 0 209.96 0 281.6C0 408.85 100.29 512 224 512s224-103.15 224-230.4c0-53.27-51.98-163.14-124.44-230.4zm-19.47 340.65C282.43 407.01 255.72 416 226.86 416C154.71 416 96 368.26 96 290.75c0-38.61 24.31-72.63 72.79-130.75c6.93 7.98 98.83 125.34 98.83 125.34l58.63-66.88c4.14 6.85 7.91 13.55 11.27 19.97c27.35 52.19 15.81 118.97-33.43 153.42z"})],-1)),le=a(()=>t("span",{class:"ml-1"},"勢い:",-1)),de={class:"ml-1"},ce=a(()=>t("span",{style:{"margin-left":"3px"}}," コメ/分",-1)),_e={class:"channel__broadcaster-status-viewers ml-2"},he=a(()=>t("span",{class:"ml-1"},"コメント数:",-1)),pe={class:"ml-1"},me=["onClick"],fe=a(()=>t("svg",{class:"iconify iconify--fluent",width:"24px",height:"24px",viewBox:"0 0 20 20"},[t("path",{fill:"currentColor",d:"M13.325 2.617a2 2 0 0 0-3.203.52l-1.73 3.459a1.5 1.5 0 0 1-.784.721l-3.59 1.436a1 1 0 0 0-.335 1.636L6.293 13L3 16.292V17h.707L7 13.706l2.61 2.61a1 1 0 0 0 1.636-.335l1.436-3.59a1.5 1.5 0 0 1 .722-.784l3.458-1.73a2 2 0 0 0 .52-3.203l-4.057-4.057Z"})],-1)),ge=[fe],ve={class:"channel__program-present"},Ce={class:"channel__program-present-title-wrapper"},we=["innerHTML"],be={class:"channel__program-present-time"},Fe=["innerHTML"],Be={class:"channel__program-following"},Ee={class:"channel__program-following-title"},ke=a(()=>t("span",{class:"channel__program-following-title-decorate"},"NEXT",-1)),Se=a(()=>t("svg",{class:"channel__program-following-title-icon iconify iconify--fluent",width:"16px",height:"16px",viewBox:"0 0 20 20"},[t("path",{fill:"currentColor",d:"M10.018 5.486a1 1 0 0 1 1.592-.806l5.88 4.311a1.25 1.25 0 0 1 0 2.017l-5.88 4.311a1 1 0 0 1-1.592-.806v-3.16L4.61 15.319a1 1 0 0 1-1.592-.806V5.486A1 1 0 0 1 4.61 4.68l5.408 3.966v-3.16Z"})],-1)),Ae=["innerHTML"],De={class:"channel__program-following-time"},ye={class:"channel__progressbar"},xe={key:0,class:"pinned-container d-flex justify-center align-center w-100"},Pe={class:"d-flex justify-center align-center flex-column"},Te=a(()=>t("h2",null,[o("ピン留めされているチャンネルが"),t("br"),o("ありません。")],-1)),je={class:"mt-4 text-text-darken-1"},Ve=a(()=>t("br",null,null,-1)),Ue=a(()=>t("div",{class:"mt-2 text-text-darken-1"},[o("チャンネルをピン留めすると、"),t("br"),o("このタブが最初に表示されます。")],-1)),He={key:0,class:"channels-list pinned-container d-flex justify-center align-center w-100",style:{"flex-grow":"1"}},$e=D('<div class="d-flex justify-center align-center flex-column" data-v-fc65ddfe><h2 data-v-fc65ddfe>視聴可能なチャンネルが<br class="d-sm-none" data-v-fc65ddfe>ありません。</h2><div class="mt-4 text-text-darken-1" data-v-fc65ddfe>前回チャンネルスキャンしたときに<br class="d-sm-none" data-v-fc65ddfe>受信可能なチャンネルを見つけられませんでした。</div><div class="mt-1 text-text-darken-1" data-v-fc65ddfe>再度チャンネルスキャンを行ってください。</div></div>',1),Me=[$e];function Ne(e,n,h,f,Ie,ze){const y=c("HeaderBar"),x=c("Navigation"),b=c("Icon"),P=c("router-link"),T=c("SwiperSlide"),j=c("Swiper"),V=I("tooltip");return u(),r("div",Y,[_(y),t("main",null,[_(x),t("div",{class:p(["channels-container channels-container--home",{"channels-container--loading":e.is_loading}])},[ee,t("div",te,[t("div",{class:"channels-tab__buttons",style:E({"--tab-length":Array.from(e.channelsStore.channels_list_with_pinned).length,"--active-tab-index":e.active_tab_index})},[(u(!0),r(g,null,v(Array.from(e.channelsStore.channels_list_with_pinned),([i],d)=>(u(),w(L,{variant:"flat",class:p(["channels-tab__button",{"channels-tab__button--active":e.active_tab_index===d}]),key:i,onClick:s=>e.active_tab_index=d},{default:m(()=>[o(l(i),1)]),_:2},1032,["class","onClick"]))),128)),se],4)]),C(_(j,{class:"channels-list","space-between":32,"auto-height":!0,"touch-start-prevent-default":!1,observer:!0,"observe-parents":!0,onSwiper:n[1]||(n[1]=i=>e.swiper_instance=i),onSlideChange:n[2]||(n[2]=i=>e.active_tab_index=i.activeIndex)},{default:m(()=>[(u(!0),r(g,null,v(Array.from(e.channelsStore.channels_list_with_pinned),([i,d])=>(u(),w(T,{key:i},{default:m(()=>[t("div",{class:p(["channels",`channels--tab-${i} channels--length-${d.length}`])},[(u(!0),r(g,null,v(d,s=>C((u(),w(P,{class:"channel",draggable:"false",key:s.id,to:`/watch/${s.display_channel_id}`},{default:m(()=>[t("div",ne,[t("img",{class:"channel__broadcaster-icon",src:`${e.Utils.api_base_url}/channels/${s.id}/logo`},null,8,ae),t("div",ie,[t("span",ue,"Ch: "+l(s.channel_number)+" "+l(s.name),1),t("div",oe,[t("div",{class:p(["channel__broadcaster-status-force",`channel__broadcaster-status-force--${e.ChannelUtils.getChannelForceType(s.jikkyo_force)}`])},[re,le,t("span",de,l(s.jikkyo_force??"--"),1),ce],2),t("div",_e,[_(b,{icon:"bi:chat-left-text-fill",height:"11px"}),he,t("span",pe,l(s.viewer_count),1)])])]),C((u(),r("div",{class:p(["channel__broadcaster-pin",{"channel__broadcaster-pin--pinned":e.isPinnedChannel(s)}]),onClick:S(Le=>e.isPinnedChannel(s)?e.removePinnedChannel(s):e.addPinnedChannel(s),["prevent","stop"]),onMousedown:n[0]||(n[0]=S(()=>{},["prevent","stop"]))},ge,42,me)),[[A],[V,e.isPinnedChannel(s)?"ピン留めを外す":"ピン留めする"]])]),t("div",ve,[t("div",Ce,[t("span",{class:"channel__program-present-title",innerHTML:e.ProgramUtils.decorateProgramInfo(s.program_present,"title")},null,8,we),t("span",be,l(e.ProgramUtils.getProgramTime(s.program_present)),1)]),t("span",{class:"channel__program-present-description",innerHTML:e.ProgramUtils.decorateProgramInfo(s.program_present,"description")},null,8,Fe)]),_(W),t("div",Be,[t("div",Ee,[ke,Se,t("span",{class:"channel__program-following-title-text",innerHTML:e.ProgramUtils.decorateProgramInfo(s.program_following,"title")},null,8,Ae)]),t("span",De,l(e.ProgramUtils.getProgramTime(s.program_following)),1)]),t("div",ye,[t("div",{class:"channel__progressbar-progress",style:E(`width:${e.ProgramUtils.getProgramProgress(s.program_present)}%;`)},null,4)])]),_:2},1032,["to"])),[[A]])),128)),i==="ピン留め"&&d.length===0?(u(),r("div",xe,[t("div",Pe,[Te,t("div",je,[o("各チャンネルの "),_(b,{style:{position:"relative",bottom:"-5px"},icon:"fluent:pin-20-filled",width:"22px"}),o(" アイコンから、よく実況する"),Ve,o("チャンネルをこのタブにピン留めできます。")]),Ue])])):k("",!0)],2)]),_:2},1024))),128))]),_:1},512),[[z,Array.from(e.channelsStore.channels_list_with_pinned).length>0]]),Array.from(e.channelsStore.channels_list_with_pinned).length===0?(u(),r("div",He,Me)):k("",!0)],2)])])}const Oe=N(Q,[["render",Ne],["__scopeId","data-v-fc65ddfe"]]);export{Oe as default};
