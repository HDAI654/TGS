const API_URL = "http://localhost:8080/graphql";
const PAGE_SIZE = 24;

const categories = [
  ["top-news","Top News","broadcast"],["news","News","newspaper"],["music","Music","music-note-beamed"],
  ["sports","Sports","trophy"],["auto","Auto","car-front"],["animation","Animation","palette"],
  ["business","Business","briefcase"],["classic","Classic","vinyl"],["comedy","Comedy","emoji-laughing"],
  ["cooking","Cooking","egg-fried"],["culture","Culture","bank"],["documentary","Documentary","camera-reels"],
  ["education","Education","mortarboard"],["entertainment","Entertainment","stars"],["family","Family","people"],
  ["general","General","tv"],["kids","Kids","balloon"],["legislative","Legislative","building"],
  ["lifestyle","Lifestyle","heart"],["movies","Movies","film"],["outdoor","Outdoor","tree"],
  ["relax","Relax","cloud-sun"],["religious","Religious","book"],["series","Series","collection-play"],
  ["science","Science","flask"],["shop","Shop","bag"],["travel","Travel","airplane"],
  ["weather","Weather","cloud-sun-fill"]
].map(([id,label,icon]) => ({id,label,icon}));

let storedFavorites = [];
try {
  const parsedFavorites = JSON.parse(localStorage.getItem("worldtv-favs") || "[]");
  storedFavorites = Array.isArray(parsedFavorites) ? parsedFavorites.map(String) : [];
} catch {
  storedFavorites = [];
}

const state = {
  theme: localStorage.getItem("worldtv-theme") || "dark",
  sidebarCollapsed: localStorage.getItem("worldtv-sidebar") === "true",
  mobileNavigationOpen: false,
  discovery: { mode:null,title:"",items:[],total:0,offset:0,limit:PAGE_SIZE,loading:false,error:null,requestId:0 },
  selectedChannel: null,
  selectedSourceIndex: 0,
  favorites: storedFavorites,
  player: { hls:null, playing:false }
};

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}
function initials(name) {
  return String(name || "?").split(/\s+/).filter(Boolean).slice(0,2).map(x=>x[0]).join("").toUpperCase();
}
function sourceType(url) {
  try {
    const path = new URL(url).pathname.toLowerCase();
    return path.includes(".m3u8") ? "HLS" : "DIRECT";
  } catch { return "STREAM"; }
}
function validUrl(url) {
  try { const u = new URL(url); return ["http:","https:"].includes(u.protocol); } catch { return false; }
}
function normalizeChannel(raw) {
  if (!raw || !raw.id || !raw.name) return null;
  return {
    id:String(raw.id), name:String(raw.name), language:raw.language || null,
    countryCode:raw.countryCode || null,
    category:raw.category ? {id:Number(raw.category.id) || null,name:raw.category.name || null} : {id:null,name:null},
    urls:Array.isArray(raw.urls) ? raw.urls.filter(validUrl) : []
  };
}
async function gql(query, variables={}, signal) {
  const controller = signal ? null : new AbortController();
  const timeout = setTimeout(() => controller?.abort(), 10000);
  try {
    const res = await fetch(API_URL, {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({query,variables}), signal:signal || controller.signal
    });
    if (!res.ok) throw new Error(`HTTP_${res.status}`);
    const json = await res.json();
    if (json.errors?.length) throw new Error("GRAPHQL_ERROR");
    return json.data;
  } catch (e) {
    if (e.name === "AbortError") throw e;
    throw e;
  } finally { clearTimeout(timeout); }
}

