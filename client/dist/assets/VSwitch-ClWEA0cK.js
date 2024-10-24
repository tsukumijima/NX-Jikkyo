import{q as $,r as j,s as H,k as Q,t as I,m as Y,v as Z,u as ee,f as B,w as D,n as te}from"./VSelect-OSKUVbpC.js";import{G as T,J as R,c5 as x,y as z,co as U,X as L,c7 as M,a5 as ae,b6 as V,b as l,cp as N,cq as le,cr as oe,K as _,cs as ne,c8 as se,F as re,ct as ce,cu as ie,S as ue}from"./index-ZF9MESNM.js";const de=T({fullscreen:Boolean,retainFocus:{type:Boolean,default:!0},scrollable:Boolean,...$({origin:"center center",scrollStrategy:"block",transition:{component:j},zIndex:2400})},"VDialog"),ge=R()({name:"VDialog",props:de(),emits:{"update:modelValue":e=>!0,afterEnter:()=>!0,afterLeave:()=>!0},setup(e,w){let{emit:h,slots:t}=w;const s=x(e,"modelValue"),{scopeId:u}=H(),o=z();function b(a){var c,v;const r=a.relatedTarget,d=a.target;if(r!==d&&((c=o.value)!=null&&c.contentEl)&&((v=o.value)!=null&&v.globalTop)&&![document,o.value.contentEl].includes(d)&&!o.value.contentEl.contains(d)){const n=le(o.value.contentEl);if(!n.length)return;const f=n[0],m=n[n.length-1];r===f?m.focus():f.focus()}}U&&L(()=>s.value&&e.retainFocus,a=>{a?document.addEventListener("focusin",b):document.removeEventListener("focusin",b)},{immediate:!0});function P(){var a;h("afterEnter"),(a=o.value)!=null&&a.contentEl&&!o.value.contentEl.contains(document.activeElement)&&o.value.contentEl.focus({preventScroll:!0})}function S(){h("afterLeave")}return L(s,async a=>{var r;a||(await ae(),(r=o.value.activatorEl)==null||r.focus({preventScroll:!0}))}),M(()=>{const a=I.filterProps(e),r=V({"aria-haspopup":"dialog","aria-expanded":String(s.value)},e.activatorProps),d=V({tabindex:-1},e.contentProps);return l(I,V({ref:o,class:["v-dialog",{"v-dialog--fullscreen":e.fullscreen,"v-dialog--scrollable":e.scrollable},e.class],style:e.style},a,{modelValue:s.value,"onUpdate:modelValue":c=>s.value=c,"aria-modal":"true",activatorProps:r,contentProps:d,role:"dialog",onAfterEnter:P,onAfterLeave:S},u),{activator:t.activator,default:function(){for(var c=arguments.length,v=new Array(c),n=0;n<c;n++)v[n]=arguments[n];return l(N,{root:"VDialog"},{default:()=>{var f;return[(f=t.default)==null?void 0:f.call(t,...v)]}})}})}),Q({},o)}}),ve=T({indeterminate:Boolean,inset:Boolean,flat:Boolean,loading:{type:[Boolean,String],default:!1},...Y(),...Z()},"VSwitch"),Ve=R()({name:"VSwitch",inheritAttrs:!1,props:ve(),emits:{"update:focused":e=>!0,"update:modelValue":e=>!0,"update:indeterminate":e=>!0},setup(e,w){let{attrs:h,slots:t}=w;const s=x(e,"indeterminate"),u=x(e,"modelValue"),{loaderClasses:o}=oe(e),{isFocused:b,focus:P,blur:S}=ee(e),a=z(),r=U&&window.matchMedia("(forced-colors: active)").matches,d=_(()=>typeof e.loading=="string"&&e.loading!==""?e.loading:e.color),c=ne(),v=_(()=>e.id||`switch-${c}`);function n(){s.value&&(s.value=!1)}function f(m){var k,y;m.stopPropagation(),m.preventDefault(),(y=(k=a.value)==null?void 0:k.input)==null||y.click()}return M(()=>{const[m,k]=se(h),y=B.filterProps(e),O=D.filterProps(e);return l(B,V({class:["v-switch",{"v-switch--flat":e.flat},{"v-switch--inset":e.inset},{"v-switch--indeterminate":s.value},o.value,e.class]},m,y,{modelValue:u.value,"onUpdate:modelValue":E=>u.value=E,id:v.value,focused:b.value,style:e.style}),{...t,default:E=>{let{id:q,messagesId:G,isDisabled:J,isReadonly:K,isValid:F}=E;const C={model:u,isValid:F};return l(D,V({ref:a},O,{modelValue:u.value,"onUpdate:modelValue":[g=>u.value=g,n],id:q.value,"aria-describedby":G.value,type:"checkbox","aria-checked":s.value?"mixed":void 0,disabled:J.value,readonly:K.value,onFocus:P,onBlur:S},k),{...t,default:g=>{let{backgroundColorClasses:p,backgroundColorStyles:i}=g;return l("div",{class:["v-switch__track",r?void 0:p.value],style:i.value,onClick:f},[t["track-true"]&&l("div",{key:"prepend",class:"v-switch__track-true"},[t["track-true"](C)]),t["track-false"]&&l("div",{key:"append",class:"v-switch__track-false"},[t["track-false"](C)])])},input:g=>{let{inputNode:p,icon:i,backgroundColorClasses:W,backgroundColorStyles:X}=g;return l(re,null,[p,l("div",{class:["v-switch__thumb",{"v-switch__thumb--filled":i||e.loading},e.inset||r?void 0:W.value],style:e.inset?void 0:X.value},[t.thumb?l(N,{defaults:{VIcon:{icon:i,size:"x-small"}}},{default:()=>[t.thumb({...C,icon:i})]}):l(te,null,{default:()=>[e.loading?l(ie,{name:"v-switch",active:!0,color:F.value===!1?void 0:d.value},{default:A=>t.loader?t.loader(A):l(ue,{active:A.isActive,color:A.color,indeterminate:!0,size:"16",width:"2"},null)}):i&&l(ce,{key:String(i),icon:i,size:"x-small"},null)]})])])}})}})}),{}}});export{ge as V,Ve as a};