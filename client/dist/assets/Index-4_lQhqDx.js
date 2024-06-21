import{d as H,x as w,y as I,z as M,r as j,a as B,o as b,c as D,b as l,e as a,A as r,B as c,h as d,l as f,V as u,w as N,k as z,C as g,M as h,q as U,s as J,_ as P}from"./index-BS3Sg6jL.js";import{H as R,N as T}from"./Navigation-CKtjjT6Z.js";import{u as A}from"./ChannelsStore-BpfES4NQ.js";import{V as K,a as x}from"./VSelect-DfudoCc9.js";import"./ssrBoot-CBm8SFmk.js";import"./VAvatar-DdSbVFQX.js";const V=v=>(U("data-v-a6f1e5e6"),v=v(),J(),v),q={class:"route-container"},E={class:"px-5 py-8",style:{width:"100%","max-width":"850px",margin:"0 auto","line-height":"1.65"}},F=V(()=>a("h1",null,"過去ログ再生",-1)),G=V(()=>a("p",{class:"mt-4 text-text-darken-1"},[a("strong",null,[a("a",{class:"link",href:"https://jikkyo.tsukumijima.net",target:"_blank"},"ニコニコ実況 過去ログ API"),f(" に保存されている、2009年11月から現在までの 旧ニコニコ実況・ニコ生統合後の新ニコニコ実況・NX-Jikkyo のすべての過去ログを、チャンネルと日時範囲を指定して再生できます。")]),a("br")],-1)),O={class:"mt-8",style:{display:"grid","grid-template-columns":"1fr 1fr","column-gap":"16px"}},X={class:"d-flex justify-space-around",style:{"font-family":"'Open Sans','YakuHanJPs','Twemoji','Hiragino Sans','Noto Sans JP',sans-serif"}},L={class:"d-flex",style:{"column-gap":"8px"}},Q={class:"d-flex",style:{"column-gap":"8px"}},W={class:"mt-6",style:{display:"grid","grid-template-columns":"1fr 1fr","column-gap":"16px"}},Z={class:"mt-3 d-flex justify-space-around"},ee=V(()=>a("span",{class:"ml-2",style:{"font-size":"17px"}},"過去ログを再生",-1)),te=H({__name:"Index",setup(v){const Y=w(),$=I([]),k=A();k.update().then(()=>{const o=[...k.channels_list.GR,...k.channels_list.BS];$.value=o.map(e=>({title:`Ch:${e.channel_number} (${e.id}) : ${e.name}`,value:e.id}))});const{jikkyo_channel_id:_,start_date:m,start_time:p,end_date:s,end_time:n}=M();function y(o){const i=g(`${s.value} ${n.value}`).add(o,"minute");s.value=i.format("YYYY-MM-DD"),n.value=i.format("HH:mm")}function C(){const o=g(`${m.value} ${p.value}`),e=g(`${s.value} ${n.value}`);if(e.diff(o,"hour")>=12){h.error("一度に再生できる過去ログは12時間以内です。");return}if(e<o){h.error("指定された終了日時が開始日時より前です。");return}if(e>g()){h.error("指定された終了日時が未来の日付です。");return}if(o.isSame(e)){h.error("指定された開始日時と終了日時が同じです。");return}const i=`${o.format("YYYYMMDDHHmmss")}-${e.format("YYYYMMDDHHmmss")}`;Y.push({path:`/log/${_.value}/${i}`})}return(o,e)=>{const i=j("Icon"),S=B("tooltip");return b(),D("div",q,[l(R),a("main",null,[l(T),a("div",E,[F,G,l(K,{class:"mt-12 datetime-field",color:"primary",variant:"outlined","hide-details":"",label:"実況チャンネル",items:$.value,modelValue:r(_),"onUpdate:modelValue":e[0]||(e[0]=t=>c(_)?_.value=t:null)},null,8,["items","modelValue"]),a("div",O,[l(x,{type:"date",color:"primary",variant:"outlined",label:"開始日付",class:"datetime-field",modelValue:r(m),"onUpdate:modelValue":e[1]||(e[1]=t=>c(m)?m.value=t:null)},null,8,["modelValue"]),l(x,{type:"time",color:"primary",variant:"outlined",label:"開始時刻",class:"datetime-field",modelValue:r(p),"onUpdate:modelValue":e[2]||(e[2]=t=>c(p)?p.value=t:null)},null,8,["modelValue"])]),a("div",X,[a("div",L,[l(u,{variant:"flat",color:"background-lighten-2",height:"46",class:"px-2",style:{"font-size":"15px"},onClick:e[3]||(e[3]=t=>y(-30))},{default:d(()=>[f(" －30分 ")]),_:1}),l(u,{variant:"flat",color:"background-lighten-2",height:"46",class:"px-2",style:{"font-size":"15px"},onClick:e[4]||(e[4]=t=>y(-5))},{default:d(()=>[f(" －5分 ")]),_:1})]),N((b(),z(u,{variant:"flat",color:"secondary",height:"46",class:"px-2",onClick:e[5]||(e[5]=t=>{s.value=r(m),n.value=r(p)})},{default:d(()=>[l(i,{icon:"fluent:chevron-double-down-16-filled",height:"40px"})]),_:1})),[[S,"開始日時を終了日時に設定",void 0,{top:!0}]]),a("div",Q,[l(u,{variant:"flat",color:"background-lighten-2",height:"46",class:"px-2",style:{"font-size":"15px"},onClick:e[6]||(e[6]=t=>y(5))},{default:d(()=>[f(" ＋5分 ")]),_:1}),l(u,{variant:"flat",color:"background-lighten-2",height:"46",class:"px-2",style:{"font-size":"15px"},onClick:e[7]||(e[7]=t=>y(30))},{default:d(()=>[f(" ＋30分 ")]),_:1})])]),a("div",W,[l(x,{type:"date",color:"primary",variant:"outlined",label:"終了日付",class:"datetime-field",modelValue:r(s),"onUpdate:modelValue":e[8]||(e[8]=t=>c(s)?s.value=t:null)},null,8,["modelValue"]),l(x,{type:"time",color:"primary",variant:"outlined",label:"終了時刻",class:"datetime-field",modelValue:r(n),"onUpdate:modelValue":e[9]||(e[9]=t=>c(n)?n.value=t:null)},null,8,["modelValue"])]),a("div",Z,[l(u,{variant:"flat",color:"secondary",height:"54",onClick:e[10]||(e[10]=t=>C())},{default:d(()=>[l(i,{icon:"fluent:receipt-play-20-regular",height:"32px"}),ee]),_:1})])])])])}}}),re=P(te,[["__scopeId","data-v-a6f1e5e6"]]);export{re as default};
