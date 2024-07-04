import{d as Ee,m as Se,Z as ye,u as Ae,G,c9 as Ve,ca as we,K as n,cb as ie,cc as te,bC as x,bv as oe,y as ee,cd as De,a1 as xe,ce as fe,H as _e,J as se,R as be,aW as Ce,cf as Te,cg as Me,c6 as le,ch as q,b as a,w as ue,a as Pe,v as ze,ci as Re,cj as Ne,ck as re,c4 as Le,F as Ie,b5 as $e,_ as Ue,r as Q,o as de,k as qe,h as ce,e as s,c as Ke,V as Oe,n as je,q as Je,s as We,l as T}from"./index-C8X01GMO.js";import{C as Xe}from"./CommentMuteSettings-C7xkcSno.js";import{S as Ye}from"./Base-CCa2W54u.js";import{n as Ge,o as He,m as Ze,u as Qe,f as me,p as eu}from"./VSelect-DSyKfG2h.js";import{a as uu}from"./VSwitch--6vbutr0.js";import"./VCard-BS33-G8r.js";import"./ssrBoot-DwA1YKw2.js";import"./VAvatar-DMoZa95l.js";import"./Navigation-C5dy3zOE.js";const tu=Ee({name:"Settings-Jikkyo",components:{SettingsBase:Ye,CommentMuteSettings:Xe},data(){return{comment_mute_settings_modal:!1,is_loading:!0}},computed:{...Se(Ae,ye)},async created(){await this.userStore.fetchUser(),this.is_loading=!1}}),ae=Symbol.for("vuetify:v-slider");function su(e,u,l){const r=l==="vertical",d=u.getBoundingClientRect(),h="touches"in e?e.touches[0]:e;return r?h.clientY-(d.top+d.height/2):h.clientX-(d.left+d.width/2)}function lu(e,u){return"touches"in e&&e.touches.length?e.touches[0][u]:"changedTouches"in e&&e.changedTouches.length?e.changedTouches[0][u]:e[u]}const au=G({disabled:{type:Boolean,default:null},error:Boolean,readonly:{type:Boolean,default:null},max:{type:[Number,String],default:100},min:{type:[Number,String],default:0},step:{type:[Number,String],default:0},thumbColor:String,thumbLabel:{type:[Boolean,String],default:void 0,validator:e=>typeof e=="boolean"||e==="always"},thumbSize:{type:[Number,String],default:20},showTicks:{type:[Boolean,String],default:!1,validator:e=>typeof e=="boolean"||e==="always"},ticks:{type:[Array,Object]},tickSize:{type:[Number,String],default:2},color:String,trackColor:String,trackFillColor:String,trackSize:{type:[Number,String],default:4},direction:{type:String,default:"horizontal",validator:e=>["vertical","horizontal"].includes(e)},reverse:Boolean,...Ve(),...we({elevation:2}),ripple:{type:Boolean,default:!0}},"Slider"),nu=e=>{const u=n(()=>parseFloat(e.min)),l=n(()=>parseFloat(e.max)),r=n(()=>+e.step>0?parseFloat(e.step):0),d=n(()=>Math.max(ie(r.value),ie(u.value)));function h(v){if(v=parseFloat(v),r.value<=0)return v;const c=fe(v,u.value,l.value),g=u.value%r.value,o=Math.round((c-g)/r.value)*r.value+g;return parseFloat(Math.min(o,l.value).toFixed(d.value))}return{min:u,max:l,step:r,decimals:d,roundValue:h}},iu=e=>{let{props:u,steps:l,onSliderStart:r,onSliderMove:d,onSliderEnd:h,getActiveThumb:v}=e;const{isRtl:c}=te(),g=x(u,"reverse"),o=n(()=>u.direction==="vertical"),A=n(()=>o.value!==g.value),{min:p,max:k,step:V,decimals:N,roundValue:P}=l,$=n(()=>parseInt(u.thumbSize,10)),L=n(()=>parseInt(u.tickSize,10)),z=n(()=>parseInt(u.trackSize,10)),w=n(()=>(k.value-p.value)/V.value),U=x(u,"disabled"),D=n(()=>u.error||u.disabled?void 0:u.thumbColor??u.color),m=n(()=>u.error||u.disabled?void 0:u.trackColor??u.color),E=n(()=>u.error||u.disabled?void 0:u.trackFillColor??u.color),b=oe(!1),C=oe(0),S=ee(),y=ee();function i(t){var ne;const _=u.direction==="vertical",he=_?"top":"left",ge=_?"height":"width",pe=_?"clientY":"clientX",{[he]:Be,[ge]:Fe}=(ne=S.value)==null?void 0:ne.$el.getBoundingClientRect(),ke=lu(t,pe);let Z=Math.min(Math.max((ke-Be-C.value)/Fe,0),1)||0;return(_?A.value:A.value!==c.value)&&(Z=1-Z),P(p.value+Z*(k.value-p.value))}const R=t=>{h({value:i(t)}),b.value=!1,C.value=0},I=t=>{y.value=v(t),y.value&&(y.value.focus(),b.value=!0,y.value.contains(t.target)?C.value=su(t,y.value,u.direction):(C.value=0,d({value:i(t)})),r({value:i(t)}))},F={passive:!0,capture:!0};function K(t){d({value:i(t)})}function J(t){t.stopPropagation(),t.preventDefault(),R(t),window.removeEventListener("mousemove",K,F),window.removeEventListener("mouseup",J)}function W(t){var _;R(t),window.removeEventListener("touchmove",K,F),(_=t.target)==null||_.removeEventListener("touchend",W)}function H(t){var _;I(t),window.addEventListener("touchmove",K,F),(_=t.target)==null||_.addEventListener("touchend",W,{passive:!1})}function B(t){t.preventDefault(),I(t),window.addEventListener("mousemove",K,F),window.addEventListener("mouseup",J,{passive:!1})}const f=t=>{const _=(t-p.value)/(k.value-p.value)*100;return fe(isNaN(_)?0:_,0,100)},O=x(u,"showTicks"),j=n(()=>O.value?u.ticks?Array.isArray(u.ticks)?u.ticks.map(t=>({value:t,position:f(t),label:t.toString()})):Object.keys(u.ticks).map(t=>({value:parseFloat(t),position:f(parseFloat(t)),label:u.ticks[t]})):w.value!==1/0?De(w.value+1).map(t=>{const _=p.value+t*V.value;return{value:_,position:f(_)}}):[]:[]),X=n(()=>j.value.some(t=>{let{label:_}=t;return!!_})),Y={activeThumbRef:y,color:x(u,"color"),decimals:N,disabled:U,direction:x(u,"direction"),elevation:x(u,"elevation"),hasLabels:X,isReversed:g,indexFromEnd:A,min:p,max:k,mousePressed:b,numTicks:w,onSliderMousedown:B,onSliderTouchstart:H,parsedTicks:j,parseMouseMove:i,position:f,readonly:x(u,"readonly"),rounded:x(u,"rounded"),roundValue:P,showTicks:O,startOffset:C,step:V,thumbSize:$,thumbColor:D,thumbLabel:x(u,"thumbLabel"),ticks:x(u,"ticks"),tickSize:L,trackColor:m,trackContainerRef:S,trackFillColor:E,trackSize:z,vertical:o};return xe(ae,Y),Y},ou=G({focused:Boolean,max:{type:Number,required:!0},min:{type:Number,required:!0},modelValue:{type:Number,required:!0},position:{type:Number,required:!0},ripple:{type:[Boolean,Object],default:!0},..._e()},"VSliderThumb"),ru=se()({name:"VSliderThumb",directives:{Ripple:be},props:ou(),emits:{"update:modelValue":e=>!0},setup(e,u){let{slots:l,emit:r}=u;const d=Ce(ae),{isRtl:h,rtlClasses:v}=te();if(!d)throw new Error("[Vuetify] v-slider-thumb must be used inside v-slider or v-range-slider");const{thumbColor:c,step:g,disabled:o,thumbSize:A,thumbLabel:p,direction:k,isReversed:V,vertical:N,readonly:P,elevation:$,mousePressed:L,decimals:z,indexFromEnd:w}=d,U=n(()=>o.value?void 0:$.value),{elevationClasses:D}=Te(U),{textColorClasses:m,textColorStyles:E}=Me(c),{pageup:b,pagedown:C,end:S,home:y,left:i,right:R,down:I,up:F}=Re,K=[b,C,S,y,i,R,I,F],J=n(()=>g.value?[1,2,3]:[1,5,10]);function W(B,f){if(!K.includes(B.key))return;B.preventDefault();const O=g.value||.1,j=(e.max-e.min)/O;if([i,R,I,F].includes(B.key)){const Y=(N.value?[h.value?i:R,V.value?I:F]:w.value!==h.value?[i,F]:[R,F]).includes(B.key)?1:-1,t=B.shiftKey?2:B.ctrlKey?1:0;f=f+Y*O*J.value[t]}else if(B.key===y)f=e.min;else if(B.key===S)f=e.max;else{const X=B.key===C?1:-1;f=f-X*O*(j>100?j/10:10)}return Math.max(e.min,Math.min(e.max,f))}function H(B){const f=W(B,e.modelValue);f!=null&&r("update:modelValue",f)}return le(()=>{const B=q(w.value?100-e.position:e.position,"%");return a("div",{class:["v-slider-thumb",{"v-slider-thumb--focused":e.focused,"v-slider-thumb--pressed":e.focused&&L.value},e.class,v.value],style:[{"--v-slider-thumb-position":B,"--v-slider-thumb-size":q(A.value)},e.style],role:"slider",tabindex:o.value?-1:0,"aria-valuemin":e.min,"aria-valuemax":e.max,"aria-valuenow":e.modelValue,"aria-readonly":!!P.value,"aria-orientation":k.value,onKeydown:P.value?void 0:H},[a("div",{class:["v-slider-thumb__surface",m.value,D.value],style:{...E.value}},null),ue(a("div",{class:["v-slider-thumb__ripple",m.value],style:E.value},null),[[Pe("ripple"),e.ripple,null,{circle:!0,center:!0}]]),a(Ge,{origin:"bottom center"},{default:()=>{var f;return[ue(a("div",{class:"v-slider-thumb__label-container"},[a("div",{class:["v-slider-thumb__label"]},[a("div",null,[((f=l["thumb-label"])==null?void 0:f.call(l,{modelValue:e.modelValue}))??e.modelValue.toFixed(g.value?z.value:1)])])]),[[ze,p.value&&e.focused||p.value==="always"]])]}})])}),{}}}),du=G({start:{type:Number,required:!0},stop:{type:Number,required:!0},..._e()},"VSliderTrack"),cu=se()({name:"VSliderTrack",props:du(),emits:{},setup(e,u){let{slots:l}=u;const r=Ce(ae);if(!r)throw new Error("[Vuetify] v-slider-track must be inside v-slider or v-range-slider");const{color:d,parsedTicks:h,rounded:v,showTicks:c,tickSize:g,trackColor:o,trackFillColor:A,trackSize:p,vertical:k,min:V,max:N,indexFromEnd:P}=r,{roundedClasses:$}=Ne(v),{backgroundColorClasses:L,backgroundColorStyles:z}=re(A),{backgroundColorClasses:w,backgroundColorStyles:U}=re(o),D=n(()=>`inset-${k.value?"block":"inline"}-${P.value?"end":"start"}`),m=n(()=>k.value?"height":"width"),E=n(()=>({[D.value]:"0%",[m.value]:"100%"})),b=n(()=>e.stop-e.start),C=n(()=>({[D.value]:q(e.start,"%"),[m.value]:q(b.value,"%")})),S=n(()=>c.value?(k.value?h.value.slice().reverse():h.value).map((i,R)=>{var F;const I=i.value!==V.value&&i.value!==N.value?q(i.position,"%"):void 0;return a("div",{key:i.value,class:["v-slider-track__tick",{"v-slider-track__tick--filled":i.position>=e.start&&i.position<=e.stop,"v-slider-track__tick--first":i.value===V.value,"v-slider-track__tick--last":i.value===N.value}],style:{[D.value]:I}},[(i.label||l["tick-label"])&&a("div",{class:"v-slider-track__tick-label"},[((F=l["tick-label"])==null?void 0:F.call(l,{tick:i,index:R}))??i.label])])}):[]);return le(()=>a("div",{class:["v-slider-track",$.value,e.class],style:[{"--v-slider-track-size":q(p.value),"--v-slider-tick-size":q(g.value)},e.style]},[a("div",{class:["v-slider-track__background",w.value,{"v-slider-track__background--opacity":!!d.value||!A.value}],style:{...E.value,...U.value}},null),a("div",{class:["v-slider-track__fill",L.value],style:{...C.value,...z.value}},null),c.value&&a("div",{class:["v-slider-track__ticks",{"v-slider-track__ticks--always-show":c.value==="always"}]},[S.value])])),{}}}),mu=G({...He(),...au(),...Ze(),modelValue:{type:[Number,String],default:0}},"VSlider"),ve=se()({name:"VSlider",props:mu(),emits:{"update:focused":e=>!0,"update:modelValue":e=>!0,start:e=>!0,end:e=>!0},setup(e,u){let{slots:l,emit:r}=u;const d=ee(),{rtlClasses:h}=te(),v=nu(e),c=Le(e,"modelValue",void 0,m=>v.roundValue(m??v.min.value)),{min:g,max:o,mousePressed:A,roundValue:p,onSliderMousedown:k,onSliderTouchstart:V,trackContainerRef:N,position:P,hasLabels:$,readonly:L}=iu({props:e,steps:v,onSliderStart:()=>{r("start",c.value)},onSliderEnd:m=>{let{value:E}=m;const b=p(E);c.value=b,r("end",b)},onSliderMove:m=>{let{value:E}=m;return c.value=p(E)},getActiveThumb:()=>{var m;return(m=d.value)==null?void 0:m.$el}}),{isFocused:z,focus:w,blur:U}=Qe(e),D=n(()=>P(c.value));return le(()=>{const m=me.filterProps(e),E=!!(e.label||l.label||l.prepend);return a(me,$e({class:["v-slider",{"v-slider--has-labels":!!l["tick-label"]||$.value,"v-slider--focused":z.value,"v-slider--pressed":A.value,"v-slider--disabled":e.disabled},h.value,e.class],style:e.style},m,{focused:z.value}),{...l,prepend:E?b=>{var C,S;return a(Ie,null,[((C=l.label)==null?void 0:C.call(l,b))??(e.label?a(eu,{id:b.id.value,class:"v-slider__label",text:e.label},null):void 0),(S=l.prepend)==null?void 0:S.call(l,b)])}:void 0,default:b=>{let{id:C,messagesId:S}=b;return a("div",{class:"v-slider__container",onMousedown:L.value?void 0:k,onTouchstartPassive:L.value?void 0:V},[a("input",{id:C.value,name:e.name||C.value,disabled:!!e.disabled,readonly:!!e.readonly,tabindex:"-1",value:c.value},null),a(cu,{ref:N,start:0,stop:D.value},{"tick-label":l["tick-label"]}),a(ru,{ref:d,"aria-describedby":S.value,focused:z.value,min:g.value,max:o.value,modelValue:c.value,"onUpdate:modelValue":y=>c.value=y,position:D.value,elevation:e.elevation,onFocus:w,onBlur:U,ripple:e.ripple},{"thumb-label":l["thumb-label"]})])}})}),{}}}),M=e=>(Je("data-v-866df850"),e=e(),We(),e),vu={class:"settings__heading"},fu=M(()=>s("span",{class:"ml-3"},"コメント/実況",-1)),_u=M(()=>s("div",{class:"settings__item-label mt-0",style:{"border-left":"3px solid rgb(var(--v-theme-text-darken-1))","padding-left":"12px"}},[T(" コメントの透明度は、コメントプレイヤー下にある設定アイコン ⚙️ から変更できます。"),s("br")],-1)),bu=M(()=>s("div",{class:"settings__item"},[s("div",{class:"settings__item-heading"},"コメントのミュート設定"),s("div",{class:"settings__item-label"},[T(" 表示したくないコメントを、映像上やコメントリストに表示しないようにミュートできます。"),s("br")]),s("div",{class:"settings__item-label mt-2"},[T(" デフォルトでは、下記のミュート設定がオンになっています。"),s("br"),T(" これらのコメントも表示したい方は、適宜オフに設定してください。"),s("br"),s("ul",{class:"ml-5 mt-2"},[s("li",null,"露骨な表現を含むコメントをミュートする"),s("li",null,"ネガティブな表現、差別的な表現、政治的に偏った表現を含むコメントをミュートする"),s("li",null,"文字サイズが大きいコメントをミュートする")])])],-1)),Cu=M(()=>s("span",{class:"ml-1"},"コメントのミュート設定を開く",-1)),hu={class:"settings__item"},gu=M(()=>s("div",{class:"settings__item-heading"},"コメントの速さ",-1)),pu=M(()=>s("div",{class:"settings__item-label"},[T(" プレイヤーに流れるコメントの速さを設定します。"),s("br"),T(" たとえば 1.2 に設定すると、コメントが 1.2 倍速く流れます。"),s("br")],-1)),Bu={class:"settings__item"},Fu=M(()=>s("div",{class:"settings__item-heading"},"コメントの文字サイズ",-1)),ku=M(()=>s("div",{class:"settings__item-label"},[T(" プレイヤーに流れるコメントの文字サイズの基準値を設定します。"),s("br"),T(" 実際の文字サイズは画面サイズに合わせて調整されます。デフォルトの文字サイズは 34px です。"),s("br")],-1)),Eu={class:"settings__item settings__item--switch"},Su=M(()=>s("label",{class:"settings__item-heading",for:"close_comment_form_after_sending"},"コメント送信後にコメント入力フォームを閉じる",-1)),yu=M(()=>s("label",{class:"settings__item-label",for:"close_comment_form_after_sending"},[T(" この設定をオンにすると、コメントを送信した後に、コメント入力フォームが自動で閉じるようになります。"),s("br"),T(" なお、コメント入力フォームが表示されたままだと、大半のショートカットキーが文字入力と競合して使えなくなります。ショートカットキーを頻繁に使う方はオンにしておくのがおすすめです。"),s("br")],-1));function Au(e,u,l,r,d,h){const v=Q("Icon"),c=Q("CommentMuteSettings"),g=Q("SettingsBase");return de(),qe(g,null,{default:ce(()=>[s("h2",vu,[ue((de(),Ke("a",{class:"settings__back-button",onClick:u[0]||(u[0]=o=>e.$router.back())},[a(v,{icon:"fluent:arrow-left-12-filled",width:"25px"})])),[[be]]),a(v,{icon:"bi:chat-left-text-fill",width:"19px"}),fu]),s("div",{class:je(["settings__content",{"settings__content--loading":e.is_loading}])},[_u,bu,a(Oe,{class:"settings__save-button mt-4",variant:"flat",onClick:u[1]||(u[1]=o=>e.comment_mute_settings_modal=!e.comment_mute_settings_modal)},{default:ce(()=>[a(v,{icon:"heroicons-solid:filter",height:"19px"}),Cu]),_:1}),s("div",hu,[gu,pu,a(ve,{class:"settings__item-form",color:"primary","show-ticks":"always","thumb-label":"","hide-details":"",step:.1,min:.5,max:2,modelValue:e.settingsStore.settings.comment_speed_rate,"onUpdate:modelValue":u[2]||(u[2]=o=>e.settingsStore.settings.comment_speed_rate=o)},null,8,["modelValue"])]),s("div",Bu,[Fu,ku,a(ve,{class:"settings__item-form",color:"primary","show-ticks":"always","thumb-label":"","hide-details":"",step:1,min:20,max:60,modelValue:e.settingsStore.settings.comment_font_size,"onUpdate:modelValue":u[3]||(u[3]=o=>e.settingsStore.settings.comment_font_size=o)},null,8,["modelValue"])]),s("div",Eu,[Su,yu,a(uu,{class:"settings__item-switch",color:"primary",id:"close_comment_form_after_sending","hide-details":"",modelValue:e.settingsStore.settings.close_comment_form_after_sending,"onUpdate:modelValue":u[4]||(u[4]=o=>e.settingsStore.settings.close_comment_form_after_sending=o)},null,8,["modelValue"])])],2),a(c,{modelValue:e.comment_mute_settings_modal,"onUpdate:modelValue":u[5]||(u[5]=o=>e.comment_mute_settings_modal=o)},null,8,["modelValue"])]),_:1})}const Nu=Ue(tu,[["render",Au],["__scopeId","data-v-866df850"]]);export{Nu as default};
