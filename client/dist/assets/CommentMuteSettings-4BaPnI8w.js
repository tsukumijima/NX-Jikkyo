import{d as p,m as A,u as f,_ as v,r as D,o as l,k as b,h as r,b as o,w as B,c,e as u,V as g,g as F,F as E,R as C,q as V,s as w,l as n}from"./index-RSutBjZx.js";import{V as y,a}from"./VSwitch-DG1RzwSI.js";import{V as S,a as k}from"./VCard-CsW2axJi.js";import{V as U}from"./ssrBoot-B_dCEWvW.js";import{a as h,V as j}from"./VSelect-DMRqH5cC.js";const $=p({name:"CommentMuteSettings",props:{modelValue:{type:Boolean,required:!0}},emits:{"update:modelValue":e=>!0},data(){return{comment_mute_settings_modal:!1,muted_comment_keyword_match_type:[{title:"部分一致",value:"partial"},{title:"前方一致",value:"forward"},{title:"後方一致",value:"backward"},{title:"完全一致",value:"exact"},{title:"正規表現",value:"regex"}]}},computed:{...A(f)},watch:{modelValue(){this.comment_mute_settings_modal=this.modelValue},comment_mute_settings_modal(){this.$emit("update:modelValue",this.comment_mute_settings_modal)}}}),i=e=>(V("data-v-b822f2bf"),e=e(),w(),e),x=i(()=>u("span",{class:"ml-3"},"コメントのミュート設定",-1)),I={class:"px-5 pb-6"},M={class:"text-subtitle-1 d-flex align-center font-weight-bold mt-4"},Z=i(()=>u("span",{class:"ml-2"},"クイック設定",-1)),z={class:"settings__item settings__item--switch"},N=i(()=>u("label",{class:"settings__item-heading",for:"mute_nicolive_comments"}," 本家ニコニコ実況に投稿されたコメントをミュートする ",-1)),H=i(()=>u("label",{class:"settings__item-label",for:"mute_nicolive_comments"},[n(" 本家ニコニコ実況のコメントサーバーに投稿されたコメントを、一括でミュートするかを設定します。"),u("br"),n(" この設定はリアルタイム実況と過去ログ再生の両方に例外なく適用されます。 ")],-1)),L={class:"settings__item settings__item--switch"},T=i(()=>u("label",{class:"settings__item-heading",for:"mute_nxjikkyo_comments"}," NX-Jikkyo に投稿されたコメントをミュートする ",-1)),q=i(()=>u("label",{class:"settings__item-label",for:"mute_nxjikkyo_comments"},[n(" NX-Jikkyo のコメントサーバーに投稿されたコメントを、一括でミュートするかを設定します。"),u("br"),n(" この設定はリアルタイム実況と過去ログ再生の両方に例外なく適用されます。 ")],-1)),J={class:"settings__item settings__item--switch"},O=i(()=>u("label",{class:"settings__item-heading",for:"mute_vulgar_comments"}," 露骨な表現を含むコメントをミュートする ",-1)),R=i(()=>u("label",{class:"settings__item-label",for:"mute_vulgar_comments"},[n(" 性的な単語などの露骨・下品な表現を含むコメントを、一括でミュートするかを設定します。"),u("br")],-1)),X={class:"settings__item settings__item--switch"},G=i(()=>u("label",{class:"settings__item-heading",for:"mute_abusive_discriminatory_prejudiced_comments"}," ネガティブな表現、差別的な表現、政治的に偏った表現を含むコメントをミュートする ",-1)),K=i(()=>u("label",{class:"settings__item-label",for:"mute_abusive_discriminatory_prejudiced_comments"},[n(" 『死ね』『殺す』などのネガティブな表現、特定の国や人々への差別的な表現、政治的に偏った表現を含むコメントを、一括でミュートするかを設定します。"),u("br")],-1)),P={class:"settings__item settings__item--switch"},Q=i(()=>u("label",{class:"settings__item-heading",for:"mute_big_size_comments"}," 文字サイズが大きいコメントをミュートする ",-1)),W=i(()=>u("label",{class:"settings__item-label",for:"mute_big_size_comments"},[n(" 通常より大きい文字サイズで表示されるコメントを、一括でミュートするかを設定します。"),u("br"),n(" 文字サイズが大きいコメントには迷惑なコメントが多いです。基本的にはオンにしておくのがおすすめです。"),u("br")],-1)),Y={class:"settings__item settings__item--switch"},uu=i(()=>u("label",{class:"settings__item-heading",for:"mute_fixed_comments"}," 映像の上下に固定表示されるコメントをミュートする ",-1)),eu=i(()=>u("label",{class:"settings__item-label",for:"mute_fixed_comments"},[n(" 映像の上下に固定された状態で表示されるコメントを、一括でミュートするかを設定します。"),u("br"),n(" 固定表示されるコメントが煩わしい方におすすめです。"),u("br")],-1)),tu={class:"settings__item settings__item--switch"},su=i(()=>u("label",{class:"settings__item-heading",for:"mute_colored_comments"}," 色付きのコメントをミュートする ",-1)),iu=i(()=>u("label",{class:"settings__item-label",for:"mute_colored_comments"},[n(" 白以外の色で表示される色付きのコメントを、一括でミュートするかを設定します。"),u("br"),n(" この設定をオンにしておくと、目立つ色のコメントを一掃できます。"),u("br")],-1)),ou={class:"settings__item settings__item--switch"},nu=i(()=>u("label",{class:"settings__item-heading",for:"mute_consecutive_same_characters_comments"}," 8文字以上同じ文字が連続しているコメントをミュートする ",-1)),mu=i(()=>u("label",{class:"settings__item-label",for:"mute_consecutive_same_characters_comments"},[n(" 『wwwwwwwwwww』『あばばばばばばばばば』など、8文字以上同じ文字が連続しているコメントを、一括でミュートするかを設定します。"),u("br"),n(" しばしばあるテンプレコメントが煩わしい方におすすめです。"),u("br")],-1)),lu={class:"text-subtitle-1 d-flex align-center font-weight-bold mt-4"},au=i(()=>u("span",{class:"ml-2 mr-2"},"ミュート済みのキーワード",-1)),du=i(()=>u("span",{class:"ml-1"},"追加",-1)),_u={class:"muted-comment-items"},cu=["onClick"],ru=i(()=>u("svg",{class:"iconify iconify--fluent",width:"20px",height:"20px",viewBox:"0 0 16 16"},[u("path",{fill:"currentColor",d:"M7 3h2a1 1 0 0 0-2 0ZM6 3a2 2 0 1 1 4 0h4a.5.5 0 0 1 0 1h-.564l-1.205 8.838A2.5 2.5 0 0 1 9.754 15H6.246a2.5 2.5 0 0 1-2.477-2.162L2.564 4H2a.5.5 0 0 1 0-1h4Zm1 3.5a.5.5 0 0 0-1 0v5a.5.5 0 0 0 1 0v-5ZM9.5 6a.5.5 0 0 0-.5.5v5a.5.5 0 0 0 1 0v-5a.5.5 0 0 0-.5-.5Z"})],-1)),Bu=[ru],Cu={class:"text-subtitle-1 d-flex align-center font-weight-bold mt-4"},gu=i(()=>u("span",{class:"ml-2 mr-2"},"ミュート済みのユーザー ID",-1)),Fu=i(()=>u("span",{class:"ml-1"},"追加",-1)),Eu={class:"muted-comment-items"},hu=["onClick"],pu=i(()=>u("svg",{class:"iconify iconify--fluent",width:"20px",height:"20px",viewBox:"0 0 16 16"},[u("path",{fill:"currentColor",d:"M7 3h2a1 1 0 0 0-2 0ZM6 3a2 2 0 1 1 4 0h4a.5.5 0 0 1 0 1h-.564l-1.205 8.838A2.5 2.5 0 0 1 9.754 15H6.246a2.5 2.5 0 0 1-2.477-2.162L2.564 4H2a.5.5 0 0 1 0-1h4Zm1 3.5a.5.5 0 0 0-1 0v5a.5.5 0 0 0 1 0v-5ZM9.5 6a.5.5 0 0 0-.5.5v5a.5.5 0 0 0 1 0v-5a.5.5 0 0 0-.5-.5Z"})],-1)),Au=[pu];function fu(e,t,vu,Du,bu,Vu){const d=D("Icon");return l(),b(y,{"max-width":"770",transition:"slide-y-transition",modelValue:e.comment_mute_settings_modal,"onUpdate:modelValue":t[11]||(t[11]=s=>e.comment_mute_settings_modal=s)},{default:r(()=>[o(k,{class:"comment-mute-settings"},{default:r(()=>[o(S,{class:"px-5 pt-6 pb-3 d-flex align-center font-weight-bold",style:{height:"60px"}},{default:r(()=>[o(d,{icon:"heroicons-solid:filter",height:"26px"}),x,o(U),B((l(),c("div",{class:"d-flex align-center rounded-circle cursor-pointer px-2 py-2",onClick:t[0]||(t[0]=s=>e.comment_mute_settings_modal=!1)},[o(d,{icon:"fluent:dismiss-12-filled",width:"23px",height:"23px"})])),[[C]])]),_:1}),u("div",I,[u("div",M,[o(d,{icon:"fa-solid:sliders-h",width:"24px",height:"20px"}),Z]),u("div",z,[N,H,o(a,{class:"settings__item-switch",color:"primary",id:"mute_nicolive_comments","hide-details":"",modelValue:e.settingsStore.settings.mute_nicolive_comments,"onUpdate:modelValue":t[1]||(t[1]=s=>e.settingsStore.settings.mute_nicolive_comments=s)},null,8,["modelValue"])]),u("div",L,[T,q,o(a,{class:"settings__item-switch",color:"primary",id:"mute_nxjikkyo_comments","hide-details":"",modelValue:e.settingsStore.settings.mute_nxjikkyo_comments,"onUpdate:modelValue":t[2]||(t[2]=s=>e.settingsStore.settings.mute_nxjikkyo_comments=s)},null,8,["modelValue"])]),u("div",J,[O,R,o(a,{class:"settings__item-switch",color:"primary",id:"mute_vulgar_comments","hide-details":"",modelValue:e.settingsStore.settings.mute_vulgar_comments,"onUpdate:modelValue":t[3]||(t[3]=s=>e.settingsStore.settings.mute_vulgar_comments=s)},null,8,["modelValue"])]),u("div",X,[G,K,o(a,{class:"settings__item-switch",color:"primary",id:"mute_abusive_discriminatory_prejudiced_comments","hide-details":"",modelValue:e.settingsStore.settings.mute_abusive_discriminatory_prejudiced_comments,"onUpdate:modelValue":t[4]||(t[4]=s=>e.settingsStore.settings.mute_abusive_discriminatory_prejudiced_comments=s)},null,8,["modelValue"])]),u("div",P,[Q,W,o(a,{class:"settings__item-switch",color:"primary",id:"mute_big_size_comments","hide-details":"",modelValue:e.settingsStore.settings.mute_big_size_comments,"onUpdate:modelValue":t[5]||(t[5]=s=>e.settingsStore.settings.mute_big_size_comments=s)},null,8,["modelValue"])]),u("div",Y,[uu,eu,o(a,{class:"settings__item-switch",color:"primary",id:"mute_fixed_comments","hide-details":"",modelValue:e.settingsStore.settings.mute_fixed_comments,"onUpdate:modelValue":t[6]||(t[6]=s=>e.settingsStore.settings.mute_fixed_comments=s)},null,8,["modelValue"])]),u("div",tu,[su,iu,o(a,{class:"settings__item-switch",color:"primary",id:"mute_colored_comments","hide-details":"",modelValue:e.settingsStore.settings.mute_colored_comments,"onUpdate:modelValue":t[7]||(t[7]=s=>e.settingsStore.settings.mute_colored_comments=s)},null,8,["modelValue"])]),u("div",ou,[nu,mu,o(a,{class:"settings__item-switch",color:"primary",id:"mute_consecutive_same_characters_comments","hide-details":"",modelValue:e.settingsStore.settings.mute_consecutive_same_characters_comments,"onUpdate:modelValue":t[8]||(t[8]=s=>e.settingsStore.settings.mute_consecutive_same_characters_comments=s)},null,8,["modelValue"])]),u("div",lu,[o(d,{icon:"fluent:comment-dismiss-20-filled",width:"24px"}),au,o(g,{class:"ml-auto",color:"background-lighten-2",variant:"flat",onClick:t[9]||(t[9]=s=>e.settingsStore.settings.muted_comment_keywords.unshift({match:"partial",pattern:""}))},{default:r(()=>[o(d,{icon:"fluent:add-12-filled",height:"17px"}),du]),_:1})]),u("div",_u,[(l(!0),c(E,null,F(e.settingsStore.settings.muted_comment_keywords,(s,m)=>(l(),c("div",{class:"muted-comment-item",key:m},[o(h,{type:"search",class:"muted-comment-item__input",color:"primary",density:"compact",variant:"outlined","hide-details":"",placeholder:"ミュートするキーワードを入力",modelValue:e.settingsStore.settings.muted_comment_keywords[m].pattern,"onUpdate:modelValue":_=>e.settingsStore.settings.muted_comment_keywords[m].pattern=_},null,8,["modelValue","onUpdate:modelValue"]),o(j,{class:"muted-comment-item__match-type",color:"primary",density:"compact",variant:"outlined","hide-details":"",items:e.muted_comment_keyword_match_type,modelValue:e.settingsStore.settings.muted_comment_keywords[m].match,"onUpdate:modelValue":_=>e.settingsStore.settings.muted_comment_keywords[m].match=_},null,8,["items","modelValue","onUpdate:modelValue"]),B((l(),c("button",{class:"muted-comment-item__delete-button",onClick:_=>e.settingsStore.settings.muted_comment_keywords.splice(e.settingsStore.settings.muted_comment_keywords.indexOf(s),1)},Bu,8,cu)),[[C]])]))),128))]),u("div",Cu,[o(d,{icon:"fluent:person-prohibited-20-filled",width:"24px"}),gu,o(g,{class:"ml-auto",color:"background-lighten-2",variant:"flat",onClick:t[10]||(t[10]=s=>e.settingsStore.settings.muted_niconico_user_ids.unshift(""))},{default:r(()=>[o(d,{icon:"fluent:add-12-filled",height:"17px"}),Fu]),_:1})]),u("div",Eu,[(l(!0),c(E,null,F(e.settingsStore.settings.muted_niconico_user_ids,(s,m)=>(l(),c("div",{class:"muted-comment-item",key:m},[o(h,{type:"search",class:"muted-comment-item__input",color:"primary",density:"compact",variant:"outlined","hide-details":"",placeholder:"ミュートするユーザー ID を入力",modelValue:e.settingsStore.settings.muted_niconico_user_ids[m],"onUpdate:modelValue":_=>e.settingsStore.settings.muted_niconico_user_ids[m]=_},null,8,["modelValue","onUpdate:modelValue"]),B((l(),c("button",{class:"muted-comment-item__delete-button",onClick:_=>e.settingsStore.settings.muted_niconico_user_ids.splice(e.settingsStore.settings.muted_niconico_user_ids.indexOf(s),1)},Au,8,hu)),[[C]])]))),128))])])]),_:1})]),_:1},8,["modelValue"])}const ju=v($,[["render",fu],["__scopeId","data-v-b822f2bf"]]);export{ju as C};