import{d as Ee,m as Se,Y as Ae,u as ye,E as W,c9 as Ve,ca as we,J as n,cb as ie,cc as te,bC as x,bv as oe,x as ee,cd as De,a0 as xe,ce as fe,G as _e,I as le,R as be,aV as Ce,cf as Te,cg as Me,c6 as se,ch as q,a,w as ue,bm as Pe,v as ze,ci as Re,cj as Ne,ck as re,c4 as Le,F as Ie,b4 as $e,_ as Ue,r as Z,o as de,j as qe,g as ce,b as l,c as Oe,V as je,n as Ke,p as Je,q as Ye,k as T}from"./index-BaStaaT9.js";import{C as Xe}from"./CommentMuteSettings-8pEd2o8i.js";import{S as Ge}from"./Base-ByFOMNoQ.js";import{l as We,n as He,m as Qe,u as Ze,f as me,o as eu}from"./VSelect-BPcsEtxq.js";import{a as uu}from"./VSwitch-DlT-cHsU.js";import"./VCard-CUMrIyiv.js";import"./ssrBoot-CaVSYxv9.js";import"./VAvatar-QKVU0Wtb.js";import"./Navigation-D_QnHcrb.js";const tu=Ee({name:"Settings-Jikkyo",components:{SettingsBase:Ge,CommentMuteSettings:Xe},data(){return{comment_mute_settings_modal:!1,is_loading:!0}},computed:{...Se(ye,Ae)},async created(){await this.userStore.fetchUser(),this.is_loading=!1}}),ae=Symbol.for("vuetify:v-slider");function lu(e,u,s){const r=s==="vertical",d=u.getBoundingClientRect(),h="touches"in e?e.touches[0]:e;return r?h.clientY-(d.top+d.height/2):h.clientX-(d.left+d.width/2)}function su(e,u){return"touches"in e&&e.touches.length?e.touches[0][u]:"changedTouches"in e&&e.changedTouches.length?e.changedTouches[0][u]:e[u]}const au=W({disabled:{type:Boolean,default:null},error:Boolean,readonly:{type:Boolean,default:null},max:{type:[Number,String],default:100},min:{type:[Number,String],default:0},step:{type:[Number,String],default:0},thumbColor:String,thumbLabel:{type:[Boolean,String],default:void 0,validator:e=>typeof e=="boolean"||e==="always"},thumbSize:{type:[Number,String],default:20},showTicks:{type:[Boolean,String],default:!1,validator:e=>typeof e=="boolean"||e==="always"},ticks:{type:[Array,Object]},tickSize:{type:[Number,String],default:2},color:String,trackColor:String,trackFillColor:String,trackSize:{type:[Number,String],default:4},direction:{type:String,default:"horizontal",validator:e=>["vertical","horizontal"].includes(e)},reverse:Boolean,...Ve(),...we({elevation:2}),ripple:{type:Boolean,default:!0}},"Slider"),nu=e=>{const u=n(()=>parseFloat(e.min)),s=n(()=>parseFloat(e.max)),r=n(()=>+e.step>0?parseFloat(e.step):0),d=n(()=>Math.max(ie(r.value),ie(u.value)));function h(v){if(v=parseFloat(v),r.value<=0)return v;const c=fe(v,u.value,s.value),g=u.value%r.value,o=Math.round((c-g)/r.value)*r.value+g;return parseFloat(Math.min(o,s.value).toFixed(d.value))}return{min:u,max:s,step:r,decimals:d,roundValue:h}},iu=e=>{let{props:u,steps:s,onSliderStart:r,onSliderMove:d,onSliderEnd:h,getActiveThumb:v}=e;const{isRtl:c}=te(),g=x(u,"reverse"),o=n(()=>u.direction==="vertical"),y=n(()=>o.value!==g.value),{min:B,max:k,step:V,decimals:N,roundValue:P}=s,$=n(()=>parseInt(u.thumbSize,10)),L=n(()=>parseInt(u.tickSize,10)),z=n(()=>parseInt(u.trackSize,10)),w=n(()=>(k.value-B.value)/V.value),U=x(u,"disabled"),D=n(()=>u.error||u.disabled?void 0:u.thumbColor??u.color),m=n(()=>u.error||u.disabled?void 0:u.trackColor??u.color),E=n(()=>u.error||u.disabled?void 0:u.trackFillColor??u.color),b=oe(!1),C=oe(0),S=ee(),A=ee();function i(t){var ne;const _=u.direction==="vertical",he=_?"top":"left",ge=_?"height":"width",Be=_?"clientY":"clientX",{[he]:Fe,[ge]:pe}=(ne=S.value)==null?void 0:ne.$el.getBoundingClientRect(),ke=su(t,Be);let Q=Math.min(Math.max((ke-Fe-C.value)/pe,0),1)||0;return(_?y.value:y.value!==c.value)&&(Q=1-Q),P(B.value+Q*(k.value-B.value))}const R=t=>{h({value:i(t)}),b.value=!1,C.value=0},I=t=>{A.value=v(t),A.value&&(A.value.focus(),b.value=!0,A.value.contains(t.target)?C.value=lu(t,A.value,u.direction):(C.value=0,d({value:i(t)})),r({value:i(t)}))},p={passive:!0,capture:!0};function O(t){d({value:i(t)})}function J(t){t.stopPropagation(),t.preventDefault(),R(t),window.removeEventListener("mousemove",O,p),window.removeEventListener("mouseup",J)}function Y(t){var _;R(t),window.removeEventListener("touchmove",O,p),(_=t.target)==null||_.removeEventListener("touchend",Y)}function H(t){var _;I(t),window.addEventListener("touchmove",O,p),(_=t.target)==null||_.addEventListener("touchend",Y,{passive:!1})}function F(t){t.preventDefault(),I(t),window.addEventListener("mousemove",O,p),window.addEventListener("mouseup",J,{passive:!1})}const f=t=>{const _=(t-B.value)/(k.value-B.value)*100;return fe(isNaN(_)?0:_,0,100)},j=x(u,"showTicks"),K=n(()=>j.value?u.ticks?Array.isArray(u.ticks)?u.ticks.map(t=>({value:t,position:f(t),label:t.toString()})):Object.keys(u.ticks).map(t=>({value:parseFloat(t),position:f(parseFloat(t)),label:u.ticks[t]})):w.value!==1/0?De(w.value+1).map(t=>{const _=B.value+t*V.value;return{value:_,position:f(_)}}):[]:[]),X=n(()=>K.value.some(t=>{let{label:_}=t;return!!_})),G={activeThumbRef:A,color:x(u,"color"),decimals:N,disabled:U,direction:x(u,"direction"),elevation:x(u,"elevation"),hasLabels:X,isReversed:g,indexFromEnd:y,min:B,max:k,mousePressed:b,numTicks:w,onSliderMousedown:F,onSliderTouchstart:H,parsedTicks:K,parseMouseMove:i,position:f,readonly:x(u,"readonly"),rounded:x(u,"rounded"),roundValue:P,showTicks:j,startOffset:C,step:V,thumbSize:$,thumbColor:D,thumbLabel:x(u,"thumbLabel"),ticks:x(u,"ticks"),tickSize:L,trackColor:m,trackContainerRef:S,trackFillColor:E,trackSize:z,vertical:o};return xe(ae,G),G},ou=W({focused:Boolean,max:{type:Number,required:!0},min:{type:Number,required:!0},modelValue:{type:Number,required:!0},position:{type:Number,required:!0},ripple:{type:[Boolean,Object],default:!0},name:String,..._e()},"VSliderThumb"),ru=le()({name:"VSliderThumb",directives:{Ripple:be},props:ou(),emits:{"update:modelValue":e=>!0},setup(e,u){let{slots:s,emit:r}=u;const d=Ce(ae),{isRtl:h,rtlClasses:v}=te();if(!d)throw new Error("[Vuetify] v-slider-thumb must be used inside v-slider or v-range-slider");const{thumbColor:c,step:g,disabled:o,thumbSize:y,thumbLabel:B,direction:k,isReversed:V,vertical:N,readonly:P,elevation:$,mousePressed:L,decimals:z,indexFromEnd:w}=d,U=n(()=>o.value?void 0:$.value),{elevationClasses:D}=Te(U),{textColorClasses:m,textColorStyles:E}=Me(c),{pageup:b,pagedown:C,end:S,home:A,left:i,right:R,down:I,up:p}=Re,O=[b,C,S,A,i,R,I,p],J=n(()=>g.value?[1,2,3]:[1,5,10]);function Y(F,f){if(!O.includes(F.key))return;F.preventDefault();const j=g.value||.1,K=(e.max-e.min)/j;if([i,R,I,p].includes(F.key)){const G=(N.value?[h.value?i:R,V.value?I:p]:w.value!==h.value?[i,p]:[R,p]).includes(F.key)?1:-1,t=F.shiftKey?2:F.ctrlKey?1:0;f=f+G*j*J.value[t]}else if(F.key===A)f=e.min;else if(F.key===S)f=e.max;else{const X=F.key===C?1:-1;f=f-X*j*(K>100?K/10:10)}return Math.max(e.min,Math.min(e.max,f))}function H(F){const f=Y(F,e.modelValue);f!=null&&r("update:modelValue",f)}return se(()=>{const F=q(w.value?100-e.position:e.position,"%");return a("div",{class:["v-slider-thumb",{"v-slider-thumb--focused":e.focused,"v-slider-thumb--pressed":e.focused&&L.value},e.class,v.value],style:[{"--v-slider-thumb-position":F,"--v-slider-thumb-size":q(y.value)},e.style],role:"slider",tabindex:o.value?-1:0,"aria-label":e.name,"aria-valuemin":e.min,"aria-valuemax":e.max,"aria-valuenow":e.modelValue,"aria-readonly":!!P.value,"aria-orientation":k.value,onKeydown:P.value?void 0:H},[a("div",{class:["v-slider-thumb__surface",m.value,D.value],style:{...E.value}},null),ue(a("div",{class:["v-slider-thumb__ripple",m.value],style:E.value},null),[[Pe("ripple"),e.ripple,null,{circle:!0,center:!0}]]),a(We,{origin:"bottom center"},{default:()=>{var f;return[ue(a("div",{class:"v-slider-thumb__label-container"},[a("div",{class:["v-slider-thumb__label"]},[a("div",null,[((f=s["thumb-label"])==null?void 0:f.call(s,{modelValue:e.modelValue}))??e.modelValue.toFixed(g.value?z.value:1)])])]),[[ze,B.value&&e.focused||B.value==="always"]])]}})])}),{}}}),du=W({start:{type:Number,required:!0},stop:{type:Number,required:!0},..._e()},"VSliderTrack"),cu=le()({name:"VSliderTrack",props:du(),emits:{},setup(e,u){let{slots:s}=u;const r=Ce(ae);if(!r)throw new Error("[Vuetify] v-slider-track must be inside v-slider or v-range-slider");const{color:d,parsedTicks:h,rounded:v,showTicks:c,tickSize:g,trackColor:o,trackFillColor:y,trackSize:B,vertical:k,min:V,max:N,indexFromEnd:P}=r,{roundedClasses:$}=Ne(v),{backgroundColorClasses:L,backgroundColorStyles:z}=re(y),{backgroundColorClasses:w,backgroundColorStyles:U}=re(o),D=n(()=>`inset-${k.value?"block":"inline"}-${P.value?"end":"start"}`),m=n(()=>k.value?"height":"width"),E=n(()=>({[D.value]:"0%",[m.value]:"100%"})),b=n(()=>e.stop-e.start),C=n(()=>({[D.value]:q(e.start,"%"),[m.value]:q(b.value,"%")})),S=n(()=>c.value?(k.value?h.value.slice().reverse():h.value).map((i,R)=>{var p;const I=i.value!==V.value&&i.value!==N.value?q(i.position,"%"):void 0;return a("div",{key:i.value,class:["v-slider-track__tick",{"v-slider-track__tick--filled":i.position>=e.start&&i.position<=e.stop,"v-slider-track__tick--first":i.value===V.value,"v-slider-track__tick--last":i.value===N.value}],style:{[D.value]:I}},[(i.label||s["tick-label"])&&a("div",{class:"v-slider-track__tick-label"},[((p=s["tick-label"])==null?void 0:p.call(s,{tick:i,index:R}))??i.label])])}):[]);return se(()=>a("div",{class:["v-slider-track",$.value,e.class],style:[{"--v-slider-track-size":q(B.value),"--v-slider-tick-size":q(g.value)},e.style]},[a("div",{class:["v-slider-track__background",w.value,{"v-slider-track__background--opacity":!!d.value||!y.value}],style:{...E.value,...U.value}},null),a("div",{class:["v-slider-track__fill",L.value],style:{...C.value,...z.value}},null),c.value&&a("div",{class:["v-slider-track__ticks",{"v-slider-track__ticks--always-show":c.value==="always"}]},[S.value])])),{}}}),mu=W({...He(),...au(),...Qe(),modelValue:{type:[Number,String],default:0}},"VSlider"),ve=le()({name:"VSlider",props:mu(),emits:{"update:focused":e=>!0,"update:modelValue":e=>!0,start:e=>!0,end:e=>!0},setup(e,u){let{slots:s,emit:r}=u;const d=ee(),{rtlClasses:h}=te(),v=nu(e),c=Le(e,"modelValue",void 0,m=>v.roundValue(m??v.min.value)),{min:g,max:o,mousePressed:y,roundValue:B,onSliderMousedown:k,onSliderTouchstart:V,trackContainerRef:N,position:P,hasLabels:$,readonly:L}=iu({props:e,steps:v,onSliderStart:()=>{r("start",c.value)},onSliderEnd:m=>{let{value:E}=m;const b=B(E);c.value=b,r("end",b)},onSliderMove:m=>{let{value:E}=m;return c.value=B(E)},getActiveThumb:()=>{var m;return(m=d.value)==null?void 0:m.$el}}),{isFocused:z,focus:w,blur:U}=Ze(e),D=n(()=>P(c.value));return se(()=>{const m=me.filterProps(e),E=!!(e.label||s.label||s.prepend);return a(me,$e({class:["v-slider",{"v-slider--has-labels":!!s["tick-label"]||$.value,"v-slider--focused":z.value,"v-slider--pressed":y.value,"v-slider--disabled":e.disabled},h.value,e.class],style:e.style},m,{focused:z.value}),{...s,prepend:E?b=>{var C,S;return a(Ie,null,[((C=s.label)==null?void 0:C.call(s,b))??(e.label?a(eu,{id:b.id.value,class:"v-slider__label",text:e.label},null):void 0),(S=s.prepend)==null?void 0:S.call(s,b)])}:void 0,default:b=>{let{id:C,messagesId:S}=b;return a("div",{class:"v-slider__container",onMousedown:L.value?void 0:k,onTouchstartPassive:L.value?void 0:V},[a("input",{id:C.value,name:e.name||C.value,disabled:!!e.disabled,readonly:!!e.readonly,tabindex:"-1",value:c.value},null),a(cu,{ref:N,start:0,stop:D.value},{"tick-label":s["tick-label"]}),a(ru,{ref:d,"aria-describedby":S.value,focused:z.value,min:g.value,max:o.value,modelValue:c.value,"onUpdate:modelValue":A=>c.value=A,position:D.value,elevation:e.elevation,onFocus:w,onBlur:U,ripple:e.ripple,name:e.name},{"thumb-label":s["thumb-label"]})])}})}),{}}}),M=e=>(Je("data-v-866df850"),e=e(),Ye(),e),vu={class:"settings__heading"},fu=M(()=>l("span",{class:"ml-3"},"コメント/実況",-1)),_u=M(()=>l("div",{class:"settings__item-label mt-0",style:{"border-left":"3px solid rgb(var(--v-theme-text-darken-1))","padding-left":"12px"}},[T(" コメントの透明度は、コメントプレイヤー下にある設定アイコン ⚙️ から変更できます。"),l("br")],-1)),bu=M(()=>l("div",{class:"settings__item"},[l("div",{class:"settings__item-heading"},"コメントのミュート設定"),l("div",{class:"settings__item-label"},[T(" 表示したくないコメントを、映像上やコメントリストに表示しないようにミュートできます。"),l("br")]),l("div",{class:"settings__item-label mt-2"},[T(" デフォルトでは、下記のミュート設定がオンになっています。"),l("br"),T(" これらのコメントも表示したい方は、適宜オフに設定してください。"),l("br"),l("ul",{class:"ml-5 mt-2"},[l("li",null,"露骨な表現を含むコメントをミュートする"),l("li",null,"ネガティブな表現、差別的な表現、政治的に偏った表現を含むコメントをミュートする"),l("li",null,"文字サイズが大きいコメントをミュートする")])])],-1)),Cu=M(()=>l("span",{class:"ml-1"},"コメントのミュート設定を開く",-1)),hu={class:"settings__item"},gu=M(()=>l("div",{class:"settings__item-heading"},"コメントの速さ",-1)),Bu=M(()=>l("div",{class:"settings__item-label"},[T(" プレイヤーに流れるコメントの速さを設定します。"),l("br"),T(" たとえば 1.2 に設定すると、コメントが 1.2 倍速く流れます。"),l("br")],-1)),Fu={class:"settings__item"},pu=M(()=>l("div",{class:"settings__item-heading"},"コメントの文字サイズ",-1)),ku=M(()=>l("div",{class:"settings__item-label"},[T(" プレイヤーに流れるコメントの文字サイズの基準値を設定します。"),l("br"),T(" 実際の文字サイズは画面サイズに合わせて調整されます。デフォルトの文字サイズは 34px です。"),l("br")],-1)),Eu={class:"settings__item settings__item--switch"},Su=M(()=>l("label",{class:"settings__item-heading",for:"close_comment_form_after_sending"},"コメント送信後にコメント入力フォームを閉じる",-1)),Au=M(()=>l("label",{class:"settings__item-label",for:"close_comment_form_after_sending"},[T(" この設定をオンにすると、コメントを送信した後に、コメント入力フォームが自動で閉じるようになります。"),l("br"),T(" なお、コメント入力フォームが表示されたままだと、大半のショートカットキーが文字入力と競合して使えなくなります。ショートカットキーを頻繁に使う方はオンにしておくのがおすすめです。"),l("br")],-1));function yu(e,u,s,r,d,h){const v=Z("Icon"),c=Z("CommentMuteSettings"),g=Z("SettingsBase");return de(),qe(g,null,{default:ce(()=>[l("h2",vu,[ue((de(),Oe("a",{class:"settings__back-button",onClick:u[0]||(u[0]=o=>e.$router.back())},[a(v,{icon:"fluent:arrow-left-12-filled",width:"25px"})])),[[be]]),a(v,{icon:"bi:chat-left-text-fill",width:"19px"}),fu]),l("div",{class:Ke(["settings__content",{"settings__content--loading":e.is_loading}])},[_u,bu,a(je,{class:"settings__save-button mt-4",variant:"flat",onClick:u[1]||(u[1]=o=>e.comment_mute_settings_modal=!e.comment_mute_settings_modal)},{default:ce(()=>[a(v,{icon:"heroicons-solid:filter",height:"19px"}),Cu]),_:1}),l("div",hu,[gu,Bu,a(ve,{class:"settings__item-form",color:"primary","show-ticks":"always","thumb-label":"","hide-details":"",step:.1,min:.5,max:2,modelValue:e.settingsStore.settings.comment_speed_rate,"onUpdate:modelValue":u[2]||(u[2]=o=>e.settingsStore.settings.comment_speed_rate=o)},null,8,["modelValue"])]),l("div",Fu,[pu,ku,a(ve,{class:"settings__item-form",color:"primary","show-ticks":"always","thumb-label":"","hide-details":"",step:1,min:20,max:60,modelValue:e.settingsStore.settings.comment_font_size,"onUpdate:modelValue":u[3]||(u[3]=o=>e.settingsStore.settings.comment_font_size=o)},null,8,["modelValue"])]),l("div",Eu,[Su,Au,a(uu,{class:"settings__item-switch",color:"primary",id:"close_comment_form_after_sending","hide-details":"",modelValue:e.settingsStore.settings.close_comment_form_after_sending,"onUpdate:modelValue":u[4]||(u[4]=o=>e.settingsStore.settings.close_comment_form_after_sending=o)},null,8,["modelValue"])])],2),a(c,{modelValue:e.comment_mute_settings_modal,"onUpdate:modelValue":u[5]||(u[5]=o=>e.comment_mute_settings_modal=o)},null,8,["modelValue"])]),_:1})}const Nu=Ue(tu,[["render",yu],["__scopeId","data-v-866df850"]]);export{Nu as default};