let activeRequest = null;
const api = {
  async channels(search, limit=PAGE_SIZE, offset=0, signal) {
    activeRequest?.abort();
    activeRequest = signal ? null : new AbortController();
    const requestSignal = signal || activeRequest.signal;
    const data = await gql(`query Channels($limit:Int!,$offset:Int!,$search:String){
      channels(limit:$limit,offset:$offset,search:$search){items{id name language countryCode urls category{id name}} total limit offset}
    }`, {limit,offset,search}, requestSignal);
    return {...(data?.channels || {}), items:(data?.channels?.items || []).map(normalizeChannel).filter(Boolean)};
  },
  async channel(id, signal) {
    const data = await gql(`query Channel($id:UUID!){
      channel(id:$id){id name language countryCode urls category{id name}}
    }`, {id}, signal);
    return normalizeChannel(data?.channel);
  },
  async countries(search="", limit=PAGE_SIZE, offset=0, signal) {
    const data = await gql(`query Countries($limit:Int!,$offset:Int!,$search:String){
      countries(limit:$limit,offset:$offset,search:$search){items{countryCode countryName timezone hasChannels channelCount} total limit offset}
    }`, {limit,offset,search}, signal);
    return data?.countries || {items:[],total:0,limit,offset};
  },
  async allCountries(signal) {
    const data = await gql(`query AllCountries{
      allCountries{items{countryCode countryName timezone hasChannels channelCount}}
    }`, {}, signal);
    return data?.allCountries?.items || [];
  },
  async count(signal) {
    const data = await gql(`query Count{
      count{channels countries}
    }`, {}, signal);
    return data?.count || null;
  }
};

