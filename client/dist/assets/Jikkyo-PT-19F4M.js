import{d as Fe,m as ye,Q as Ee,u as Ae,x as Q,aa as Ve,ab as we,B as n,ac as oe,ad as te,ae as T,af as ie,W as ee,ag as De,Y as Te,ah as fe,y as _e,A as se,R as be,ai as he,aj as xe,ak as Me,a6 as ae,al as j,a,w as ue,I as Pe,v as ze,am as Re,an as Ne,ao as re,a4 as Le,F as Ie,a8 as $e,_ as Ue,r as Z,o as de,i as je,g as ce,b as l,c as Oe,V as qe,n as Ke,p as Ye,k as Je,j as I}from"./index--jRW6aUY.js";import{C as We}from"./CommentMuteSettings-CoCAKWwF.js";import{S as Xe}from"./Base-44HeqPwm.js";import{n as Qe,o as Ge,m as He,u as Ze,d as me,p as eu,j as uu}from"./VSwitch-YZIJ6XkY.js";import"./VCard-DYlqhwQD.js";import"./ssrBoot-vShFW_Pp.js";import"./VAvatar-CprxM-F-.js";import"./Navigation-ZyyA-CMr.js";const tu=Fe({name:"Settings-Jikkyo",components:{SettingsBase:Xe,CommentMuteSettings:We},data(){return{comment_mute_settings_modal:!1,is_loading:!0}},computed:{...ye(Ae,Ee)},async created(){await this.userStore.fetchUser(),this.is_loading=!1}}),le=Symbol.for("vuetify:v-slider");function su(e,u,s){const r=s==="vertical",d=u.getBoundingClientRect(),g="touches"in e?e.touches[0]:e;return r?g.clientY-(d.top+d.height/2):g.clientX-(d.left+d.width/2)}function au(e,u){return"touches"in e&&e.touches.length?e.touches[0][u]:"changedTouches"in e&&e.changedTouches.length?e.changedTouches[0][u]:e[u]}const lu=Q({disabled:{type:Boolean,default:null},error:Boolean,readonly:{type:Boolean,default:null},max:{type:[Number,String],default:100},min:{type:[Number,String],default:0},step:{type:[Number,String],default:0},thumbColor:String,thumbLabel:{type:[Boolean,String],default:void 0,validator:e=>typeof e=="boolean"||e==="always"},thumbSize:{type:[Number,String],default:20},showTicks:{type:[Boolean,String],default:!1,validator:e=>typeof e=="boolean"||e==="always"},ticks:{type:[Array,Object]},tickSize:{type:[Number,String],default:2},color:String,trackColor:String,trackFillColor:String,trackSize:{type:[Number,String],default:4},direction:{type:String,default:"horizontal",validator:e=>["vertical","horizontal"].includes(e)},reverse:Boolean,...Ve(),...we({elevation:2}),ripple:{type:Boolean,default:!0}},"Slider"),nu=e=>{const u=n(()=>parseFloat(e.min)),s=n(()=>parseFloat(e.max)),r=n(()=>+e.step>0?parseFloat(e.step):0),d=n(()=>Math.max(oe(r.value),oe(u.value)));function g(v){if(v=parseFloat(v),r.value<=0)return v;const c=fe(v,u.value,s.value),p=u.value%r.value,i=Math.round((c-p)/r.value)*r.value+p;return parseFloat(Math.min(i,s.value).toFixed(d.value))}return{min:u,max:s,step:r,decimals:d,roundValue:g}},ou=e=>{let{props:u,steps:s,onSliderStart:r,onSliderMove:d,onSliderEnd:g,getActiveThumb:v}=e;const{isRtl:c}=te(),p=T(u,"reverse"),i=n(()=>u.direction==="vertical"),A=n(()=>i.value!==p.value),{min:C,max:S,step:V,decimals:R,roundValue:M}=s,$=n(()=>parseInt(u.thumbSize,10)),N=n(()=>parseInt(u.tickSize,10)),P=n(()=>parseInt(u.trackSize,10)),w=n(()=>(S.value-C.value)/V.value),U=T(u,"disabled"),D=n(()=>u.error||u.disabled?void 0:u.thumbColor??u.color),m=n(()=>u.error||u.disabled?void 0:u.trackColor??u.color),F=n(()=>u.error||u.disabled?void 0:u.trackFillColor??u.color),b=ie(!1),h=ie(0),y=ee(),E=ee();function o(t){var ne;const _=u.direction==="vertical",ge=_?"top":"left",pe=_?"height":"width",Ce=_?"clientY":"clientX",{[ge]:ke,[pe]:Be}=(ne=y.value)==null?void 0:ne.$el.getBoundingClientRect(),Se=au(t,Ce);let H=Math.min(Math.max((Se-ke-h.value)/Be,0),1)||0;return(_?A.value:A.value!==c.value)&&(H=1-H),M(C.value+H*(S.value-C.value))}const z=t=>{g({value:o(t)}),b.value=!1,h.value=0},L=t=>{E.value=v(t),E.value&&(E.value.focus(),b.value=!0,E.value.contains(t.target)?h.value=su(t,E.value,u.direction):(h.value=0,d({value:o(t)})),r({value:o(t)}))},B={passive:!0,capture:!0};function O(t){d({value:o(t)})}function Y(t){t.stopPropagation(),t.preventDefault(),z(t),window.removeEventListener("mousemove",O,B),window.removeEventListener("mouseup",Y)}function J(t){var _;z(t),window.removeEventListener("touchmove",O,B),(_=t.target)==null||_.removeEventListener("touchend",J)}function G(t){var _;L(t),window.addEventListener("touchmove",O,B),(_=t.target)==null||_.addEventListener("touchend",J,{passive:!1})}function k(t){t.preventDefault(),L(t),window.addEventListener("mousemove",O,B),window.addEventListener("mouseup",Y,{passive:!1})}const f=t=>{const _=(t-C.value)/(S.value-C.value)*100;return fe(isNaN(_)?0:_,0,100)},q=T(u,"showTicks"),K=n(()=>q.value?u.ticks?Array.isArray(u.ticks)?u.ticks.map(t=>({value:t,position:f(t),label:t.toString()})):Object.keys(u.ticks).map(t=>({value:parseFloat(t),position:f(parseFloat(t)),label:u.ticks[t]})):w.value!==1/0?De(w.value+1).map(t=>{const _=C.value+t*V.value;return{value:_,position:f(_)}}):[]:[]),W=n(()=>K.value.some(t=>{let{label:_}=t;return!!_})),X={activeThumbRef:E,color:T(u,"color"),decimals:R,disabled:U,direction:T(u,"direction"),elevation:T(u,"elevation"),hasLabels:W,isReversed:p,indexFromEnd:A,min:C,max:S,mousePressed:b,numTicks:w,onSliderMousedown:k,onSliderTouchstart:G,parsedTicks:K,parseMouseMove:o,position:f,readonly:T(u,"readonly"),rounded:T(u,"rounded"),roundValue:M,showTicks:q,startOffset:h,step:V,thumbSize:$,thumbColor:D,thumbLabel:T(u,"thumbLabel"),ticks:T(u,"ticks"),tickSize:N,trackColor:m,trackContainerRef:y,trackFillColor:F,trackSize:P,vertical:i};return Te(le,X),X},iu=Q({focused:Boolean,max:{type:Number,required:!0},min:{type:Number,required:!0},modelValue:{type:Number,required:!0},position:{type:Number,required:!0},ripple:{type:[Boolean,Object],default:!0},..._e()},"VSliderThumb"),ru=se()({name:"VSliderThumb",directives:{Ripple:be},props:iu(),emits:{"update:modelValue":e=>!0},setup(e,u){let{slots:s,emit:r}=u;const d=he(le),{isRtl:g,rtlClasses:v}=te();if(!d)throw new Error("[Vuetify] v-slider-thumb must be used inside v-slider or v-range-slider");const{thumbColor:c,step:p,disabled:i,thumbSize:A,thumbLabel:C,direction:S,isReversed:V,vertical:R,readonly:M,elevation:$,mousePressed:N,decimals:P,indexFromEnd:w}=d,U=n(()=>i.value?void 0:$.value),{elevationClasses:D}=xe(U),{textColorClasses:m,textColorStyles:F}=Me(c),{pageup:b,pagedown:h,end:y,home:E,left:o,right:z,down:L,up:B}=Re,O=[b,h,y,E,o,z,L,B],Y=n(()=>p.value?[1,2,3]:[1,5,10]);function J(k,f){if(!O.includes(k.key))return;k.preventDefault();const q=p.value||.1,K=(e.max-e.min)/q;if([o,z,L,B].includes(k.key)){const X=(R.value?[g.value?o:z,V.value?L:B]:w.value!==g.value?[o,B]:[z,B]).includes(k.key)?1:-1,t=k.shiftKey?2:k.ctrlKey?1:0;f=f+X*q*Y.value[t]}else if(k.key===E)f=e.min;else if(k.key===y)f=e.max;else{const W=k.key===h?1:-1;f=f-W*q*(K>100?K/10:10)}return Math.max(e.min,Math.min(e.max,f))}function G(k){const f=J(k,e.modelValue);f!=null&&r("update:modelValue",f)}return ae(()=>{const k=j(w.value?100-e.position:e.position,"%");return a("div",{class:["v-slider-thumb",{"v-slider-thumb--focused":e.focused,"v-slider-thumb--pressed":e.focused&&N.value},e.class,v.value],style:[{"--v-slider-thumb-position":k,"--v-slider-thumb-size":j(A.value)},e.style],role:"slider",tabindex:i.value?-1:0,"aria-valuemin":e.min,"aria-valuemax":e.max,"aria-valuenow":e.modelValue,"aria-readonly":!!M.value,"aria-orientation":S.value,onKeydown:M.value?void 0:G},[a("div",{class:["v-slider-thumb__surface",m.value,D.value],style:{...F.value}},null),ue(a("div",{class:["v-slider-thumb__ripple",m.value],style:F.value},null),[[Pe("ripple"),e.ripple,null,{circle:!0,center:!0}]]),a(Qe,{origin:"bottom center"},{default:()=>{var f;return[ue(a("div",{class:"v-slider-thumb__label-container"},[a("div",{class:["v-slider-thumb__label"]},[a("div",null,[((f=s["thumb-label"])==null?void 0:f.call(s,{modelValue:e.modelValue}))??e.modelValue.toFixed(p.value?P.value:1)])])]),[[ze,C.value&&e.focused||C.value==="always"]])]}})])}),{}}}),du=Q({start:{type:Number,required:!0},stop:{type:Number,required:!0},..._e()},"VSliderTrack"),cu=se()({name:"VSliderTrack",props:du(),emits:{},setup(e,u){let{slots:s}=u;const r=he(le);if(!r)throw new Error("[Vuetify] v-slider-track must be inside v-slider or v-range-slider");const{color:d,parsedTicks:g,rounded:v,showTicks:c,tickSize:p,trackColor:i,trackFillColor:A,trackSize:C,vertical:S,min:V,max:R,indexFromEnd:M}=r,{roundedClasses:$}=Ne(v),{backgroundColorClasses:N,backgroundColorStyles:P}=re(A),{backgroundColorClasses:w,backgroundColorStyles:U}=re(i),D=n(()=>`inset-${S.value?"block":"inline"}-${M.value?"end":"start"}`),m=n(()=>S.value?"height":"width"),F=n(()=>({[D.value]:"0%",[m.value]:"100%"})),b=n(()=>e.stop-e.start),h=n(()=>({[D.value]:j(e.start,"%"),[m.value]:j(b.value,"%")})),y=n(()=>c.value?(S.value?g.value.slice().reverse():g.value).map((o,z)=>{var B;const L=o.value!==V.value&&o.value!==R.value?j(o.position,"%"):void 0;return a("div",{key:o.value,class:["v-slider-track__tick",{"v-slider-track__tick--filled":o.position>=e.start&&o.position<=e.stop,"v-slider-track__tick--first":o.value===V.value,"v-slider-track__tick--last":o.value===R.value}],style:{[D.value]:L}},[(o.label||s["tick-label"])&&a("div",{class:"v-slider-track__tick-label"},[((B=s["tick-label"])==null?void 0:B.call(s,{tick:o,index:z}))??o.label])])}):[]);return ae(()=>a("div",{class:["v-slider-track",$.value,e.class],style:[{"--v-slider-track-size":j(C.value),"--v-slider-tick-size":j(p.value)},e.style]},[a("div",{class:["v-slider-track__background",w.value,{"v-slider-track__background--opacity":!!d.value||!A.value}],style:{...F.value,...U.value}},null),a("div",{class:["v-slider-track__fill",N.value],style:{...h.value,...P.value}},null),c.value&&a("div",{class:["v-slider-track__ticks",{"v-slider-track__ticks--always-show":c.value==="always"}]},[y.value])])),{}}}),mu=Q({...Ge(),...lu(),...He(),modelValue:{type:[Number,String],default:0}},"VSlider"),ve=se()({name:"VSlider",props:mu(),emits:{"update:focused":e=>!0,"update:modelValue":e=>!0,start:e=>!0,end:e=>!0},setup(e,u){let{slots:s,emit:r}=u;const d=ee(),{rtlClasses:g}=te(),v=nu(e),c=Le(e,"modelValue",void 0,m=>v.roundValue(m??v.min.value)),{min:p,max:i,mousePressed:A,roundValue:C,onSliderMousedown:S,onSliderTouchstart:V,trackContainerRef:R,position:M,hasLabels:$,readonly:N}=ou({props:e,steps:v,onSliderStart:()=>{r("start",c.value)},onSliderEnd:m=>{let{value:F}=m;const b=C(F);c.value=b,r("end",b)},onSliderMove:m=>{let{value:F}=m;return c.value=C(F)},getActiveThumb:()=>{var m;return(m=d.value)==null?void 0:m.$el}}),{isFocused:P,focus:w,blur:U}=Ze(e),D=n(()=>M(c.value));return ae(()=>{const m=me.filterProps(e),F=!!(e.label||s.label||s.prepend);return a(me,$e({class:["v-slider",{"v-slider--has-labels":!!s["tick-label"]||$.value,"v-slider--focused":P.value,"v-slider--pressed":A.value,"v-slider--disabled":e.disabled},g.value,e.class],style:e.style},m,{focused:P.value}),{...s,prepend:F?b=>{var h,y;return a(Ie,null,[((h=s.label)==null?void 0:h.call(s,b))??(e.label?a(eu,{id:b.id.value,class:"v-slider__label",text:e.label},null):void 0),(y=s.prepend)==null?void 0:y.call(s,b)])}:void 0,default:b=>{let{id:h,messagesId:y}=b;return a("div",{class:"v-slider__container",onMousedown:N.value?void 0:S,onTouchstartPassive:N.value?void 0:V},[a("input",{id:h.value,name:e.name||h.value,disabled:!!e.disabled,readonly:!!e.readonly,tabindex:"-1",value:c.value},null),a(cu,{ref:R,start:0,stop:D.value},{"tick-label":s["tick-label"]}),a(ru,{ref:d,"aria-describedby":y.value,focused:P.value,min:p.value,max:i.value,modelValue:c.value,"onUpdate:modelValue":E=>c.value=E,position:D.value,elevation:e.elevation,onFocus:w,onBlur:U,ripple:e.ripple},{"thumb-label":s["thumb-label"]})])}})}),{}}}),x=e=>(Ye("data-v-764168d6"),e=e(),Je(),e),vu={class:"settings__heading"},fu=x(()=>l("span",{class:"ml-3"},"コメント/実況",-1)),_u=x(()=>l("div",{class:"settings__item-label mt-0"},[I(" コメントの透明度の設定は、別途コメントプレイヤー下の設定アイコンから行えます。"),l("br")],-1)),bu=x(()=>l("div",{class:"settings__item"},[l("div",{class:"settings__item-heading"},"コメントのミュート設定"),l("div",{class:"settings__item-label"},[I(" 表示したくないコメントを、映像上やコメントリストに表示しないようにミュートできます。"),l("br")])],-1)),hu=x(()=>l("span",{class:"ml-1"},"コメントのミュート設定を開く",-1)),gu={class:"settings__item"},pu=x(()=>l("div",{class:"settings__item-heading"},"コメントの速さ",-1)),Cu=x(()=>l("div",{class:"settings__item-label"},[I(" プレイヤーに流れるコメントの速さを設定します。"),l("br"),I(" たとえば 1.2 に設定すると、コメントが 1.2 倍速く流れます。"),l("br")],-1)),ku={class:"settings__item"},Bu=x(()=>l("div",{class:"settings__item-heading"},"コメントの文字サイズ",-1)),Su=x(()=>l("div",{class:"settings__item-label"},[I(" プレイヤーに流れるコメントの文字サイズの基準値を設定します。"),l("br"),I(" 実際の文字サイズは画面サイズに合わせて調整されます。デフォルトの文字サイズは 34px です。"),l("br")],-1)),Fu={class:"settings__item settings__item--switch"},yu=x(()=>l("label",{class:"settings__item-heading",for:"close_comment_form_after_sending"},"コメント送信後にコメント入力フォームを閉じる",-1)),Eu=x(()=>l("label",{class:"settings__item-label",for:"close_comment_form_after_sending"},[I(" この設定をオンにすると、コメントを送信した後に、コメント入力フォームが自動で閉じるようになります。"),l("br"),I(" なお、コメント入力フォームが表示されたままだと、大半のショートカットキーが文字入力と競合して使えなくなります。ショートカットキーを頻繁に使う方はオンにしておくのがおすすめです。"),l("br")],-1));function Au(e,u,s,r,d,g){const v=Z("Icon"),c=Z("CommentMuteSettings"),p=Z("SettingsBase");return de(),je(p,null,{default:ce(()=>[l("h2",vu,[ue((de(),Oe("a",{class:"settings__back-button",onClick:u[0]||(u[0]=i=>e.$router.back())},[a(v,{icon:"fluent:arrow-left-12-filled",width:"25px"})])),[[be]]),a(v,{icon:"bi:chat-left-text-fill",width:"19px"}),fu]),l("div",{class:Ke(["settings__content",{"settings__content--loading":e.is_loading}])},[_u,bu,a(qe,{class:"settings__save-button mt-4",variant:"flat",onClick:u[1]||(u[1]=i=>e.comment_mute_settings_modal=!e.comment_mute_settings_modal)},{default:ce(()=>[a(v,{icon:"heroicons-solid:filter",height:"19px"}),hu]),_:1}),l("div",gu,[pu,Cu,a(ve,{class:"settings__item-form",color:"primary","show-ticks":"always","thumb-label":"","hide-details":"",step:.1,min:.5,max:2,modelValue:e.settingsStore.settings.comment_speed_rate,"onUpdate:modelValue":u[2]||(u[2]=i=>e.settingsStore.settings.comment_speed_rate=i)},null,8,["modelValue"])]),l("div",ku,[Bu,Su,a(ve,{class:"settings__item-form",color:"primary","show-ticks":"always","thumb-label":"","hide-details":"",step:1,min:20,max:60,modelValue:e.settingsStore.settings.comment_font_size,"onUpdate:modelValue":u[3]||(u[3]=i=>e.settingsStore.settings.comment_font_size=i)},null,8,["modelValue"])]),l("div",Fu,[yu,Eu,a(uu,{class:"settings__item-switch",color:"primary",id:"close_comment_form_after_sending","hide-details":"",modelValue:e.settingsStore.settings.close_comment_form_after_sending,"onUpdate:modelValue":u[4]||(u[4]=i=>e.settingsStore.settings.close_comment_form_after_sending=i)},null,8,["modelValue"])])],2),a(c,{modelValue:e.comment_mute_settings_modal,"onUpdate:modelValue":u[5]||(u[5]=i=>e.comment_mute_settings_modal=i)},null,8,["modelValue"])]),_:1})}const Ru=Ue(tu,[["render",Au],["__scopeId","data-v-764168d6"]]);export{Ru as default};