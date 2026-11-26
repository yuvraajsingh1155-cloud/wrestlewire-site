(()=>{"use strict";
const root=document.documentElement;let theme="dark";
try{theme=localStorage.getItem("ww.theme")||"dark"}catch{}
function current(){return theme==="system"?(matchMedia("(prefers-color-scheme: light)").matches?"light":"dark"):theme}
function renderTheme(){root.dataset.wwTheme=current();document.querySelectorAll("[data-ww-reader-theme]").forEach(b=>b.textContent="Theme: "+theme)}
renderTheme();
document.querySelectorAll("[data-ww-reader-theme]").forEach(b=>b.addEventListener("click",()=>{const options=["dark","light","system"];theme=options[(options.indexOf(theme)+1)%options.length];try{localStorage.setItem("ww.theme",theme)}catch{}renderTheme()}));
const url=location.pathname;
function readSaved(){try{const list=JSON.parse(localStorage.getItem("ww.saved")||"[]");return new Set(Array.isArray(list)?list:[])}catch{return new Set()}}
function sync(){const state=readSaved().has(url);document.querySelectorAll("[data-ww-reader-save]").forEach(b=>{b.setAttribute("aria-pressed",String(state));b.textContent=state?"★ Saved":"☆ Save"})}sync();
document.querySelectorAll("[data-ww-reader-save]").forEach(b=>b.addEventListener("click",()=>{const s=readSaved();if(s.has(url))s.delete(url);else s.add(url);try{localStorage.setItem("ww.saved",JSON.stringify([...s].slice(-200)))}catch{}sync()}));
document.querySelectorAll("[data-ww-reader-share]").forEach(b=>b.addEventListener("click",async()=>{try{if(navigator.share){await navigator.share({title:document.title,url:location.href});return}if(navigator.clipboard){await navigator.clipboard.writeText(location.href);b.textContent="✓ Copied link";setTimeout(()=>b.textContent="Share",2000)}}catch{}}));
const bar=document.getElementById("ww-reading-progress");if(bar){let scheduled=false;function update(){const max=document.documentElement.scrollHeight-innerHeight;bar.style.width=(max>0?Math.min(100,scrollY/max*100):100)+"%";scheduled=false}addEventListener("scroll",()=>{if(!scheduled){scheduled=true;requestAnimationFrame(update)}},{passive:true});update()}
if("serviceWorker" in navigator)addEventListener("load",()=>navigator.serviceWorker.register("/service-worker.js").catch(()=>{}));
})();