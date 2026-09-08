// network first, cache fallback: always fresh online, still opens on a train
const C='pattern-recall-v1';
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',function(e){
  if(e.request.method!=='GET') return;
  const u=new URL(e.request.url);
  if(u.origin!==self.location.origin) return;
  e.respondWith(fetch(e.request).then(function(r){
    const copy=r.clone(); caches.open(C).then(c=>c.put(e.request,copy)); return r;
  }).catch(function(){ return caches.match(e.request).then(function(m){ return m || caches.match('index.html'); }); }));
});
