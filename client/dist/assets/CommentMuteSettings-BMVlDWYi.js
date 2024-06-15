import{x as $,A as L,a4 as M,W as Z,ap as j,N as y,a6 as T,a1 as z,a8 as A,a as s,aq as R,ar as N,d as O,m as H,u as q,_ as W,r as G,o as c,j as J,g as v,w as b,c as E,b as e,V as S,f as k,F as U,R as V,p as K,l as Q,k as m}from"./index-7ItfYin_.js";import{q as X,r as Y,s as uu,i as eu,t as x,j as B,v as P,l as tu}from"./VSwitch-DF_yn8_F.js";import{V as su,a as ou}from"./VCard-D5i-sL4O.js";import{V as iu}from"./ssrBoot-DpC4T-nM.js";const nu=$({fullscreen:Boolean,retainFocus:{type:Boolean,default:!0},scrollable:Boolean,...X({origin:"center center",scrollStrategy:"block",transition:{component:Y},zIndex:2400})},"VDialog"),au=L()({name:"VDialog",props:nu(),emits:{"update:modelValue":u=>!0,afterLeave:()=>!0},setup(u,o){let{emit:D,slots:h}=o;const p=M(u,"modelValue"),{scopeId:w}=uu(),n=Z();function t(l){var g,F;const _=l.relatedTarget,C=l.target;if(_!==C&&((g=n.value)!=null&&g.contentEl)&&((F=n.value)!=null&&F.globalTop)&&![document,n.value.contentEl].includes(C)&&!n.value.contentEl.contains(C)){const r=N(n.value.contentEl);if(!r.length)return;const f=r[0],I=r[r.length-1];_===f?I.focus():f.focus()}}j&&y(()=>p.value&&u.retainFocus,l=>{l?document.addEventListener("focusin",t):document.removeEventListener("focusin",t)},{immediate:!0});function a(){var l;(l=n.value)!=null&&l.contentEl&&!n.value.contentEl.contains(document.activeElement)&&n.value.contentEl.focus({preventScroll:!0})}function d(){D("afterLeave")}return y(p,async l=>{var _;l||(await z(),(_=n.value.activatorEl)==null||_.focus({preventScroll:!0}))}),T(()=>{const l=x.filterProps(u),_=A({"aria-haspopup":"dialog","aria-expanded":String(p.value)},u.activatorProps),C=A({tabindex:-1},u.contentProps);return s(x,A({ref:n,class:["v-dialog",{"v-dialog--fullscreen":u.fullscreen,"v-dialog--scrollable":u.scrollable},u.class],style:u.style},l,{modelValue:p.value,"onUpdate:modelValue":g=>p.value=g,"aria-modal":"true",activatorProps:_,contentProps:C,role:"dialog",onAfterEnter:a,onAfterLeave:d},w),{activator:h.activator,default:function(){for(var g=arguments.length,F=new Array(g),r=0;r<g;r++)F[r]=arguments[r];return s(R,{root:"VDialog"},{default:()=>{var f;return[(f=h.default)==null?void 0:f.call(h,...F)]}})}})}),eu({},n)}}),lu=O({name:"CommentMuteSettings",props:{modelValue:{type:Boolean,required:!0}},emits:{"update:modelValue":u=>!0},data(){return{comment_mute_settings_modal:!1,muted_comment_keyword_match_type:[{title:"部分一致",value:"partial"},{title:"前方一致",value:"forward"},{title:"後方一致",value:"backward"},{title:"完全一致",value:"exact"},{title:"正規表現",value:"regex"}]}},computed:{...H(q)},watch:{modelValue(){this.comment_mute_settings_modal=this.modelValue},comment_mute_settings_modal(){this.$emit("update:modelValue",this.comment_mute_settings_modal)}}}),i=u=>(K("data-v-9a8b82e1"),u=u(),Q(),u),mu=i(()=>e("span",{class:"ml-3"},"コメントのミュート設定",-1)),du={class:"px-5 pb-6"},ru={class:"text-subtitle-1 d-flex align-center font-weight-bold mt-4"},cu=i(()=>e("span",{class:"ml-2"},"クイック設定",-1)),_u={class:"settings__item settings__item--switch"},gu=i(()=>e("label",{class:"settings__item-heading",for:"mute_vulgar_comments"}," 露骨な表現を含むコメントをミュートする ",-1)),Eu=i(()=>e("label",{class:"settings__item-label",for:"mute_vulgar_comments"},[m(" 性的な単語などの露骨・下品な表現を含むコメントを、一括でミュートするかを設定します。"),e("br")],-1)),pu={class:"settings__item settings__item--switch"},Bu=i(()=>e("label",{class:"settings__item-heading",for:"mute_abusive_discriminatory_prejudiced_comments"}," ネガティブな表現、差別的な表現、政治的に偏った表現を含むコメントをミュートする ",-1)),hu=i(()=>e("label",{class:"settings__item-label",for:"mute_abusive_discriminatory_prejudiced_comments"},[m(" 『死ね』『殺す』などのネガティブな表現、特定の国や人々への差別的な表現、政治的に偏った表現を含むコメントを、一括でミュートするかを設定します。"),e("br")],-1)),Cu={class:"settings__item settings__item--switch"},Fu=i(()=>e("label",{class:"settings__item-heading",for:"mute_big_size_comments"}," 文字サイズが大きいコメントをミュートする ",-1)),fu=i(()=>e("label",{class:"settings__item-label",for:"mute_big_size_comments"},[m(" 通常より大きい文字サイズで表示されるコメントを、一括でミュートするかを設定します。"),e("br"),m(" 文字サイズが大きいコメントには迷惑なコメントが多いです。基本的にはオンにしておくのがおすすめです。"),e("br")],-1)),vu={class:"settings__item settings__item--switch"},Au=i(()=>e("label",{class:"settings__item-heading",for:"mute_fixed_comments"}," 映像の上下に固定表示されるコメントをミュートする ",-1)),bu=i(()=>e("label",{class:"settings__item-label",for:"mute_fixed_comments"},[m(" 映像の上下に固定された状態で表示されるコメントを、一括でミュートするかを設定します。"),e("br"),m(" 固定表示されるコメントが煩わしい方におすすめです。"),e("br")],-1)),Vu={class:"settings__item settings__item--switch"},Du=i(()=>e("label",{class:"settings__item-heading",for:"mute_colored_comments"}," 色付きのコメントをミュートする ",-1)),wu=i(()=>e("label",{class:"settings__item-label",for:"mute_colored_comments"},[m(" 白以外の色で表示される色付きのコメントを、一括でミュートするかを設定します。"),e("br"),m(" この設定をオンにしておくと、目立つ色のコメントを一掃できます。"),e("br")],-1)),yu={class:"settings__item settings__item--switch"},Su=i(()=>e("label",{class:"settings__item-heading",for:"mute_consecutive_same_characters_comments"}," 8文字以上同じ文字が連続しているコメントをミュートする ",-1)),ku=i(()=>e("label",{class:"settings__item-label",for:"mute_consecutive_same_characters_comments"},[m(" 『wwwwwwwwwww』『あばばばばばばばばば』など、8文字以上同じ文字が連続しているコメントを、一括でミュートするかを設定します。"),e("br"),m(" しばしばあるテンプレコメントが煩わしい方におすすめです。"),e("br")],-1)),Uu={class:"text-subtitle-1 d-flex align-center font-weight-bold mt-4"},xu=i(()=>e("span",{class:"ml-2 mr-2"},"ミュート済みのキーワード",-1)),Pu=i(()=>e("span",{class:"ml-1"},"追加",-1)),Iu={class:"muted-comment-items"},$u=["onClick"],Lu=i(()=>e("svg",{class:"iconify iconify--fluent",width:"20px",height:"20px",viewBox:"0 0 16 16"},[e("path",{fill:"currentColor",d:"M7 3h2a1 1 0 0 0-2 0ZM6 3a2 2 0 1 1 4 0h4a.5.5 0 0 1 0 1h-.564l-1.205 8.838A2.5 2.5 0 0 1 9.754 15H6.246a2.5 2.5 0 0 1-2.477-2.162L2.564 4H2a.5.5 0 0 1 0-1h4Zm1 3.5a.5.5 0 0 0-1 0v5a.5.5 0 0 0 1 0v-5ZM9.5 6a.5.5 0 0 0-.5.5v5a.5.5 0 0 0 1 0v-5a.5.5 0 0 0-.5-.5Z"})],-1)),Mu=[Lu],Zu={class:"text-subtitle-1 d-flex align-center font-weight-bold mt-4"},ju=i(()=>e("span",{class:"ml-2 mr-2"},"ミュート済みのユーザー ID",-1)),Tu=i(()=>e("span",{class:"ml-1"},"追加",-1)),zu={class:"muted-comment-items"},Ru=["onClick"],Nu=i(()=>e("svg",{class:"iconify iconify--fluent",width:"20px",height:"20px",viewBox:"0 0 16 16"},[e("path",{fill:"currentColor",d:"M7 3h2a1 1 0 0 0-2 0ZM6 3a2 2 0 1 1 4 0h4a.5.5 0 0 1 0 1h-.564l-1.205 8.838A2.5 2.5 0 0 1 9.754 15H6.246a2.5 2.5 0 0 1-2.477-2.162L2.564 4H2a.5.5 0 0 1 0-1h4Zm1 3.5a.5.5 0 0 0-1 0v5a.5.5 0 0 0 1 0v-5ZM9.5 6a.5.5 0 0 0-.5.5v5a.5.5 0 0 0 1 0v-5a.5.5 0 0 0-.5-.5Z"})],-1)),Ou=[Nu];function Hu(u,o,D,h,p,w){const n=G("Icon");return c(),J(au,{"max-width":"770",transition:"slide-y-transition",modelValue:u.comment_mute_settings_modal,"onUpdate:modelValue":o[9]||(o[9]=t=>u.comment_mute_settings_modal=t)},{default:v(()=>[s(ou,{class:"comment-mute-settings"},{default:v(()=>[s(su,{class:"px-5 pt-6 pb-3 d-flex align-center font-weight-bold",style:{height:"60px"}},{default:v(()=>[s(n,{icon:"heroicons-solid:filter",height:"26px"}),mu,s(iu),b((c(),E("div",{class:"d-flex align-center rounded-circle cursor-pointer px-2 py-2",onClick:o[0]||(o[0]=t=>u.comment_mute_settings_modal=!1)},[s(n,{icon:"fluent:dismiss-12-filled",width:"23px",height:"23px"})])),[[V]])]),_:1}),e("div",du,[e("div",ru,[s(n,{icon:"fa-solid:sliders-h",width:"24px",height:"20px"}),cu]),e("div",_u,[gu,Eu,s(B,{class:"settings__item-switch",color:"primary",id:"mute_vulgar_comments","hide-details":"",modelValue:u.settingsStore.settings.mute_vulgar_comments,"onUpdate:modelValue":o[1]||(o[1]=t=>u.settingsStore.settings.mute_vulgar_comments=t)},null,8,["modelValue"])]),e("div",pu,[Bu,hu,s(B,{class:"settings__item-switch",color:"primary",id:"mute_abusive_discriminatory_prejudiced_comments","hide-details":"",modelValue:u.settingsStore.settings.mute_abusive_discriminatory_prejudiced_comments,"onUpdate:modelValue":o[2]||(o[2]=t=>u.settingsStore.settings.mute_abusive_discriminatory_prejudiced_comments=t)},null,8,["modelValue"])]),e("div",Cu,[Fu,fu,s(B,{class:"settings__item-switch",color:"primary",id:"mute_big_size_comments","hide-details":"",modelValue:u.settingsStore.settings.mute_big_size_comments,"onUpdate:modelValue":o[3]||(o[3]=t=>u.settingsStore.settings.mute_big_size_comments=t)},null,8,["modelValue"])]),e("div",vu,[Au,bu,s(B,{class:"settings__item-switch",color:"primary",id:"mute_fixed_comments","hide-details":"",modelValue:u.settingsStore.settings.mute_fixed_comments,"onUpdate:modelValue":o[4]||(o[4]=t=>u.settingsStore.settings.mute_fixed_comments=t)},null,8,["modelValue"])]),e("div",Vu,[Du,wu,s(B,{class:"settings__item-switch",color:"primary",id:"mute_colored_comments","hide-details":"",modelValue:u.settingsStore.settings.mute_colored_comments,"onUpdate:modelValue":o[5]||(o[5]=t=>u.settingsStore.settings.mute_colored_comments=t)},null,8,["modelValue"])]),e("div",yu,[Su,ku,s(B,{class:"settings__item-switch",color:"primary",id:"mute_consecutive_same_characters_comments","hide-details":"",modelValue:u.settingsStore.settings.mute_consecutive_same_characters_comments,"onUpdate:modelValue":o[6]||(o[6]=t=>u.settingsStore.settings.mute_consecutive_same_characters_comments=t)},null,8,["modelValue"])]),e("div",Uu,[s(n,{icon:"fluent:comment-dismiss-20-filled",width:"24px"}),xu,s(S,{class:"ml-auto",color:"background-lighten-2",variant:"flat",onClick:o[7]||(o[7]=t=>u.settingsStore.settings.muted_comment_keywords.unshift({match:"partial",pattern:""}))},{default:v(()=>[s(n,{icon:"fluent:add-12-filled",height:"17px"}),Pu]),_:1})]),e("div",Iu,[(c(!0),E(U,null,k(u.settingsStore.settings.muted_comment_keywords,(t,a)=>(c(),E("div",{class:"muted-comment-item",key:a},[s(P,{type:"search",class:"muted-comment-item__input",color:"primary",density:"compact",variant:"outlined","hide-details":"",placeholder:"ミュートするキーワードを入力",modelValue:u.settingsStore.settings.muted_comment_keywords[a].pattern,"onUpdate:modelValue":d=>u.settingsStore.settings.muted_comment_keywords[a].pattern=d},null,8,["modelValue","onUpdate:modelValue"]),s(tu,{class:"muted-comment-item__match-type",color:"primary",density:"compact",variant:"outlined","hide-details":"",items:u.muted_comment_keyword_match_type,modelValue:u.settingsStore.settings.muted_comment_keywords[a].match,"onUpdate:modelValue":d=>u.settingsStore.settings.muted_comment_keywords[a].match=d},null,8,["items","modelValue","onUpdate:modelValue"]),b((c(),E("button",{class:"muted-comment-item__delete-button",onClick:d=>u.settingsStore.settings.muted_comment_keywords.splice(u.settingsStore.settings.muted_comment_keywords.indexOf(t),1)},Mu,8,$u)),[[V]])]))),128))]),e("div",Zu,[s(n,{icon:"fluent:person-prohibited-20-filled",width:"24px"}),ju,s(S,{class:"ml-auto",color:"background-lighten-2",variant:"flat",onClick:o[8]||(o[8]=t=>u.settingsStore.settings.muted_niconico_user_ids.unshift(""))},{default:v(()=>[s(n,{icon:"fluent:add-12-filled",height:"17px"}),Tu]),_:1})]),e("div",zu,[(c(!0),E(U,null,k(u.settingsStore.settings.muted_niconico_user_ids,(t,a)=>(c(),E("div",{class:"muted-comment-item",key:a},[s(P,{type:"search",class:"muted-comment-item__input",color:"primary",density:"compact",variant:"outlined","hide-details":"",placeholder:"ミュートするユーザー ID を入力",modelValue:u.settingsStore.settings.muted_niconico_user_ids[a],"onUpdate:modelValue":d=>u.settingsStore.settings.muted_niconico_user_ids[a]=d},null,8,["modelValue","onUpdate:modelValue"]),b((c(),E("button",{class:"muted-comment-item__delete-button",onClick:d=>u.settingsStore.settings.muted_niconico_user_ids.splice(u.settingsStore.settings.muted_niconico_user_ids.indexOf(t),1)},Ou,8,Ru)),[[V]])]))),128))])])]),_:1})]),_:1},8,["modelValue"])}const Ku=W(lu,[["render",Hu],["__scopeId","data-v-9a8b82e1"]]);export{Ku as C,au as V};