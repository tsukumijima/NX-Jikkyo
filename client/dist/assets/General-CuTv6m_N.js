import{d as ru,U as E,m as du,M as g,u as cu,x as _u,a2 as H,A as Cu,a3 as Bu,a4 as mu,B as _,a5 as O,W as y,N as Fu,a6 as gu,a7 as Au,a as i,a8 as b,F as S,a1 as pu,a9 as vu,_ as Du,r as M,o as T,i as fu,g as p,b as e,w as hu,c as Eu,t as q,j as o,V as k,R as yu}from"./index-Dp96uVM_.js";import{S as bu}from"./Base-CXwwOogJ.js";import{m as Su,c as ku,u as Vu,d as J,f as wu,e as Iu,g as Pu,h as $u,i as Ru,j as X,k as x,l as G}from"./VSwitch-Bnkqduh8.js";import"./Navigation-BzOaQlv4.js";import"./ssrBoot-ZsjtgShn.js";import"./VAvatar-DTmbaPuY.js";const zu=ru({name:"Settings-General",components:{SettingsBase:bu},data(){return{Utils:Object.freeze(E),is_form_dense:E.isSmartphoneHorizontal(),pinned_channel_settings_modal:!1,panel_display_state:[{title:"前回の状態を復元する",value:"RestorePreviousState"},{title:"常に表示する",value:"AlwaysDisplay"},{title:"常に折りたたむ",value:"AlwaysFold"}],tv_panel_active_tab:[{title:"番組情報タブ",value:"Program"},{title:"チャンネルタブ",value:"Channel"},{title:"コメントタブ",value:"Comment"}],video_panel_active_tab:[{title:"番組情報タブ",value:"RecordedProgram"},{title:"シリーズタブ",value:"Series"},{title:"コメントタブ",value:"Comment"},{title:"Twitter タブ",value:"Twitter"}],import_settings_file:[]}},computed:{...du(cu)},methods:{exportSettings(){const u=JSON.stringify(this.settingsStore.settings,null,4),s=new Blob([u],{type:"application/json"});E.downloadBlobData(s,"NX-Jikkyo-Settings.json"),g.success("設定をエクスポートしました。")},async importSettings(){if(this.import_settings_file.length===0){g.error("インポートする設定データを選択してください！");return}await this.settingsStore.importClientSettings(this.import_settings_file[0])===!0?(g.success("設定をインポートしました。"),window.setTimeout(()=>this.$router.go(0),300)):g.error("設定データが不正なため、インポートできませんでした。")},async resetSettings(){await this.settingsStore.resetClientSettings(),g.success("設定をリセットしました。"),window.setTimeout(()=>this.$router.go(0),300)}}}),ju=_u({chips:Boolean,counter:Boolean,counterSizeString:{type:String,default:"$vuetify.fileInput.counterSize"},counterString:{type:String,default:"$vuetify.fileInput.counter"},multiple:Boolean,showSize:{type:[Boolean,Number,String],default:!1,validator:u=>typeof u=="boolean"||[1e3,1024].includes(Number(u))},...Su({prependIcon:"$file"}),modelValue:{type:[Array,Object],default:u=>u.multiple?[]:null,validator:u=>H(u).every(s=>s!=null&&typeof s=="object")},...ku({clearable:!0})},"VFileInput"),Nu=Cu()({name:"VFileInput",inheritAttrs:!1,props:ju(),emits:{"click:control":u=>!0,"mousedown:control":u=>!0,"update:focused":u=>!0,"update:modelValue":u=>!0},setup(u,s){let{attrs:V,emit:v,slots:r}=s;const{t:D}=Bu(),l=mu(u,"modelValue",u.modelValue,t=>H(t),t=>u.multiple||Array.isArray(u.modelValue)?t:t[0]),{isFocused:C,focus:a,blur:L}=Vu(u),w=_(()=>typeof u.showSize!="boolean"?u.showSize:void 0),I=_(()=>(l.value??[]).reduce((t,n)=>{let{size:B=0}=n;return t+B},0)),P=_(()=>O(I.value,w.value)),f=_(()=>(l.value??[]).map(t=>{const{name:n="",size:B=0}=t;return u.showSize?`${n} (${O(B,w.value)})`:n})),W=_(()=>{var n;const t=((n=l.value)==null?void 0:n.length)??0;return u.showSize?D(u.counterSizeString,t,P.value):D(u.counterString,t)}),$=y(),R=y(),d=y(),K=_(()=>C.value||u.active),z=_(()=>["plain","underlined"].includes(u.variant));function h(){var t;d.value!==document.activeElement&&((t=d.value)==null||t.focus()),C.value||a()}function Q(t){var n;(n=d.value)==null||n.click()}function Y(t){v("mousedown:control",t)}function Z(t){var n;(n=d.value)==null||n.click(),v("click:control",t)}function uu(t){t.stopPropagation(),h(),pu(()=>{l.value=[],vu(u["onClick:clear"],t)})}return Fu(l,t=>{(!Array.isArray(t)||!t.length)&&d.value&&(d.value.value="")}),gu(()=>{const t=!!(r.counter||u.counter),n=!!(t||r.details),[B,eu]=Au(V),{modelValue:ae,...tu}=J.filterProps(u),su=wu(u);return i(J,b({ref:$,modelValue:l.value,"onUpdate:modelValue":m=>l.value=m,class:["v-file-input",{"v-file-input--chips":!!u.chips,"v-input--plain-underlined":z.value},u.class],style:u.style,"onClick:prepend":Q},B,tu,{centerAffix:!z.value,focused:C.value}),{...r,default:m=>{let{id:A,isDisabled:F,isDirty:j,isReadonly:N,isValid:iu}=m;return i(Iu,b({ref:R,"prepend-icon":u.prependIcon,onMousedown:Y,onClick:Z,"onClick:clear":uu,"onClick:prependInner":u["onClick:prependInner"],"onClick:appendInner":u["onClick:appendInner"]},su,{id:A.value,active:K.value||j.value,dirty:j.value,disabled:F.value,focused:C.value,error:iu.value===!1}),{...r,default:lu=>{var U;let{props:{class:nu,...au}}=lu;return i(S,null,[i("input",b({ref:d,type:"file",readonly:N.value,disabled:F.value,multiple:u.multiple,name:u.name,onClick:c=>{c.stopPropagation(),N.value&&c.preventDefault(),h()},onChange:c=>{if(!c.target)return;const ou=c.target;l.value=[...ou.files??[]]},onFocus:h,onBlur:L},au,eu),null),i("div",{class:nu},[!!((U=l.value)!=null&&U.length)&&(r.selection?r.selection({fileNames:f.value,totalBytes:I.value,totalBytesReadable:P.value}):u.chips?f.value.map(c=>i(Pu,{key:c,size:"small",text:c},null)):f.value.join(", "))])])}})},details:n?m=>{var A,F;return i(S,null,[(A=r.details)==null?void 0:A.call(r,m),t&&i(S,null,[i("span",null,null),i($u,{active:!!((F=l.value)!=null&&F.length),value:W.value},r.counter)])])}:void 0})}),Ru({},$,R,d)}}),Uu={class:"settings__heading"},Ou=e("span",{class:"ml-3"},"全般",-1),Mu={class:"settings__content"},Tu={class:"settings__item settings__item--switch"},qu=e("label",{class:"settings__item-heading",for:"show_player_background_image"},"コメントプレイヤーに背景画像を表示する",-1),Ju=e("label",{class:"settings__item-label",for:"show_player_background_image"},[o(" この設定をオンにすると、コメントプレイヤーにランダムで背景画像を表示します。"),e("br"),o(" オフにした場合は、背景画像を表示しません。"),e("br")],-1),Xu={class:"settings__item settings__item--switch"},xu={class:"settings__item-heading",for:"tv_channel_selection_requires_alt_key"},Gu={class:"settings__item-label",for:"tv_channel_selection_requires_alt_key"},Hu=e("br",null,null,-1),Lu=e("br",null,null,-1),Wu={class:"settings__item"},Ku=e("div",{class:"settings__item-heading"},"デフォルトのパネルの表示状態",-1),Qu=e("div",{class:"settings__item-label"},[o(" 実況画面を開いたときに、右側のパネルをどう表示するかを設定します。"),e("br")],-1),Yu={class:"settings__item"},Zu=e("div",{class:"settings__item-heading"},"デフォルトで表示されるパネルのタブ",-1),ue=e("div",{class:"settings__item-label"},[o(" 実況画面を開いたときに、右側のパネルで最初に表示されるタブを設定します。"),e("br")],-1),ee=e("div",{class:"settings__item"},[e("div",{class:"settings__item-heading"},"設定をエクスポート"),e("div",{class:"settings__item-label"},[o(" このデバイス (ブラウザ) に保存されている設定データを、エクスポート (ダウンロード) できます。"),e("br"),o(" ダウンロードした設定データ (NX-Jikkyo-Settings.json) は、[設定をインポート] からインポートできます。異なるサーバーの NX-Jikkyo を同じ設定で使いたいときなどに使ってください。"),e("br")])],-1),te={class:"settings__item"},se=e("div",{class:"settings__item-heading text-error-lighten-1"},"設定をインポート",-1),ie=e("div",{class:"settings__item-label"},[o(" [設定をエクスポート] でダウンロードした設定データを、このデバイス (ブラウザ) にインポートできます。"),e("br"),e("strong",{class:"text-error-lighten-1"},"設定をインポートすると、現在のデバイス設定はすべて上書きされます。元に戻すことはできません。"),e("br"),e("strong",{class:"text-error-lighten-1"},"設定のデバイス間同期がオンのときは、同期が有効なすべてのデバイスに反映されます。"),o("十分ご注意ください。"),e("br")],-1),le=e("div",{class:"settings__item"},[e("div",{class:"settings__item-heading text-error-lighten-1"},"設定を初期状態にリセット"),e("div",{class:"settings__item-label"},[o(" このデバイス (ブラウザ) に保存されている設定データを、初期状態のデフォルト値にリセットできます。"),e("br"),e("strong",{class:"text-error-lighten-1"},"設定をリセットすると、元に戻すことはできません。"),e("br"),e("strong",{class:"text-error-lighten-1"},"設定のデバイス間同期がオンのときは、同期が有効なすべてのデバイスに反映されます。"),o("十分ご注意ください。"),e("br")])],-1);function ne(u,s,V,v,r,D){const l=M("Icon"),C=M("SettingsBase");return T(),fu(C,null,{default:p(()=>[e("h2",Uu,[hu((T(),Eu("a",{class:"settings__back-button",onClick:s[0]||(s[0]=a=>u.$router.back())},[i(l,{icon:"fluent:arrow-left-12-filled",width:"25px"})])),[[yu]]),i(l,{icon:"fa-solid:sliders-h",width:"19px",style:{margin:"0 4px"}}),Ou]),e("div",Mu,[e("div",Tu,[qu,Ju,i(X,{class:"settings__item-switch",color:"primary",id:"show_player_background_image","hide-details":"",modelValue:u.settingsStore.settings.show_player_background_image,"onUpdate:modelValue":s[1]||(s[1]=a=>u.settingsStore.settings.show_player_background_image=a)},null,8,["modelValue"])]),e("div",Xu,[e("label",xu,"チャンネル選局のキーボードショートカットを "+q(u.Utils.AltOrOption())+" + 数字キー/テンキーに変更する",1),e("label",Gu,[o(" この設定をオンにすると、数字キーまたはテンキーに対応するリモコン番号（1～12）の実況チャンネルに切り替えるとき、"+q(u.Utils.AltOrOption())+" キーを同時に押す必要があります。",1),Hu,o(" コメントを入力しようとして誤って数字キーを押してしまい、チャンネルが変わってしまう事態を避けたい方におすすめです。"),Lu]),i(X,{class:"settings__item-switch",color:"primary",id:"tv_channel_selection_requires_alt_key","hide-details":"",modelValue:u.settingsStore.settings.tv_channel_selection_requires_alt_key,"onUpdate:modelValue":s[2]||(s[2]=a=>u.settingsStore.settings.tv_channel_selection_requires_alt_key=a)},null,8,["modelValue"])]),i(x,{class:"mt-6"}),e("div",Wu,[Ku,Qu,i(G,{class:"settings__item-form",color:"primary",variant:"outlined","hide-details":"",density:u.is_form_dense?"compact":"default",items:u.panel_display_state,modelValue:u.settingsStore.settings.panel_display_state,"onUpdate:modelValue":s[3]||(s[3]=a=>u.settingsStore.settings.panel_display_state=a)},null,8,["density","items","modelValue"])]),e("div",Yu,[Zu,ue,i(G,{class:"settings__item-form",color:"primary",variant:"outlined","hide-details":"",density:u.is_form_dense?"compact":"default",items:u.tv_panel_active_tab,modelValue:u.settingsStore.settings.tv_panel_active_tab,"onUpdate:modelValue":s[4]||(s[4]=a=>u.settingsStore.settings.tv_panel_active_tab=a)},null,8,["density","items","modelValue"])]),i(x,{class:"mt-6"}),ee,i(k,{class:"settings__save-button mt-4",variant:"flat",onClick:s[5]||(s[5]=a=>u.exportSettings())},{default:p(()=>[i(l,{icon:"fa6-solid:download",class:"mr-3",height:"19px"}),o("設定をエクスポート ")]),_:1}),e("div",te,[se,ie,i(Nu,{class:"settings__item-form",color:"primary",variant:"outlined","hide-details":"",label:"設定データ (NX-Jikkyo-Settings.json) を選択",density:u.is_form_dense?"compact":"default",accept:"application/json","prepend-icon":"","prepend-inner-icon":"mdi-paperclip",modelValue:u.import_settings_file,"onUpdate:modelValue":s[6]||(s[6]=a=>u.import_settings_file=a)},null,8,["density","modelValue"])]),i(k,{class:"settings__save-button bg-error mt-5",variant:"flat",onClick:s[7]||(s[7]=a=>u.importSettings())},{default:p(()=>[i(l,{icon:"fa6-solid:upload",class:"mr-3",height:"19px"}),o("設定をインポート ")]),_:1}),le,i(k,{class:"settings__save-button bg-error mt-5",variant:"flat",onClick:s[8]||(s[8]=a=>u.resetSettings())},{default:p(()=>[i(l,{icon:"material-symbols:device-reset-rounded",class:"mr-2",height:"23px"}),o("設定をリセット ")]),_:1})])]),_:1})}const Be=Du(zu,[["render",ne]]);export{Be as default};
