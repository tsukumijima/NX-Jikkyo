import{d,m as h,U as u,u as m,_,r as y,o as f,l as S}from"./index-0KBw0l56.js";import{W as w,P as v,u as $}from"./PlayerController-Bs0HlLBy.js";import{u as b}from"./ChannelsStore-6BmmP5gh.js";import"./ssrBoot-Drq5GoA5.js";import"./VSwitch-CyZlsd4u.js";import"./VSelect-DeY_zS_n.js";import"./VAvatar-CV6GnAd0.js";import"./VCard-2D6Bj1o0.js";import"./swiper-C9tqf6EG.js";import"./CommentMuteSettings-CA22Rt8J.js";let r=null;const g=d({name:"TV-Watch",components:{Watch:w},data(){return{interval_ids:[]}},computed:{...h(b,$,m)},created(){this.channelsStore.display_channel_id=this.$route.params.display_channel_id,this.init()},beforeRouteUpdate(n,e,i){const t=this.destroy();this.channelsStore.display_channel_id=n.params.display_channel_id,(async()=>this.playerStore.is_zapping===!0?(this.playerStore.is_zapping=!1,this.interval_ids.push(window.setTimeout(()=>{t.then(()=>this.init())},.5*1e3))):t.then(()=>this.init()))(),i()},beforeUnmount(){this.destroy(),this.channelsStore.display_channel_id="gr000"},methods:{async init(){var i;if(this.interval_ids.push(window.setTimeout(()=>{this.channelsStore.update(!0),this.interval_ids.push(window.setInterval(()=>{this.channelsStore.update(!0)},30*1e3))},0*1e3)),await this.channelsStore.update(),this.$route.params.display_channel_id===void 0){this.$router.push({path:"/not-found/"});return}if(this.channelsStore.channel.current.name==="チャンネル情報取得エラー"){await u.sleep(3),this.$router.push({path:"/not-found/"});return}const e=this.channelsStore.channel.current;if(e){const t=`テレビ実況 - Ch: ${e.channel_number} ${e.name} | NX-Jikkyo : ニコニコ実況避難所`,s=((i=e.program_present)==null?void 0:i.description)||"";document.title=t;const a=document.querySelector('meta[name="description"]');a&&a.setAttribute("content",s);const o=document.querySelector('meta[property="og:title"]');o&&o.setAttribute("content",t);const c=document.querySelector('meta[property="og:description"]');c&&c.setAttribute("content",s);const l=document.querySelector('meta[name="twitter:title"]');l&&l.setAttribute("content",t);const p=document.querySelector('meta[name="twitter:description"]');p&&p.setAttribute("content",s)}r=new v("Live"),await r.init()},async destroy(){for(const n of this.interval_ids)window.clearInterval(n);this.interval_ids=[],r!==null&&(await r.destroy(),r=null)}}});function W(n,e,i,t,s,a){const o=y("Watch",!0);return f(),S(o,{playback_mode:"Live"})}const I=_(g,[["render",W]]);export{I as default};
