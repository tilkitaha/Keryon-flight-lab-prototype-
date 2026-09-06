const q=(s,r=document)=>r.querySelector(s);
const qa=(s,r=document)=>[...r.querySelectorAll(s)];
const world=q('.worldWrap');
const side=q('.side');
const log=q('#log');
const decisions=q('#decisions');
const scenario=q('#scenario');
if(!world||!side){console.warn('KERYON Resilience layer: host UI not found');}else{
  const layer=document.createElement('div');layer.className='resilience-layer';
  layer.innerHTML='<canvas class="resilience-fx" aria-hidden="true"></canvas><div class="resilience-banner"></div><div class="resilience-flash"></div>';
  world.appendChild(layer);
  const canvas=q('.resilience-fx',layer),ctx=canvas.getContext('2d'),banner=q('.resilience-banner',layer),flash=q('.resilience-flash',layer);
  const panel=document.createElement('section');panel.className='panel section resilience-panel';
  panel.innerHTML=`<h2>KERYON Disaster & Resilience</h2><div class="eventbuttons">
    <button class="eventbtn" data-event="relief"><strong>RELIEF DROP</strong><span>Inert emergency supply delivery</span></button>
    <button class="eventbtn" data-event="fire"><strong>URBAN FIRE / SMOKE</strong><span>Visibility and rerouting test</span></button>
    <button class="eventbtn" data-event="lightning"><strong>LIGHTNING CELL</strong><span>Weather shock and sensor disturbance</span></button>
    <button class="eventbtn" data-event="blackout"><strong>COMMS BLACKOUT</strong><span>Graceful autonomy degradation</span></button>
    <button class="eventbtn" data-event="debris"><strong>DEBRIS ZONE</strong><span>Obstacle avoidance visualization</span></button>
    <button class="eventbtn" data-event="evac"><strong>EVACUATION CORRIDOR</strong><span>Multi-UAV corridor monitoring</span></button>
  </div><div class="resilience-stats"><div class="resilience-stat"><div class="k">Events</div><div class="v" id="resEvents">0</div></div><div class="resilience-stat"><div class="k">Aid drops</div><div class="v" id="resDrops">0</div></div><div class="resilience-stat"><div class="k">Resilience</div><div class="v" id="resScore">100%</div></div></div><div class="resilience-replay"><button class="btn" id="resReplay">CINEMATIC REPLAY</button><button class="btn" id="resClear">CLEAR EVENTS</button></div><div class="resilience-note">All effects are synthetic disaster-response simulations. No weapon, targeting, strike or explosive-delivery logic is modeled.</div>`;
  side.insertBefore(panel,side.children[1]||null);
  const events=[];let drops=0,resilience=100,replayTimer=null,particles=[],running=true,last=performance.now();
  function resize(){const r=world.getBoundingClientRect(),dpr=Math.min(2,window.devicePixelRatio||1);canvas.width=Math.max(1,Math.round(r.width*dpr));canvas.height=Math.max(1,Math.round(r.height*dpr));canvas.style.width=r.width+'px';canvas.style.height=r.height+'px';ctx.setTransform(dpr,0,0,dpr,0,0)}
  new ResizeObserver(resize).observe(world);resize();
  function hostLog(text){if(log){const d=document.createElement('div');d.textContent=text;log.prepend(d);while(log.children.length>12)log.lastElementChild.remove()}}
  function aiDecision(title,text){if(decisions){const d=document.createElement('div');d.className='decision';d.innerHTML='<b>'+title+'</b><span>'+text+'</span>';decisions.prepend(d);while(decisions.children.length>7)decisions.lastElementChild.remove()}}
  function showBanner(text){banner.textContent=text;banner.classList.add('show');setTimeout(()=>banner.classList.remove('show'),2400)}
  function updateStats(){q('#resEvents').textContent=String(events.length);q('#resDrops').textContent=String(drops);q('#resScore').textContent=Math.max(0,Math.round(resilience))+'%'}
  function addMarker(x,y,text,warning=false,life=5000){const m=document.createElement('div');m.className='resilience-marker'+(warning?' warning':'');m.style.left=x+'%';m.style.top=y+'%';m.textContent=text;layer.appendChild(m);setTimeout(()=>m.remove(),life)}
  function addPulse(x,y){const p=document.createElement('div');p.className='resilience-pulse active';p.style.left=x+'%';p.style.top=y+'%';layer.appendChild(p);setTimeout(()=>p.remove(),2400)}
  function addSmoke(x,y,count=10){for(let i=0;i<count;i++){const s=document.createElement('div');s.className='resilience-smoke';s.style.left=(x+(Math.random()-0.5)*5)+'%';s.style.top=(y+(Math.random()-0.5)*5)+'%';s.style.animationDelay=(Math.random()*0.7)+'s';layer.appendChild(s);setTimeout(()=>s.remove(),6800)}}
  function addCrate(x=50){const c=document.createElement('div');c.className='resilience-crate drop';c.style.left=x+'%';c.style.top='18%';layer.appendChild(c);setTimeout(()=>c.remove(),3800)}
  function syncScenario(value){if(!scenario)return;scenario.value=value;scenario.dispatchEvent(new Event('change',{bubbles:true}))}
  function record(type,label){events.push({type,label,time:Date.now()});updateStats();showBanner(label)}
  function trigger(type,fromReplay=false){
    if(!fromReplay)record(type,{relief:'HUMANITARIAN RELIEF DROP',fire:'URBAN FIRE / SMOKE EVENT',lightning:'LIGHTNING CELL DETECTED',blackout:'COMMUNICATIONS BLACKOUT',debris:'DEBRIS ZONE DETECTED',evac:'EVACUATION CORRIDOR ACTIVE'}[type]);
    if(type==='relief'){drops++;resilience=Math.min(100,resilience+2);updateStats();addCrate(45+Math.random()*10);addPulse(50,76);addMarker(50,78,'AID PACKAGE // SAFE DROP',false,4200);hostLog('RELIEF // Inert emergency supply package released');aiDecision('NOEMA','Selected a synthetic relief drop zone and preserved separation from simulated buildings.');}
    if(type==='fire'){resilience-=7;syncScenario('urban');addSmoke(61,63,18);addMarker(61,66,'SMOKE PLUME // AVOID',true,6500);hostLog('ENV // Urban smoke plume injected');aiDecision('NOEMA','Visibility degraded. Fleet spacing increased and optical confidence reduced for the affected sector.');}
    if(type==='lightning'){resilience-=9;syncScenario('storm');flash.classList.remove('active');void flash.offsetWidth;flash.classList.add('active');for(let i=0;i<20;i++)particles.push({type:'rain',x:Math.random(),y:Math.random(),vx:-.001-Math.random()*.002,vy:.012+Math.random()*.018,life:1});hostLog('WX // Lightning cell shock injected');aiDecision('NOEMA','Transient sensor disturbance detected. Autonomy switched to conservative weather-resilience behavior.');}
    if(type==='blackout'){resilience-=12;syncScenario('link');addMarker(48,48,'LINK LOST // AUTONOMOUS HOLD',true,6000);for(let i=0;i<4;i++)addPulse(30+i*13,45+Math.sin(i)*8);hostLog('COMMS // Simulated network blackout');aiDecision('NOEMA','External link unavailable. Fleet entered bounded autonomous hold and maintained cooperative separation.');}
    if(type==='debris'){resilience-=5;for(let i=0;i<8;i++){const x=35+Math.random()*30,y=55+Math.random()*18;particles.push({type:'debris',x:x/100,y:y/100,vx:(Math.random()-.5)*.002,vy:-.002-Math.random()*.003,life:1});}addMarker(51,66,'DEBRIS FIELD // REROUTE',true,6000);hostLog('MAP // Synthetic debris field injected');aiDecision('NOEMA','Obstacle confidence increased. Route corridor shifted away from the synthetic debris field.');}
    if(type==='evac'){resilience=Math.min(100,resilience+4);for(let i=0;i<5;i++){const x=28+i*10,y=69-i*4;addMarker(x,y,'SAFE '+(i+1),false,7000);if(i<4){const l=document.createElement('div');l.className='resilience-gridline';l.style.left=x+'%';l.style.top=y+'%';l.style.width='70px';l.style.transform='rotate(-22deg)';layer.appendChild(l);setTimeout(()=>l.remove(),7000)}}hostLog('CIV // Synthetic evacuation corridor activated');aiDecision('NOEMA','Fleet reassigned to corridor observation, traffic awareness and communications relay roles.');}
    updateStats();
  }
  qa('.eventbtn',panel).forEach(b=>b.addEventListener('click',()=>trigger(b.dataset.event)));
  q('#resClear').addEventListener('click',()=>{events.length=0;drops=0;resilience=100;particles=[];qa('.resilience-marker,.resilience-pulse,.resilience-crate,.resilience-smoke,.resilience-gridline',layer).forEach(n=>n.remove());updateStats();showBanner('RESILIENCE EVENTS CLEARED');hostLog('SYS // Disaster & Resilience event layer cleared')});
  q('#resReplay').addEventListener('click',()=>{if(!events.length){showBanner('NO EVENTS TO REPLAY');return}clearInterval(replayTimer);const copy=events.slice(-6);let i=0;showBanner('CINEMATIC EVENT REPLAY');hostLog('REPLAY // Replaying recent resilience events');replayTimer=setInterval(()=>{if(i>=copy.length){clearInterval(replayTimer);showBanner('REPLAY COMPLETE');return}trigger(copy[i++].type,true)},1800)});
  function draw(now){if(!running)return;const r=world.getBoundingClientRect(),w=r.width,h=r.height,dt=Math.min(.05,(now-last)/1000);last=now;ctx.clearRect(0,0,w,h);for(const p of particles){p.x+=p.vx*dt*60;p.y+=p.vy*dt*60;p.life-=dt*.28;if(p.type==='rain'){ctx.strokeStyle='rgba(160,205,230,'+Math.max(0,p.life*.45)+')';ctx.beginPath();ctx.moveTo(p.x*w,p.y*h);ctx.lineTo((p.x-.008)*w,(p.y-.025)*h);ctx.stroke()}else{ctx.fillStyle='rgba(220,178,95,'+Math.max(0,p.life*.8)+')';ctx.fillRect(p.x*w,p.y*h,3,3)}}particles=particles.filter(p=>p.life>0&&p.y<1.2);requestAnimationFrame(draw)}requestAnimationFrame(draw);
  updateStats();hostLog('SYS // Disaster & Resilience module armed');aiDecision('NOEMA','Disaster-response layer ready: relief logistics, weather shocks, communications loss, debris avoidance and evacuation monitoring.');
}