function setApiStatus(online) {
  $("#apiDot").classList.toggle("online", online);
  $("#apiStatus").textContent = online ? "API connected" : "API disconnected";
}
function renderCategories() {
  const html = categories.map(c => `<button class="nav-item category-item" data-category="${c.id}" title="${c.label}">
    <i class="bi bi-${c.icon}"></i><span>${c.label}</span></button>`).join("");
  $("#categoryList").innerHTML = html;
}
function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  localStorage.setItem("worldtv-theme",state.theme);
  $$(".topbar-actions [data-action=theme] i,#themeIcon").forEach(i => i.className = `bi bi-${state.theme==="dark"?"sun":"moon"}`);
}
function applySidebar() {
  $("#sidebar").classList.toggle("collapsed",state.sidebarCollapsed);
  localStorage.setItem("worldtv-sidebar",state.sidebarCollapsed);
}
function openMobile() {
  state.mobileNavigationOpen = true; $("#sidebar").classList.add("mobile-open"); $("#mobileBackdrop").classList.add("show");
}
function closeMobile() {
  state.mobileNavigationOpen = false; $("#sidebar").classList.remove("mobile-open"); $("#mobileBackdrop").classList.remove("show");
}
function showToast(message) {
  const t=$("#toast");t.textContent=message;t.classList.add("show");clearTimeout(showToast.timer);
  showToast.timer=setTimeout(()=>t.classList.remove("show"),2800);
}
function openModal(id){ const el=$(id);el.hidden=false;document.body.style.overflow="hidden"; }
function closeModal(id){
  const el=$(id);el.hidden=true;
  if (id==="#playerModal") stopPlayer();
  if (!$("#discoveryModal").hidden || !$("#playerModal").hidden) return;
  document.body.style.overflow="";
}
function renderSkeletons() { $("#discoveryBody").innerHTML=`<div class="channel-grid">${Array.from({length:8},()=>'<div class="skeleton"></div>').join("")}</div>`; }
function renderChannels(items) {
  if (!items.length) {
    $("#discoveryBody").innerHTML=`<div class="empty"><i class="bi bi-broadcast"></i><strong>No channels found</strong><span>Try a country, channel name, language, or category.</span></div>`;
    return;
  }
  $("#discoveryBody").innerHTML=`<div class="channel-grid">${items.map(c=>`
    <button class="channel-card" data-channel-id="${escapeHtml(c.id)}">
      <div class="channel-icon">${escapeHtml(initials(c.name))}</div>
      <div class="card-title">${escapeHtml(c.name)}</div>
      <div class="card-meta">${escapeHtml([c.countryCode,c.language].filter(Boolean).join(" · ") || "Global")}</div>
      <div class="card-foot"><span>${escapeHtml(c.category?.name || "General")}</span>
        <span class="bookmark ${state.favorites.includes(c.id)?"saved":""}"><i class="bi bi-bookmark${state.favorites.includes(c.id)?"-fill":""}"></i> ${c.urls.length} source${c.urls.length===1?"":"s"}</span>
      </div>
    </button>`).join("")}</div>`;
}
function renderPagination() {
  const d=state.discovery, pages=Math.max(1,Math.ceil(d.total/d.limit)), page=Math.floor(d.offset/d.limit)+1;
  $("#pagination").innerHTML=pages>1?`<button class="page-btn" data-page="-1" ${page<=1?"disabled":""}>Previous</button>
    <span class="page-info">${page} / ${pages}</span>
    <button class="page-btn" data-page="1" ${page>=pages?"disabled":""}>Next</button>`:"";
}
async function discover({title,query=null,mode="search",offset=0}) {
  const requestId = state.discovery.requestId + 1;
  state.discovery={...state.discovery,title,query,mode,offset,loading:true,error:null,requestId};
  $("#discoveryTitle").textContent=title;$("#discoveryMeta").textContent="Loading directory…";renderSkeletons();renderPagination();openModal("#discoveryModal");
  try {
    let result;
    if(mode==="countries") {
      const items = await api.allCountries();
      result = {items, total:items.length, limit:items.length, offset:0};
    } else {
      // The API intentionally returns null for an empty/None channel search.
      // Only issue channel requests when there is a real search/category query.
      if(!query || !String(query).trim()) {
        state.discovery={...state.discovery,items:[],total:0,loading:false};
        $("#discoveryMeta").textContent="";
        $("#discoveryBody").innerHTML=`<div class="empty"><i class="bi bi-search"></i><strong>Search for a channel</strong><span>Enter a channel name, country, language, or category.</span></div>`;
        renderPagination();
        return;
      }
      result=await api.channels(String(query).trim(),PAGE_SIZE,offset);
    }
    if(state.discovery.requestId !== requestId) return;
    state.discovery={...state.discovery,items:result.items,total:result.total,loading:false};
    $("#discoveryMeta").textContent=`${result.total || 0} result${result.total===1?"":"s"}`;
    if(mode==="countries") renderCountries(result.items); else renderChannels(result.items);
    renderPagination();setApiStatus(true);
  } catch(e) {
    if(e.name==="AbortError" || state.discovery.requestId !== requestId) return;
    state.discovery.error=e;$("#discoveryMeta").textContent="";
    $("#discoveryBody").innerHTML=`<div class="empty"><i class="bi bi-wifi-off"></i><strong>Network unavailable</strong><span>We couldn't reach the TV directory. Check that the local API is running and try again.</span><br><button class="primary-btn" data-retry="1" style="margin-top:18px">Retry</button></div>`;
    setApiStatus(false);
  }
}
function renderCountries(items) {
  if(!items.length){$("#discoveryBody").innerHTML=`<div class="empty"><i class="bi bi-globe2"></i><strong>No countries found</strong><span>No countries match this discovery.</span></div>`;return;}
  $("#discoveryBody").innerHTML=`<div class="country-grid">${items.map(c=>`
    <button class="country-card" data-country="${escapeHtml(c.countryCode)}" data-country-name="${escapeHtml(c.countryName)}">
      <div class="channel-icon">${escapeHtml(c.countryCode || "??")}</div>
      <div class="card-title">${escapeHtml(c.countryName)}</div>
      <div class="card-meta">${escapeHtml(c.timezone || "Timezone unavailable")}</div>
      <div class="card-foot"><span>${c.hasChannels?"Channels available":"No channels"}</span><span>${c.channelCount ?? 0}</span></div>
    </button>`).join("")}</div>`;
}
async function openChannel(id) {
  try {
    const channel=state.discovery.items.find(c=>c.id===id) || await api.channel(id);
    if(!channel){showToast("Channel is unavailable.");return;}
    state.selectedChannel=channel;state.selectedSourceIndex=0;
    $("#playerTitle").textContent=channel.name;$("#playerSubtitle").textContent=[channel.countryCode,channel.category?.name].filter(Boolean).join(" · ");
    $("#playerMeta").innerHTML=[["Country",channel.countryCode],["Language",channel.language],["Category",channel.category?.name],["Channel ID",channel.id]].filter(x=>x[1]).map(x=>`<span>${escapeHtml(x[0])}: ${escapeHtml(x[1])}</span>`).join("");
    $("#sourceCount").textContent=`${channel.urls.length} source${channel.urls.length===1?"":"s"}`;
    $("#sourceList").innerHTML=channel.urls.length ? channel.urls.map((url,i)=>`<button class="source-option ${i===0?"active":""}" data-source="${i}">
      <i class="bi bi-${i===0?"record-circle":"circle"}"></i><span>Source ${i+1}</span><span class="source-type">${sourceType(url)}</span></button>`).join("") :
      `<div class="empty" style="padding:25px">No playable sources are available.</div>`;
    updateFavoriteButton();openModal("#playerModal");
    if(channel.urls.length) playSource(0);
  } catch { showToast("Couldn't load this channel."); }
}
function updateFavoriteButton(){
  const saved=state.favorites.includes(state.selectedChannel?.id),b=$("#favoriteBtn");
  b.classList.toggle("saved",saved);b.innerHTML=`<i class="bi bi-bookmark${saved?"-fill":""}"></i><span>${saved?"Saved":"Save"}</span>`;
}
function toggleFavorite(){
  if(!state.selectedChannel)return;
  const id=state.selectedChannel.id;
  state.favorites=state.favorites.includes(id)?state.favorites.filter(x=>x!==id):[...state.favorites,id];
  localStorage.setItem("worldtv-favs",JSON.stringify(state.favorites));$("#savedCount").textContent=state.favorites.length;updateFavoriteButton();showToast(state.favorites.includes(id)?"Channel saved":"Removed from saved");
}
function stopPlayer(){
  if(state.player.hls){state.player.hls.destroy();state.player.hls=null;}
  const v=$("#video");v.pause();v.removeAttribute("src");v.load();$("#playerOverlay").style.display="grid";
}
function playSource(index){
  const c=state.selectedChannel,url=c?.urls?.[index];if(!url)return;
  if(state.player.hls){state.player.hls.destroy();state.player.hls=null;}
  const v=$("#video");state.selectedSourceIndex=index;
  $$(".source-option").forEach((b,i)=>{b.classList.toggle("active",i===index);b.querySelector("i").className=`bi bi-${i===index?"record-circle":"circle"}`;});
  $("#playerOverlay").style.display="grid";$("#playerOverlay span").textContent="Connecting…";
  const hls = sourceType(url)==="HLS";
  if(hls && window.Hls?.isSupported()){
    const player=new Hls({enableWorker:true});state.player.hls=player;
    player.loadSource(url);player.attachMedia(v);
    player.on(Hls.Events.MANIFEST_PARSED,()=>{ $("#playerOverlay").style.display="none";v.play().catch(()=>{}); });
    player.on(Hls.Events.ERROR,(_,data)=>{if(data.fatal){$("#playerOverlay span").textContent="Stream unavailable — try another source.";showToast("Stream unavailable");}});
  } else {
    v.src=url;v.onloadedmetadata=()=>{$("#playerOverlay").style.display="none";v.play().catch(()=>{});};
    v.onerror=()=>{$("#playerOverlay span").textContent="Stream unavailable — try another source.";showToast("Stream unavailable");};
    if(sourceType(url)==="HLS" && v.canPlayType("application/vnd.apple.mpegurl")) v.load();
  }
}
async function loadStats(){
  try {
    const result = await api.count();
    if(!result) throw new Error("COUNT_UNAVAILABLE");
    $("#statChannels").textContent=result.channels ?? "—";
    $("#statCountries").textContent=result.countries ?? "—";
    setApiStatus(true);
  } catch {
    $("#statChannels").textContent="—";
    $("#statCountries").textContent="—";
    setApiStatus(false);
  }
}
function initEvents(){
  $("#brandToggle").onclick=()=>{ if(innerWidth<=800) closeMobile(); else {state.sidebarCollapsed=!state.sidebarCollapsed;applySidebar();} };
  $("#hamburger").onclick=openMobile;$("#mobileBackdrop").onclick=closeMobile;
  $("#searchForm").onsubmit=e=>{e.preventDefault();const q=$("#searchInput").value.trim();if(q)discover({title:`Search: ${q}`,query:q});};
  $("#favoriteBtn").onclick=toggleFavorite;
  document.addEventListener("keydown",e=>{
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();$("#searchInput").focus();}
    if(e.key==="Escape"){closeMobile();if(!$("#playerModal").hidden)closeModal("#playerModal");else if(!$("#discoveryModal").hidden)closeModal("#discoveryModal");}
  });
  document.addEventListener("click",e=>{
    const action=e.target.closest("[data-action]")?.dataset.action;
    if(action){
      if(["theme"].includes(action)){state.theme=state.theme==="dark"?"light":"dark";applyTheme();return;}
      if(["countries","saved","home"].includes(action)) closeMobile();
      if(action==="countries") discover({title:"Countries",mode:"countries"});
      else if(action==="saved") openSaved();
      else if(action==="home") {
        closeModal("#discoveryModal");
        $("#searchInput").value="";
      }
    }
    const cat=e.target.closest("[data-category]")?.dataset.category;
    if(cat){closeMobile();const c=categories.find(x=>x.id===cat);if(c) discover({title:c.label,query:c.label,mode:"category"});}
    const cid=e.target.closest("[data-channel-id]")?.dataset.channelId;if(cid)openChannel(cid);
    const country=e.target.closest("[data-country]");if(country){closeModal("#discoveryModal");discover({title:country.dataset.countryName,query:country.dataset.country,mode:"search"});}
    const source=e.target.closest("[data-source]")?.dataset.source;if(source!=null)playSource(Number(source));
    const page=e.target.closest("[data-page]")?.dataset.page;if(page){const next=state.discovery.offset+Number(page)*PAGE_SIZE;discover({...state.discovery,offset:next});}
    if(e.target.closest("[data-retry]"))discover({...state.discovery});
    const close=e.target.closest("[data-close]")?.dataset.close;if(close)closeModal(`#${close}Modal`);
  });
}
async function openSaved(){
  if(!state.favorites.length){
    state.discovery={...state.discovery,title:"Saved channels",mode:"saved",items:[],total:0,offset:0,limit:PAGE_SIZE,loading:false,error:null};
    $("#discoveryTitle").textContent="Saved channels";
    $("#discoveryMeta").textContent="";
    $("#discoveryBody").innerHTML=`<div class="empty"><i class="bi bi-bookmark"></i><strong>No saved channels</strong><span>Save a channel while watching it and it will appear here.</span></div>`;
    $("#pagination").innerHTML="";
    openModal("#discoveryModal");
    return;
  }
  state.discovery={...state.discovery,title:"Saved channels",mode:"saved",items:[],total:0,offset:0,limit:PAGE_SIZE};
  $("#discoveryTitle").textContent="Saved channels";$("#discoveryMeta").textContent="";openModal("#discoveryModal");renderSkeletons();
  const results=[];for(const id of state.favorites.slice(0,PAGE_SIZE)){try{const c=await api.channel(id);if(c)results.push(c)}catch{}}
  state.discovery.items=results;state.discovery.total=results.length;renderChannels(results);renderPagination();
}
function init(){
  renderCategories();applyTheme();applySidebar();$("#savedCount").textContent=state.favorites.length;initEvents();loadStats();
}
init();

