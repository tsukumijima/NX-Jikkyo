import{d as p,m as _,_ as u,r as n,o as m,c as v,a as t,b as s,g as e,V as i,n as g,t as r,p as h,k as f}from"./index--jRW6aUY.js";import{H as x,N as b,u as S}from"./Navigation-ZyyA-CMr.js";import{a as B}from"./VCard-DYlqhwQD.js";import"./ssrBoot-vShFW_Pp.js";import"./VAvatar-CprxM-F-.js";const C=p({name:"Settings-Index",components:{HeaderBar:x,Navigation:b},computed:{..._(S)},async created(){await this.versionStore.fetchServerVersion()}}),c=a=>(h("data-v-34c04cbc"),a=a(),f(),a),k={class:"route-container"},w={class:"settings-navigation"},y=c(()=>s("h1",{class:"mt-2",style:{"font-size":"24px"}},"設定",-1)),I=c(()=>s("span",{class:"ml-4"},"全般",-1)),N=c(()=>s("span",{class:"ml-4"},"コメント/実況",-1)),V={class:"ml-4"};function H(a,$,A,j,z,D){const l=n("HeaderBar"),d=n("Navigation"),o=n("Icon");return m(),v("div",k,[t(l),s("main",null,[t(d),t(B,{class:"settings-container d-flex px-5 py-5 mx-auto",elevation:"0",width:"100%","max-width":"1000"},{default:e(()=>[s("nav",w,[y,t(i,{variant:"flat",class:"settings-navigation__button mt-6",to:"/settings/general"},{default:e(()=>[t(o,{icon:"fa-solid:sliders-h",width:"26px",style:{padding:"0 3px"}}),I]),_:1}),t(i,{variant:"flat",class:"settings-navigation__button",to:"/settings/jikkyo"},{default:e(()=>[t(o,{icon:"bi:chat-left-text-fill",width:"26px",style:{padding:"0 2px"}}),N]),_:1}),t(i,{variant:"flat",class:g(["settings-navigation__button settings-navigation__button--version",{"settings-navigation__button--version-highlight":a.versionStore.is_update_available}]),href:"https://github.com/tsukumijima/NX-Jikkyo"},{default:e(()=>[t(o,{icon:"fluent:info-16-regular",width:"26px"}),s("span",V," version "+r(a.versionStore.client_version)+r(a.versionStore.is_update_available?" (Update Available)":""),1)]),_:1},8,["class"])])]),_:1})])])}const q=u(C,[["render",H],["__scopeId","data-v-34c04cbc"]]);export{q as default};