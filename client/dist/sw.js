if(!self.define){let s,e={};const a=(a,r)=>(a=new URL(a+".js",r).href,e[a]||new Promise((e=>{if("document"in self){const s=document.createElement("script");s.src=a,s.onload=e,document.head.appendChild(s)}else s=a,importScripts(a),e()})).then((()=>{let s=e[a];if(!s)throw new Error(`Module ${a} didn’t register its module`);return s})));self.define=(r,i)=>{const n=s||("document"in self?document.currentScript.src:"")||location.href;if(e[n])return;let l={};const o=s=>a(s,n),c={module:{uri:n},exports:l,require:o};e[n]=Promise.all(r.map((s=>c[s]||o(s)))).then((s=>(i(...s),l)))}}define(["./workbox-7cfec069"],(function(s){"use strict";self.addEventListener("message",(s=>{s.data&&"SKIP_WAITING"===s.data.type&&self.skipWaiting()})),s.precacheAndRoute([{url:"assets/About-CnyOdybC.js",revision:null},{url:"assets/Base-Czzfa-im.js",revision:null},{url:"assets/Base.BjlBCSlx.css",revision:null},{url:"assets/ChannelsStore-CcCW9zOz.js",revision:null},{url:"assets/CommentMuteSettings-CXeT0l_R.js",revision:null},{url:"assets/CommentMuteSettings.D_KuTpX_.css",revision:null},{url:"assets/General-WiR19SSJ.js",revision:null},{url:"assets/General.aK4X36qF.css",revision:null},{url:"assets/Home-BlSIAqzV.js",revision:null},{url:"assets/Home.BP9nEE5C.css",revision:null},{url:"assets/Index-B9byl_uV.js",revision:null},{url:"assets/index-BNWJpVxJ.js",revision:null},{url:"assets/Index-DnYqd_mb.js",revision:null},{url:"assets/Index.BJ2SdNT5.css",revision:null},{url:"assets/Index.C74jPTNm.css",revision:null},{url:"assets/index.ttl4FU1m.css",revision:null},{url:"assets/Jikkyo-TGlY5781.js",revision:null},{url:"assets/Jikkyo.2hwbduGt.css",revision:null},{url:"assets/Navigation-CY1UoHTm.js",revision:null},{url:"assets/Navigation.C-Nn5LlV.css",revision:null},{url:"assets/NotFound-CvhjuZKh.js",revision:null},{url:"assets/NotFound.CtTq_cgx.css",revision:null},{url:"assets/PlayerController-CX4QXlyC.js",revision:null},{url:"assets/PlayerController.CW-8vHvn.css",revision:null},{url:"assets/ssrBoot-HAdF_jEQ.js",revision:null},{url:"assets/ssrBoot.D4XLN205.css",revision:null},{url:"assets/swiper-BILgi2JZ.js",revision:null},{url:"assets/swiper.Be9b3THL.css",revision:null},{url:"assets/VAvatar-DDF4vV5b.js",revision:null},{url:"assets/VAvatar.BPRvkK24.css",revision:null},{url:"assets/VCard-B2678Vpo.js",revision:null},{url:"assets/VCard.IL2cTJ3-.css",revision:null},{url:"assets/VSelect-B-vClQQZ.js",revision:null},{url:"assets/VSelect.D2-p08jS.css",revision:null},{url:"assets/VSwitch-CE9N9MUU.js",revision:null},{url:"assets/VSwitch.CGl4HpQf.css",revision:null},{url:"assets/Watch-BdM1wJ9s.js",revision:null},{url:"assets/Watch-DmHMw96B.js",revision:null},{url:"assets/workbox-window.prod.es5-D5gOYdM7.js",revision:null},{url:"index.html",revision:"641d8be2fdbdf815d0f9c37439263a39"},{url:"assets/images/icons/icon-192px.png",revision:"d28a46b734fd5febfa29c30d974c3344"},{url:"assets/images/icons/icon-512px.png",revision:"ff334ecb42220b8261edd514a2630ca0"},{url:"assets/images/icons/icon-maskable-192px.png",revision:"f9b88ad399371607223ffcd8d4001f27"},{url:"assets/fonts/Kosugi-Regular.woff2",revision:"c11d0f4e766049ad73b069d2bfd35a74"},{url:"assets/fonts/KosugiMaru-Regular.woff2",revision:"62b5c6457c2bc2bfda594fce863db134"},{url:"assets/fonts/MaterialDesignIcons.woff2",revision:"1d7bcee1b302339c3b8db10214dc9ec6"},{url:"assets/fonts/NotoSansJP-Bold.woff2",revision:"8ae2b8c883b00e678cf347f4089e54b5"},{url:"assets/fonts/NotoSansJP-Medium.woff2",revision:"e8e02898cd984df0386a7feb0881d73c"},{url:"assets/fonts/OpenSans-Bold.woff2",revision:"c0b9bbd547c51eb4bf70adfe2c6751a4"},{url:"assets/fonts/OpenSans-Medium.woff2",revision:"291650388e03dfa88fed8fe2ec138f43"},{url:"assets/fonts/Quicksand-Bold.ttf",revision:"e8dcee4bbf2288a2d264c76fa547f37a"},{url:"assets/fonts/Quicksand-Medium.ttf",revision:"fd7f304a26dd790aef9f1ae84403eab3"},{url:"assets/fonts/Twemoji.woff2",revision:"def76ca590bbc2ab6c79bfbb22ddd882"},{url:"assets/fonts/YakuHanJPs-Bold.woff2",revision:"33e20e22177396ce5c9e402bdeaf9fbd"},{url:"assets/fonts/YakuHanJPs-Medium.woff2",revision:"56621201e09808a0a36a251226584e25"},{url:"assets/images/account-icon-default.png",revision:"3840f879e0ddf77549f4035ae72e8f6b"},{url:"assets/images/icon.svg",revision:"2b8356bad75efefbbf21592f29c7ae01"},{url:"assets/images/logo.svg",revision:"5fcb1230bc3e67174dafbbaeeaae2493"},{url:"assets/images/icons/apple-touch-icon.png",revision:"4f05b71ea984dbc38a2ae179a11dda12"},{url:"assets/images/icons/favicon.svg",revision:"9d6ceff2e63b818b0fdd5a43aaa2c023"},{url:"assets/images/icons/icon-maskable-512px.png",revision:"b5939f40c5695c0f8e6f1b8e37953385"},{url:"assets/images/player-backgrounds/01.jpg",revision:"14d74db9eb062b39dc128daeba77cb63"},{url:"assets/images/player-backgrounds/02.jpg",revision:"98e077363a5eec17da30acef5038f924"},{url:"assets/images/player-backgrounds/03.jpg",revision:"e75e4fc34090286e347cebf12c74b1b8"},{url:"assets/images/player-backgrounds/04.jpg",revision:"714dd3c050c09a16236f2424c548c83f"},{url:"assets/images/player-backgrounds/05.jpg",revision:"717125c34121b326e8f90773565f59ca"},{url:"assets/images/player-backgrounds/06.jpg",revision:"aa3b22785383baf67ad6d53fee94ed1c"},{url:"assets/images/player-backgrounds/07.jpg",revision:"dc9937f7a374b99981cb0d6c9a642e56"},{url:"assets/images/player-backgrounds/08.jpg",revision:"b6cedbf1da35814fbf784591380fde62"},{url:"assets/images/player-backgrounds/09.jpg",revision:"e989450375d6954b37b066a1cec3ad35"},{url:"assets/images/player-backgrounds/10.jpg",revision:"417128b6120078997139b44ee2c73dbd"},{url:"assets/images/player-backgrounds/11.jpg",revision:"8c173e2d5980e09dc7b0e36e97b8f189"},{url:"assets/images/player-backgrounds/12.jpg",revision:"97231a4813562229cc55d4516cb85350"},{url:"assets/images/player-backgrounds/13.jpg",revision:"6efbebd72cadf7bdd59a0ad5325662d7"},{url:"assets/images/player-backgrounds/14.jpg",revision:"54d47c83175ed7f11697a2cb3e54e3b1"},{url:"assets/images/player-backgrounds/15.jpg",revision:"e9cb581540c06a770d299dede678ff0c"},{url:"assets/images/player-backgrounds/16.jpg",revision:"b7e7ddc4ae9ba3811f3d5c0ae39a073f"},{url:"assets/images/player-backgrounds/17.jpg",revision:"d363a4b8256115c7505a420ca6a55aae"},{url:"assets/images/player-backgrounds/18.jpg",revision:"6c4e11b735bf6c95dfa5d47c3ae8e2e2"},{url:"assets/images/player-backgrounds/19.jpg",revision:"7fdf1e54a13c7e9d34ceb170fb47c26a"},{url:"assets/images/player-backgrounds/20.jpg",revision:"119ef99d06f809582244c2014ba005aa"},{url:"assets/images/player-backgrounds/21.jpg",revision:"b83a101c3a856de1728790666e4c0040"},{url:"assets/images/player-backgrounds/22.jpg",revision:"e6575b88d5aa774dc9b3c53e334c7c04"},{url:"assets/images/player-backgrounds/23.jpg",revision:"c78d6d5548d8e2ed7b6681a6a29f75bb"},{url:"assets/images/player-backgrounds/24.jpg",revision:"1da1420c684e6e51a0301b83544cf08c"},{url:"assets/images/player-backgrounds/25.jpg",revision:"aa51d71045e5f5cc9d3b89daa344b917"},{url:"assets/images/player-backgrounds/26.jpg",revision:"a8deb2d94eb69f1ccaaede00ba5bb6b7"},{url:"assets/images/player-backgrounds/27.jpg",revision:"5dde7e046f56139835c5db0c397ea0bd"},{url:"assets/images/player-backgrounds/28.jpg",revision:"a8027e60652ba8b43f436aba7895a82c"},{url:"assets/images/player-backgrounds/29.jpg",revision:"e0b12e01312c0e627fb133726e44da8e"},{url:"assets/images/player-backgrounds/30.jpg",revision:"b1841274afaa34e3f2c73a0bf6546c83"},{url:"assets/images/player-backgrounds/31.jpg",revision:"89a95df22ca39eb75cf5be6ba869223e"},{url:"assets/images/player-backgrounds/32.jpg",revision:"04aae5ba779d6f5637e40c9da4952e57"},{url:"assets/images/player-backgrounds/33.jpg",revision:"cb273547824cbd6adbd3dc4a19e3741c"},{url:"assets/images/player-backgrounds/34.jpg",revision:"772bdfc97346e0f4466db4f23aaa986f"},{url:"assets/images/player-backgrounds/35.jpg",revision:"08635247d80c6eada10efd122a0233ae"},{url:"assets/images/player-backgrounds/36.jpg",revision:"d941cbfec1db86258d3131c664c6c606"},{url:"assets/images/player-backgrounds/37.jpg",revision:"4f79166b5886629699c8914996dae8ec"},{url:"assets/images/player-backgrounds/38.jpg",revision:"428d6030a438a79fda9c3b891c49ab7e"},{url:"assets/images/player-backgrounds/39.jpg",revision:"81a7227fee4c963573dbd748066e79e4"},{url:"assets/images/player-backgrounds/40.jpg",revision:"e59c8f21613f90767eacfcf35a1827d2"},{url:"assets/images/player-backgrounds/41.jpg",revision:"63aeaea733070316bff748bc113a4a46"},{url:"assets/images/player-backgrounds/42.jpg",revision:"d1875f1d0349c573d3e8cb91f2aadc33"},{url:"assets/images/player-backgrounds/43.jpg",revision:"e64ed14afdc88195682716c677108b80"},{url:"assets/images/player-backgrounds/44.jpg",revision:"0c29f86f731632a6ac52703b68ffa274"},{url:"assets/images/player-backgrounds/45.jpg",revision:"6b061167c6e71f473ee9adc45a7dbf7c"},{url:"assets/images/player-backgrounds/46.jpg",revision:"d24c8fbd847cba6e0e99c85218daa430"},{url:"assets/images/player-backgrounds/47.jpg",revision:"9a907a8ecadc4889f604b0a00564d1f9"},{url:"assets/images/player-backgrounds/48.jpg",revision:"aaf24d179484067bf4bab284c52456dd"},{url:"assets/images/player-backgrounds/49.jpg",revision:"0d6cffc1fe9c516400a904f8cea606b3"},{url:"assets/images/player-backgrounds/50.jpg",revision:"dde138765e318791b3e236ab985f9e98"},{url:"manifest.webmanifest",revision:"21c3c4b595428a1101afb41f3b759796"}],{}),s.cleanupOutdatedCaches(),s.registerRoute(new s.NavigationRoute(s.createHandlerBoundToURL("index.html"),{denylist:[/^\/api/]}))}));
