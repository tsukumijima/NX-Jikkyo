import{V as T,_ as H,u as J}from"./ssrBoot-N4oCjL4t.js";import{d as A,y as L,a2 as W,r as w,o as v,c as y,w as h,k,h as d,b as o,l as R,A as X,V as C,i as j,R as f,q as V,s as N,e as c,_ as E,G as q,c_ as G,H as U,cQ as Q,cb as K,ca as M,dn as Y,I as O,cW as Z,cI as tt,J as et,dp as nt,d2 as at,cl as st,bD as S,cS as it,cg as ot,ck as rt,K as B,dq as lt,cX as ct,cR as ut,c7 as vt,dr as _t,ci as D,n as g,Q as dt,U as I,m as ht,a as ft,t as gt}from"./index-Cvbjt1uf.js";function pt(t,s,e,r){function l(n){return n instanceof e?n:new e(function(i){i(n)})}return new(e||(e=Promise))(function(n,i){function _(u){try{a(r.next(u))}catch(m){i(m)}}function p(u){try{a(r.throw(u))}catch(m){i(m)}}function a(u){u.done?n(u.value):l(u.value).then(_,p)}a((r=r.apply(t,[])).next())})}function mt(t,s){var e={label:0,sent:function(){if(n[0]&1)throw n[1];return n[1]},trys:[],ops:[]},r,l,n,i;return i={next:_(0),throw:_(1),return:_(2)},typeof Symbol=="function"&&(i[Symbol.iterator]=function(){return this}),i;function _(a){return function(u){return p([a,u])}}function p(a){if(r)throw new TypeError("Generator is already executing.");for(;i&&(i=0,a[0]&&(e=0)),e;)try{if(r=1,l&&(n=a[0]&2?l.return:a[0]?l.throw||((n=l.return)&&n.call(l),0):l.next)&&!(n=n.call(l,a[1])).done)return n;switch(l=0,n&&(a=[a[0]&2,n.value]),a[0]){case 0:case 1:n=a;break;case 4:return e.label++,{value:a[1],done:!1};case 5:e.label++,l=a[1],a=[0];continue;case 7:a=e.ops.pop(),e.trys.pop();continue;default:if(n=e.trys,!(n=n.length>0&&n[n.length-1])&&(a[0]===6||a[0]===2)){e=0;continue}if(a[0]===3&&(!n||a[1]>n[0]&&a[1]<n[3])){e.label=a[1];break}if(a[0]===6&&e.label<n[1]){e.label=n[1],n=a;break}if(n&&e.label<n[2]){e.label=n[2],e.ops.push(a);break}n[2]&&e.ops.pop(),e.trys.pop();continue}a=s.call(t,e)}catch(u){a=[6,u],l=0}finally{r=n=0}if(a[0]&5)throw a[1];return{value:a[0]?a[1]:void 0,done:!0}}}var kt=function(){function t(){var s=this;this.event=null,this.callbacks=[],this.install=function(){return pt(s,void 0,void 0,function(){var e=this;return mt(this,function(r){switch(r.label){case 0:return this.event?(this.event.prompt(),[4,this.event.userChoice.then(function(l){var n=l.outcome;return e.updateEvent(null),n==="accepted"||!0})]):[3,2];case 1:return[2,r.sent()];case 2:throw new Error("Not allowed to prompt.")}})})},!(typeof window>"u")&&(window.addEventListener("beforeinstallprompt",function(e){e.preventDefault(),s.updateEvent(e)}),window.addEventListener("appinstalled",function(){s.updateEvent(null)}))}return t.prototype.getEvent=function(){return this.event},t.prototype.canInstall=function(){return this.event!==null},t.prototype.updateEvent=function(s){var e=this;s!==this.event&&(this.event=s,this.callbacks.forEach(function(r){return r(e.canInstall())}))},t.prototype.addListener=function(s){s(this.canInstall()),this.callbacks.push(s)},t.prototype.removeListener=function(s){this.callbacks=this.callbacks.filter(function(e){return s!==e})},t}(),P=new kt;const z=t=>(V("data-v-7d4d6936"),t=t(),N(),t),bt={class:"header"},yt=z(()=>c("img",{class:"nx-jikkyo-logo__image",src:H,height:"35",alt:"NX-Jikkyo"},null,-1)),wt=z(()=>c("div",{class:"subtitle ml-2 pt-1 d-flex align-center text-text-darken-1",style:{"font-size":"15px","user-select":"none"}},[c("div",{class:"mr-2",style:{"font-size":"17px"}},"|"),R(" Nico Nico Jikkyo Alternative ")],-1)),St=A({__name:"HeaderBar",setup(t){const s=L(!1);return W(()=>{P.addListener(e=>{s.value=e})}),(e,r)=>{const l=w("router-link"),n=w("Icon");return v(),y("header",bt,[h((v(),k(l,{class:"nx-jikkyo-logo ml-3 ml-md-6",to:"/"},{default:d(()=>[yt]),_:1})),[[f]]),wt,o(T),s.value?(v(),k(C,{key:0,variant:"flat",color:"background-lighten-3",class:"pwa-install-button",onClick:r[0]||(r[0]=i=>X(P).install())},{default:d(()=>[o(n,{icon:"material-symbols:install-desktop-rounded",height:"20px",class:"mr-1"}),R(" アプリとしてインストール ")]),_:1})):j("",!0)])}}}),te=E(St,[["__scopeId","data-v-7d4d6936"]]),Bt=q({bgColor:String,color:String,grow:Boolean,mode:{type:String,validator:t=>!t||["horizontal","shift"].includes(t)},height:{type:[Number,String],default:56},active:{type:Boolean,default:!0},...G(),...U(),...Q(),...K(),...M(),...Y({name:"bottom-navigation"}),...O({tag:"header"}),...Z({modelValue:!0,selectedClass:"v-btn--selected"}),...tt()},"VBottomNavigation"),Ct=et()({name:"VBottomNavigation",props:Bt(),emits:{"update:modelValue":t=>!0},setup(t,s){let{slots:e}=s;const{themeClasses:r}=nt(),{borderClasses:l}=at(t),{backgroundColorClasses:n,backgroundColorStyles:i}=st(S(t,"bgColor")),{densityClasses:_}=it(t),{elevationClasses:p}=ot(t),{roundedClasses:a}=rt(t),{ssrBootStyles:u}=J(),m=B(()=>Number(t.height)-(t.density==="comfortable"?8:0)-(t.density==="compact"?16:0)),x=S(t,"active"),{layoutItemStyles:F}=lt({id:t.name,order:B(()=>parseInt(t.order,10)),position:B(()=>"bottom"),layoutSize:B(()=>x.value?m.value:0),elementSize:m,active:x,absolute:S(t,"absolute")});return ct(t,_t),ut({VBtn:{color:S(t,"color"),density:S(t,"density"),stacked:B(()=>t.mode!=="horizontal"),variant:"text"}},{scoped:!0}),vt(()=>o(t.tag,{class:["v-bottom-navigation",{"v-bottom-navigation--active":x.value,"v-bottom-navigation--grow":t.grow,"v-bottom-navigation--shift":t.mode==="shift"},r.value,n.value,l.value,_.value,p.value,a.value,t.class],style:[i.value,F.value,{height:D(m.value),transform:`translateY(${D(x.value?0:100,"%")})`},u.value,t.style]},{default:()=>[e.default&&o("div",{class:"v-bottom-navigation__content"},[e.default()])]})),{}}}),xt={},$=t=>(V("data-v-93ece83c"),t=t(),N(),t),$t=$(()=>c("span",{class:"mt-1"},"テレビ実況",-1)),It=$(()=>c("span",{class:"mt-1"},"過去ログ再生",-1)),Vt=$(()=>c("span",{class:"mt-1"},"NX-Jikkyo とは",-1)),Nt=$(()=>c("span",{class:"mt-1"},"設定",-1));function Et(t,s){const e=w("Icon");return v(),k(Ct,{class:"bottom-navigation-container elevation-12",color:"primary",grow:"",active:""},{default:d(()=>[o(C,{class:g(["bottom-navigation-button",{"v-btn--active":t.$route.path=="/"}]),to:"/"},{default:d(()=>[o(e,{icon:"fluent:tv-20-regular",width:"30px"}),$t]),_:1},8,["class"]),o(C,{class:g(["bottom-navigation-button",{"v-btn--active":t.$route.path.startsWith("/log")}]),to:"/log/"},{default:d(()=>[o(e,{icon:"fluent:receipt-play-20-regular",width:"30px"}),It]),_:1},8,["class"]),o(C,{class:g(["bottom-navigation-button",{"v-btn--active":t.$route.path.startsWith("/about")}]),to:"/about/"},{default:d(()=>[o(e,{icon:"fluent:info-16-regular",width:"26px"}),Vt]),_:1},8,["class"]),o(C,{class:g(["bottom-navigation-button",{"v-btn--active":t.$route.path.startsWith("/settings")}]),to:"/settings/"},{default:d(()=>[o(e,{icon:"fluent:settings-20-regular",width:"30px"}),Nt]),_:1},8,["class"])]),_:1})}const Dt=E(xt,[["render",Et],["__scopeId","data-v-93ece83c"]]);class Pt{static async fetchServerVersion(s=!1){return null}}const Tt=dt("version",{state:()=>({server_version_info:null,last_updated_at:0}),getters:{client_version(){return I.version},server_version(){var t;return((t=this.server_version_info)==null?void 0:t.version)??null},latest_version(){var t;return((t=this.server_version_info)==null?void 0:t.latest_version)??null},is_client_develop_version(){return this.client_version.includes("-dev")},is_server_develop_version(){var t;return((t=this.server_version)==null?void 0:t.includes("-dev"))??!1},is_update_available(){return this.server_version===null||this.latest_version===null?!1:this.is_server_develop_version===!1&&this.server_version!==this.latest_version||this.is_server_develop_version===!0&&this.server_version.replace("-dev","")===this.latest_version},is_version_mismatch(){return this.server_version===null?!1:this.client_version!==this.server_version}},actions:{async fetchServerVersion(t=!1){if(this.server_version_info!==null&&t===!1)return I.time()-this.last_updated_at>60&&this.fetchServerVersion(!0),this.server_version_info;const s=await Pt.fetchServerVersion();return s===null?null:(this.server_version_info=s,this.last_updated_at=I.time(),this.server_version_info)}}}),At=Tt,Rt=A({name:"Navigation",components:{BottomNavigation:Dt},computed:{...ht(At)},async created(){await this.versionStore.fetchServerVersion()}}),b=t=>(V("data-v-0957749e"),t=t(),N(),t),zt={class:"navigation-container elevation-8"},Ft={class:"navigation"},Ht={class:"navigation-scroll"},Jt=b(()=>c("span",{class:"navigation__link-text"},"テレビ実況",-1)),Lt=b(()=>c("span",{class:"navigation__link-text"},"過去ログ再生",-1)),Wt={class:"navigation__link","active-class":"navigation__link--active",href:"https://jikkyo.tsukumijima.net",target:"_blank"},Xt=b(()=>c("span",{class:"navigation__link-text"},"過去ログ API",-1)),jt=b(()=>c("span",{class:"navigation__link-text"},"NX-Jikkyo とは",-1)),qt=b(()=>c("span",{class:"navigation__link-text"},"設定",-1)),Gt={class:"navigation__link","active-class":"navigation__link--active",href:"https://x.com/search?q=%23NXJikkyo%20from%3ATVRemotePlus&src=typed_query&f=live",target:"_blank"},Ut=b(()=>c("span",{class:"navigation__link-text"},"最新情報",-1)),Qt={class:"navigation__link","active-class":"navigation__link--active",href:"https://x.com/TVRemotePlus",target:"_blank"},Kt=b(()=>c("span",{class:"navigation__link-text"},"公式 Twitter",-1)),Mt={class:"navigation__link-text"};function Yt(t,s,e,r,l,n){const i=w("Icon"),_=w("router-link"),p=w("BottomNavigation"),a=ft("tooltip");return v(),y("div",null,[c("div",zt,[c("nav",Ft,[c("div",Ht,[h((v(),k(_,{class:g(["navigation__link",{"navigation__link--active":t.$route.path=="/"}]),"active-class":"navigation__link--active",to:"/"},{default:d(()=>[o(i,{class:"navigation__link-icon",icon:"fluent:tv-20-regular",width:"26px"}),Jt]),_:1},8,["class"])),[[f]]),h((v(),k(_,{class:g(["navigation__link",{"navigation__link--active":t.$route.path.startsWith("/log")}]),"active-class":"navigation__link--active",to:"/log/"},{default:d(()=>[o(i,{class:"navigation__link-icon",icon:"fluent:receipt-play-20-regular",width:"26px"}),Lt]),_:1},8,["class"])),[[f]]),h((v(),y("a",Wt,[o(i,{class:"navigation__link-icon",icon:"fluent:slide-text-multiple-20-regular",width:"26px"}),Xt])),[[f]]),h((v(),k(_,{class:g(["navigation__link",{"navigation__link--active":t.$route.path.startsWith("/about")}]),"active-class":"navigation__link--active",to:"/about/"},{default:d(()=>[o(i,{class:"navigation__link-icon",icon:"fluent:info-16-regular",width:"26px"}),jt]),_:1},8,["class"])),[[f]]),o(T),h((v(),k(_,{class:g(["navigation__link",{"navigation__link--active":t.$route.path.startsWith("/settings")}]),"active-class":"navigation__link--active",to:"/settings/"},{default:d(()=>[o(i,{class:"navigation__link-icon",icon:"fluent:settings-20-regular",width:"26px"}),qt]),_:1},8,["class"])),[[f]]),h((v(),y("a",Gt,[o(i,{class:"navigation__link-icon",icon:"fluent:news-20-regular",width:"26px"}),Ut])),[[f]]),h((v(),y("a",Qt,[o(i,{class:"navigation__link-icon",icon:"basil:twitter-outline",width:"26px"}),Kt])),[[f]]),h((v(),y("a",{class:g(["navigation__link",{"navigation__link--develop-version":t.versionStore.is_client_develop_version,"navigation__link--highlight":t.versionStore.is_update_available}]),"active-class":"navigation__link--active",href:"https://github.com/tsukumijima/NX-Jikkyo",target:"_blank"},[o(i,{class:"navigation__link-icon",icon:"fluent:info-16-regular",width:"26px"}),c("span",Mt,"version "+gt(t.versionStore.client_version),1)],2)),[[f],[a,t.versionStore.is_update_available?`アップデートがあります (version ${t.versionStore.latest_version})`:"",void 0,{top:!0}]])])])]),o(p)])}const ee=E(Rt,[["render",Yt],["__scopeId","data-v-0957749e"]]);export{te as H,ee as N,At as u};
