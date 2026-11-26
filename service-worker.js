const CACHE="ww-static-v1";
const OFFLINE="/offline.html";
const ASSETS=["/offline.html","/favicon.svg","/assets/ww-platform.css","/assets/ww-platform.js"];
self.addEventListener("install",event=>event.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener("activate",event=>event.waitUntil((async()=>{for(const key of await caches.keys())if(key.startsWith("ww-static-")&&key!==CACHE)await caches.delete(key);await self.clients.claim()})()));
self.addEventListener("fetch",event=>{
 const req=event.request;
 if(req.method!=="GET"||new URL(req.url).origin!==self.location.origin)return;
 if(req.mode==="navigate"){
   // Live pages are ALWAYS network-first and never cached.
   event.respondWith(fetch(req).catch(async()=>await caches.match(OFFLINE)||new Response("Offline",{status:503})));return;
 }
 const p=new URL(req.url).pathname;
 if(!ASSETS.includes(p))return;
 event.respondWith(fetch(req).then(res=>{if(res.ok){const copy=res.clone();event.waitUntil(caches.open(CACHE).then(c=>c.put(req,copy)))}return res}).catch(()=>caches.match(req)));
});