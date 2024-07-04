import{d as C,s as D,x as S,y as H,r as j,o as $,c as w,a as l,b as t,z as s,A as v,g as u,k as d,V as m,w as I,j as B,B as p,M as _,p as N,q as z,_ as T}from"./index-BaStaaT9.js";import{H as U,N as J}from"./Navigation-D_QnHcrb.js";import{u as P}from"./ChannelsStore-CddwsnhO.js";import{V as R,a as h}from"./VSelect-BPcsEtxq.js";import{T as A}from"./ssrBoot-CaVSYxv9.js";import"./VAvatar-QKVU0Wtb.js";const k=x=>(N("data-v-c381094e"),x=x(),z(),x),K={class:"route-container"},q={class:"px-5 py-8",style:{width:"100%","max-width":"850px",margin:"0 auto","line-height":"1.65"}},E=k(()=>t("h1",null,"過去ログ再生",-1)),F=k(()=>t("p",{class:"mt-4 text-text-darken-1"},[t("strong",null,[t("a",{class:"link",href:"https://jikkyo.tsukumijima.net",target:"_blank"},"ニコニコ実況 過去ログ API"),d(" に保存されている、2009年11月から現在までの 旧ニコニコ実況・ニコ生統合後の新ニコニコ実況・NX-Jikkyo のすべての過去ログを、チャンネルと日時範囲を指定して再生できます。")]),t("br")],-1)),G=k(()=>t("p",{class:"mt-2 text-text-darken-1"},[d(" 十数年分もの膨大な過去ログデータには、当時の世相が色濃く反映された、その時代を生きた「生の声」が、まるでタイムカプセルのように刻まれています。"),t("br"),d(" たまには昔のコメントを眺めて懐かしんだり、録画番組をコメント付きで楽しんでみては？ ")],-1)),O={class:"mt-8",style:{display:"grid","grid-template-columns":"1fr 1fr","column-gap":"16px"}},X={class:"d-flex justify-space-around",style:{"font-family":"'Open Sans','YakuHanJPs','Twemoji','Hiragino Sans','Noto Sans JP',sans-serif"}},L={class:"d-flex",style:{"column-gap":"8px"}},Q={class:"d-flex",style:{"column-gap":"8px"}},W={class:"mt-6",style:{display:"grid","grid-template-columns":"1fr 1fr","column-gap":"16px"}},Z={class:"mt-2 d-flex justify-space-around"},ee=k(()=>t("span",{class:"ml-2",style:{"font-size":"17px"}},"過去ログを再生",-1)),te=C({__name:"Index",setup(x){const b=D(),Y=S([]),V=P();V.update().then(()=>{const o=[...V.channels_list.GR,...V.channels_list.BS];Y.value=o.map(e=>({title:`Ch:${e.channel_number} (${e.id}) : ${e.name}`,value:e.id}))});const{jikkyo_channel_id:g,start_date:c,start_time:f,end_date:n,end_time:i}=H();function y(o){const e=p(`${n.value} ${i.value}`);if(!e.isValid())return;const r=e.add(o,"minute");n.value=r.format("YYYY-MM-DD"),i.value=r.format("HH:mm")}function M(){const o=p(`${c.value} ${f.value}`),e=p(`${n.value} ${i.value}`);if(!o.isValid()||!e.isValid()){_.error("開始日時または終了日時が無効です。");return}if(e.diff(o,"hour")>=12){_.error("一度に再生できる過去ログは12時間以内です。");return}if(e<o){_.error("指定された終了日時が開始日時より前です。");return}if(e>p()){_.error("指定された終了日時が未来の日付です。");return}if(o.isSame(e)){_.error("指定された開始日時と終了日時が同じです。");return}const r=`${o.format("YYYYMMDDHHmmss")}-${e.format("YYYYMMDDHHmmss")}`;b.push({path:`/log/${g.value}/${r}`})}return(o,e)=>{const r=j("Icon");return $(),w("div",K,[l(U),t("main",null,[l(J),t("div",q,[E,F,G,l(R,{class:"mt-8 datetime-field",color:"primary",variant:"outlined","hide-details":"",label:"実況チャンネル",items:Y.value,modelValue:s(g),"onUpdate:modelValue":e[0]||(e[0]=a=>v(g)?g.value=a:null)},null,8,["items","modelValue"]),t("div",O,[l(h,{type:"date",class:"datetime-field",color:"primary",variant:"outlined",label:"開始日付",min:"2009-11-26",max:s(p)().format("YYYY-MM-DD"),modelValue:s(c),"onUpdate:modelValue":e[1]||(e[1]=a=>v(c)?c.value=a:null)},null,8,["max","modelValue"]),l(h,{type:"time",class:"datetime-field",color:"primary",variant:"outlined",label:"開始時刻",modelValue:s(f),"onUpdate:modelValue":e[2]||(e[2]=a=>v(f)?f.value=a:null)},null,8,["modelValue"])]),t("div",X,[t("div",L,[l(m,{variant:"flat",color:"background-lighten-2",height:"46",class:"px-2",style:{"font-size":"15px"},onClick:e[3]||(e[3]=a=>y(-30))},{default:u(()=>[d(" －30分 ")]),_:1}),l(m,{variant:"flat",color:"background-lighten-2",height:"46",class:"px-2",style:{"font-size":"15px"},onClick:e[4]||(e[4]=a=>y(-5))},{default:u(()=>[d(" －5分 ")]),_:1})]),I(($(),B(m,{variant:"flat",color:"secondary",height:"46",class:"px-2",onClick:e[5]||(e[5]=a=>{n.value=s(c),i.value=s(f)})},{default:u(()=>[l(r,{icon:"fluent:chevron-double-down-16-filled",height:"40px"})]),_:1})),[[A,"開始日時を終了日時に設定",void 0,{top:!0}]]),t("div",Q,[l(m,{variant:"flat",color:"background-lighten-2",height:"46",class:"px-2",style:{"font-size":"15px"},onClick:e[6]||(e[6]=a=>y(5))},{default:u(()=>[d(" ＋5分 ")]),_:1}),l(m,{variant:"flat",color:"background-lighten-2",height:"46",class:"px-2",style:{"font-size":"15px"},onClick:e[7]||(e[7]=a=>y(30))},{default:u(()=>[d(" ＋30分 ")]),_:1})])]),t("div",W,[l(h,{type:"date",class:"datetime-field",color:"primary",variant:"outlined",label:"終了日付",min:"2009-11-26",max:s(p)().format("YYYY-MM-DD"),modelValue:s(n),"onUpdate:modelValue":e[8]||(e[8]=a=>v(n)?n.value=a:null)},null,8,["max","modelValue"]),l(h,{type:"time",class:"datetime-field",color:"primary",variant:"outlined",label:"終了時刻",modelValue:s(i),"onUpdate:modelValue":e[9]||(e[9]=a=>v(i)?i.value=a:null)},null,8,["modelValue"])]),t("div",Z,[l(m,{variant:"flat",color:"secondary",height:"54",onClick:e[10]||(e[10]=a=>M())},{default:u(()=>[l(r,{icon:"fluent:receipt-play-20-regular",height:"32px"}),ee]),_:1})])])])])}}}),re=T(te,[["__scopeId","data-v-c381094e"]]);export{re as default};
