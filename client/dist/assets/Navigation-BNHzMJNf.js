import{V as D,_ as E,u as z}from"./ssrBoot-YRM7ru8H.js";import{_ as $,r as h,o,c as p,w as c,k as g,h as i,b as e,R as v,q as V,s as w,e as s,z as R,cW as T,A as W,cK as F,c9 as J,c8 as U,dl as X,B as G,cS as H,cA as L,C as q,dm as K,c_ as M,cj as O,bA as u,cO as Y,ce as Q,ci as Z,D as d,dn as tt,cT as et,cM as st,c5 as at,dp as ot,cg as P,n as l,V as f,I as it,U as C,d as nt,m as rt,a as lt,t as ct}from"./index-BD7LREOA.js";const vt={},_t=t=>(V("data-v-bc91920e"),t=t(),w(),t),ut={class:"header"},dt=_t(()=>s("img",{class:"nx-jikkyo-logo__image",src:E,height:"35"},null,-1));function ht(t,n){const a=h("router-link");return o(),p("header",ut,[c((o(),g(a,{class:"nx-jikkyo-logo ml-3 ml-md-6",to:"/"},{default:i(()=>[dt]),_:1})),[[v]]),e(D)])}const Ft=$(vt,[["render",ht],["__scopeId","data-v-bc91920e"]]),gt=R({bgColor:String,color:String,grow:Boolean,mode:{type:String,validator:t=>!t||["horizontal","shift"].includes(t)},height:{type:[Number,String],default:56},active:{type:Boolean,default:!0},...T(),...W(),...F(),...J(),...U(),...X({name:"bottom-navigation"}),...G({tag:"header"}),...H({modelValue:!0,selectedClass:"v-btn--selected"}),...L()},"VBottomNavigation"),mt=q()({name:"VBottomNavigation",props:gt(),emits:{"update:modelValue":t=>!0},setup(t,n){let{slots:a}=n;const{themeClasses:I}=K(),{borderClasses:N}=M(t),{backgroundColorClasses:x,backgroundColorStyles:r}=O(u(t,"bgColor")),{densityClasses:_}=Y(t),{elevationClasses:S}=Q(t),{roundedClasses:y}=Z(t),{ssrBootStyles:A}=z(),B=d(()=>Number(t.height)-(t.density==="comfortable"?8:0)-(t.density==="compact"?16:0)),m=u(t,"active"),{layoutItemStyles:j}=tt({id:t.name,order:d(()=>parseInt(t.order,10)),position:d(()=>"bottom"),layoutSize:d(()=>m.value?B.value:0),elementSize:B,active:m,absolute:u(t,"absolute")});return et(t,ot),st({VBtn:{color:u(t,"color"),density:u(t,"density"),stacked:d(()=>t.mode!=="horizontal"),variant:"text"}},{scoped:!0}),at(()=>e(t.tag,{class:["v-bottom-navigation",{"v-bottom-navigation--active":m.value,"v-bottom-navigation--grow":t.grow,"v-bottom-navigation--shift":t.mode==="shift"},I.value,x.value,N.value,_.value,S.value,y.value,t.class],style:[r.value,j.value,{height:P(B.value),transform:`translateY(${P(m.value?0:100,"%")})`},A.value,t.style]},{default:()=>[a.default&&e("div",{class:"v-bottom-navigation__content"},[a.default()])]})),{}}}),ft={},k=t=>(V("data-v-cc058374"),t=t(),w(),t),pt=k(()=>s("span",{class:"mt-1"},"テレビ実況",-1)),kt=k(()=>s("span",{class:"mt-1"},"過去ログ API",-1)),bt=k(()=>s("span",{class:"mt-1"},"NX-Jikkyo とは",-1)),St=k(()=>s("span",{class:"mt-1"},"設定",-1));function yt(t,n){const a=h("Icon");return o(),g(mt,{class:"bottom-navigation-container elevation-12",color:"primary",grow:"",active:""},{default:i(()=>[e(f,{class:l(["bottom-navigation-button",{"v-btn--active":t.$route.path=="/"}]),to:"/"},{default:i(()=>[e(a,{icon:"fluent:tv-20-regular",width:"30px"}),pt]),_:1},8,["class"]),e(f,{class:"bottom-navigation-button",href:"https://jikkyo.tsukumijima.net",target:"_blank"},{default:i(()=>[e(a,{icon:"fluent:slide-text-multiple-20-regular",width:"26px"}),kt]),_:1}),e(f,{class:l(["bottom-navigation-button",{"v-btn--active":t.$route.path.startsWith("/about")}]),to:"/about/"},{default:i(()=>[e(a,{icon:"fluent:info-16-regular",width:"26px"}),bt]),_:1},8,["class"]),e(f,{class:l(["bottom-navigation-button",{"v-btn--active":t.$route.path.startsWith("/settings")}]),to:"/settings/"},{default:i(()=>[e(a,{icon:"fluent:settings-20-regular",width:"30px"}),St]),_:1},8,["class"])]),_:1})}const Bt=$(ft,[["render",yt],["__scopeId","data-v-cc058374"]]);class Ct{static async fetchServerVersion(n=!1){return null}}const $t=it("version",{state:()=>({server_version_info:null,last_updated_at:0}),getters:{client_version(){return C.version},server_version(){var t;return((t=this.server_version_info)==null?void 0:t.version)??null},latest_version(){var t;return((t=this.server_version_info)==null?void 0:t.latest_version)??null},is_client_develop_version(){return this.client_version.includes("-dev")},is_server_develop_version(){var t;return((t=this.server_version)==null?void 0:t.includes("-dev"))??!1},is_update_available(){return this.server_version===null||this.latest_version===null?!1:this.is_server_develop_version===!1&&this.server_version!==this.latest_version||this.is_server_develop_version===!0&&this.server_version.replace("-dev","")===this.latest_version},is_version_mismatch(){return this.server_version===null?!1:this.client_version!==this.server_version}},actions:{async fetchServerVersion(t=!1){if(this.server_version_info!==null&&t===!1)return C.time()-this.last_updated_at>60&&this.fetchServerVersion(!0),this.server_version_info;const n=await Ct.fetchServerVersion();return n===null?null:(this.server_version_info=n,this.last_updated_at=C.time(),this.server_version_info)}}}),Vt=$t,wt=nt({name:"Navigation",components:{BottomNavigation:Bt},computed:{...rt(Vt)},async created(){await this.versionStore.fetchServerVersion()}}),b=t=>(V("data-v-7290f238"),t=t(),w(),t),It={class:"navigation-container elevation-8"},Nt={class:"navigation"},xt={class:"navigation-scroll"},Pt=b(()=>s("span",{class:"navigation__link-text"},"テレビ実況",-1)),Dt={class:"navigation__link","active-class":"navigation__link--active",href:"https://jikkyo.tsukumijima.net",target:"_blank"},At=b(()=>s("span",{class:"navigation__link-text"},"過去ログ API",-1)),jt=b(()=>s("span",{class:"navigation__link-text"},"NX-Jikkyo とは",-1)),Et=b(()=>s("span",{class:"navigation__link-text"},"設定",-1)),zt={class:"navigation__link-text"};function Rt(t,n,a,I,N,x){const r=h("Icon"),_=h("router-link"),S=h("BottomNavigation"),y=lt("tooltip");return o(),p("div",null,[s("div",It,[s("nav",Nt,[s("div",xt,[c((o(),g(_,{class:l(["navigation__link",{"navigation__link--active":t.$route.path=="/"}]),"active-class":"navigation__link--active",to:"/"},{default:i(()=>[e(r,{class:"navigation__link-icon",icon:"fluent:tv-20-regular",width:"26px"}),Pt]),_:1},8,["class"])),[[v]]),c((o(),p("a",Dt,[e(r,{class:"navigation__link-icon",icon:"fluent:slide-text-multiple-20-regular",width:"26px"}),At])),[[v]]),c((o(),g(_,{class:l(["navigation__link",{"navigation__link--active":t.$route.path.startsWith("/about")}]),"active-class":"navigation__link--active",to:"/about/"},{default:i(()=>[e(r,{class:"navigation__link-icon",icon:"fluent:info-16-regular",width:"26px"}),jt]),_:1},8,["class"])),[[v]]),e(D),c((o(),g(_,{class:l(["navigation__link",{"navigation__link--active":t.$route.path.startsWith("/settings")}]),"active-class":"navigation__link--active",to:"/settings/"},{default:i(()=>[e(r,{class:"navigation__link-icon",icon:"fluent:settings-20-regular",width:"26px"}),Et]),_:1},8,["class"])),[[v]]),c((o(),p("a",{class:l(["navigation__link",{"navigation__link--develop-version":t.versionStore.is_client_develop_version,"navigation__link--highlight":t.versionStore.is_update_available}]),"active-class":"navigation__link--active",href:"https://github.com/tsukumijima/NX-Jikkyo",target:"_blank"},[e(r,{class:"navigation__link-icon",icon:"fluent:info-16-regular",width:"26px"}),s("span",zt,"version "+ct(t.versionStore.client_version),1)],2)),[[v],[y,t.versionStore.is_update_available?`アップデートがあります (version ${t.versionStore.latest_version})`:"",void 0,{top:!0}]])])])]),e(S)])}const Jt=$(wt,[["render",Rt],["__scopeId","data-v-7290f238"]]);export{Ft as H,Jt as N,Vt as u};