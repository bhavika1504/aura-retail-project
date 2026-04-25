/* ====================================================
   AURA OS — Team SoloMid
   OOP Design Patterns Dashboard · Warm Light Theme
   ==================================================== */
const{useState,useEffect,useCallback,useRef,useMemo}=React;

// ── helpers ──────────────────────────────────────
const ts=()=>{const d=new Date();return`${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2,'0')}`};
const uid=()=>Math.random().toString(36).slice(2,8).toUpperCase();

// ── SINGLETON: EventBus ──────────────────────────
class EventBus{
  static _i=null;_s={};
  constructor(){if(EventBus._i)return EventBus._i;EventBus._i=this;}
  static get(){if(!EventBus._i)new EventBus();return EventBus._i;}
  sub(t,fn){(this._s[t]??=[]).push(fn);return()=>this.unsub(t,fn);}
  unsub(t,fn){this._s[t]=(this._s[t]??[]).filter(h=>h!==fn);}
  pub(t,p={}){const e={...p,type:t,time:ts(),id:uid()};(this._s[t]??[]).forEach(h=>{try{h(e)}catch(_){}});}
  totalSubs(){return Object.values(this._s).reduce((a,b)=>a+b.length,0);}
}
const bus=EventBus.get();

// ── PATTERN: State ────────────────────────────────
const KSTATES={
  active:{key:'active',label:'Active',emoji:'🟢',cls:'a-s',clst:'a-s-t',btnCls:'to-a',
    canBuy:(q,c)=>true,desc:'Full operation — all systems go.',color:'var(--success)'},
  maintenance:{key:'maintenance',label:'Maintenance',emoji:'🔧',cls:'m-s',clst:'m-s-t',btnCls:'to-m',
    canBuy:()=>false,desc:'Purchases suspended, restock allowed.',color:'var(--warn)'},
  emergency:{key:'emergency',label:'Emergency',emoji:'🚨',cls:'e-s',clst:'e-s-t',btnCls:'to-e',
    canBuy:(q,c)=>q<=2,desc:'All items capped at 2 units/txn.',color:'var(--wine)'},
  power_saving:{key:'power_saving',label:'Power Saving',emoji:'🌙',cls:'p-s',clst:'p-s-t',btnCls:'to-p',
    canBuy:(q,c)=>true,desc:'Low-power standby, auto-wakes.',color:'var(--blue-d)'},
};

// ── PATTERN: Strategy ─────────────────────────────
const STRATS={
  standard:{key:'standard',nm:'Standard',emoji:'💵',cls:'std',desc:'No adjustment · base price only',
    calc:(b,q,ctx)=>+(b*q).toFixed(2)},
  discount:{key:'discount',nm:'Discount 20%',emoji:'🏷',cls:'dis',desc:'−20% · +5% premium tier bonus',
    calc:(b,q,ctx)=>{let r=.2;if(ctx.tier==='premium')r+=.05;return+(b*q*(1-r)).toFixed(2);}},
  emergency:{key:'emergency',nm:'Emergency',emoji:'⚠️',cls:'emr',desc:'Essential ×1.0 · Non-essential ×1.5',
    calc:(b,q,ctx)=>+(b*q*(ctx.cat==='essential'?1.0:1.5)).toFixed(2)},
};

// ── PATTERN: Chain of Responsibility ──────────────
const HANDLERS=[
  {id:'retry',emoji:'🔄',nm:'RetryHandler',    cls:'retry',desc:'Retry dispense × 3'},
  {id:'recal',emoji:'⚙️',nm:'RecalibrationHandler',cls:'recal',desc:'Recalibrate motor/sensor'},
  {id:'tech', emoji:'📟',nm:'TechnicianAlert',  cls:'tech', desc:'Alert on-site technician'},
];

// ── Inventory seed ─────────────────────────────────
const SEED=[
  {id:'MED001',nm:'Paracetamol 500mg',cat:'essential',qty:50,res:0,hw:0,price:25,max:50},
  {id:'MED002',nm:'Vitamin C Tablets',cat:'general',  qty:30,res:0,hw:0,price:80,max:30},
  {id:'FOOD01',nm:'Energy Bar',        cat:'essential',qty:40,res:0,hw:0,price:45,max:40},
  {id:'FOOD02',nm:'Mineral Water 1L',  cat:'essential',qty:100,res:0,hw:0,price:20,max:100},
  {id:'LUX01', nm:'Luxury Chocolate',  cat:'premium',  qty:15,res:0,hw:0,price:350,max:15},
  {id:'MISC01',nm:'Hand Sanitizer',    cat:'general',  qty:25,res:0,hw:0,price:60,max:25},
];

// ── Pattern badges ────────────────────────────────
const PBADGES=[
  {pc:'p-obs',ic:'👁️',nm:'Observer',          dc:'EventBus subscribe/publish'},
  {pc:'p-sin',ic:'🔮',nm:'Singleton',          dc:'Single EventBus instance'},
  {pc:'p-sta',ic:'🔄',nm:'State',              dc:'4 kiosk operating modes'},
  {pc:'p-str',ic:'📐',nm:'Strategy',           dc:'3 interchangeable pricing algos'},
  {pc:'p-fac',ic:'🏛️',nm:'Facade',             dc:'KioskInterface unified API'},
  {pc:'p-cmd',ic:'⚡',nm:'Command',            dc:'Purchase · Refund · Restock'},
  {pc:'p-mem',ic:'📸',nm:'Memento',            dc:'Atomic rollback snapshots'},
  {pc:'p-chn',ic:'⛓️',nm:'Chain of Resp.',     dc:'Hardware failure escalation'},
  {pc:'p-fly',ic:'🏭',nm:'Abstract Factory',   dc:'PharmacyKiosk · FoodKiosk'},
  {pc:'p-cmd',ic:'🎨',nm:'Decorator',          dc:'LoggingDecorator · TimingDecorator · ValidationDecorator'},
];

// ── Team ──────────────────────────────────────────
const TEAM=[
  {nm:'Devam Tanna',    av:'DT',avCls:'av1',role:'Developer'},
  {nm:'Kajal Valrani',  av:'KV',avCls:'av2',role:'Developer'},
  {nm:'Charmi Bhayani', av:'CB',avCls:'av3',role:'Developer'},
  {nm:'Bhavika Mulani', av:'BM',avCls:'av4',role:'Developer'},
];

// ── Toast ─────────────────────────────────────────
function useToast(){
  const[t,st]=useState([]);
  const add=useCallback((type,title,msg)=>{
    const item={id:Date.now(),type,title,msg};
    st(p=>[...p.slice(-4),item]);
    setTimeout(()=>st(p=>p.filter(x=>x.id!==item.id)),4200);
  },[]);
  const rm=useCallback(id=>st(p=>p.filter(x=>x.id!==id)),[]);
  return{toasts:t,add,rm};
}

function Toasts({toasts,rm}){
  const icons={success:'✅',error:'❌',warning:'⚠️',info:'ℹ️'};
  return(
    <div className="toast-wrap">
      {toasts.map(t=>(
        <div key={t.id} className={`toast ${t.type}`} onClick={()=>rm(t.id)}>
          <span style={{fontSize:'1rem',flexShrink:0}}>{icons[t.type]}</span>
          <div>
            <div style={{fontWeight:800,marginBottom:2}}>{t.title}</div>
            <div style={{fontSize:'.66rem',opacity:.8}}>{t.msg}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ════════════════════════════════════════════════
// WELCOME SPLASH — shows on every page load
// ════════════════════════════════════════════════
function WelcomeSplash({onEnter}){
  const[visible,setVisible]=useState(true);
  const enter=()=>{setVisible(false);setTimeout(onEnter,350);};

  if(!visible)return null;

  return(
    <div className="splash-overlay" style={{animation:'overlay-in .4s ease forwards'}}>
      <div className="splash-card">
        {/* Header */}
        <div className="splash-header">
          <div className="splash-team-badge">⚡ Team SoloMid</div>
          <div className="splash-title">AURA OS</div>
          <div className="splash-sub">Retail Kiosk Intelligence System</div>
          <div className="splash-sub" style={{marginTop:6,fontSize:'.78rem',color:'rgba(255,255,255,.65)'}}>
            Central Management Console
          </div>
          <div className="splash-heart">❤️</div>
        </div>

        {/* Body */}
        <div className="splash-body">
          <div className="splash-label">Created with ❤️ by</div>

          <div className="member-grid">
            {TEAM.map((m,i)=>(
              <div key={m.nm} className="member-card" style={{animationDelay:`${.1+i*.1}s`}}>
                <div className={`member-av ${m.avCls}`}>{m.av}</div>
                <div>
                  <div className="member-name">{m.nm}</div>
                  <div className="member-init" style={{fontFamily:'var(--mono)',fontSize:'.58rem',color:'var(--t3)'}}>{m.role}</div>
                </div>
              </div>
            ))}
          </div>

          <div style={{textAlign:'center',fontSize:'.67rem',color:'var(--t3)',marginBottom:18,fontFamily:'var(--mono)',letterSpacing:'1px'}}>
            Enterprise Retail System · 2025
          </div>

          <button className="splash-enter-btn" onClick={enter}>
            <span>🚀</span>
            <span>Enter Dashboard</span>
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Nav items ──────────────────────────────────────
const NAV=[
  {id:'dash',label:'Dashboard',  icon:'📊',sec:'MONITOR'},
  {id:'txn', label:'Transactions',icon:'⚡',sec:'OPERATE'},
  {id:'inv', label:'Inventory',  icon:'📦',sec:'OPERATE'},
  {id:'kiosk',label:'Kiosk Screen',  icon:'📱',sec:'OPERATE'},
  {id:'hw',  label:'Hardware',   icon:'⛓️',sec:'OPERATE'},
];


// ════════════════════════════════════════════════
// ROOT APP
// ════════════════════════════════════════════════
function App(){
  const[showSplash,setShowSplash]=useState(true);
  const[page,setPage]=useState('dash');
  const[mode,setMode]=useState(KSTATES.active);
  const[strat,setStrat]=useState('standard');
  const[inv,setInv]=useState([]);
  const[txns,setTxns]=useState([]);
  const[kiosks,setKiosks]=useState([]);
  const[activeKiosk,setActiveKiosk]=useState({id:'PHARM-001',type:'PharmacyKiosk',location:'City Hospital'});
  const[events,setEvts]=useState([
    {id:'e0',time:'--:--:--',kind:'mc',type:'Network',msg:'Connecting to Aura Kiosk Backend...'},
  ]);
  const[mems,setMems]=useState([]);

  const fetchKiosks = useCallback(async () => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/kiosks');
      if (res.ok) {
        const data = await res.json();
        setKiosks(data);
      }
    } catch(e) {}
  }, []);

  const switchKiosk = useCallback(async (id) => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/kiosk/select', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ id })
      });
      if (res.ok) {
        const data = await res.json();
        fetchState();
        fetchInv();
      }
    } catch(e) {}
  }, []);

  // Fetch logic
  const fetchState = useCallback(async () => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/state');
      if (res.ok) {
        const data = await res.json();
        setMode(KSTATES[data.mode] || KSTATES.active);
        setStrat(data.strat || 'standard');
        setTxns(data.txns || []);
        setActiveKiosk({id: data.id, type: data.type, location: data.location});
      }
    } catch(e) {}
  }, []);

  const fetchInv = useCallback(async () => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/inventory');
      if (res.ok) {
        const data = await res.json();
        setInv(data);
      }
    } catch(e) {}
  }, []);

  useEffect(() => {
    fetchKiosks();
    fetchState();
    fetchInv();
    const id = setInterval(() => { fetchState(); fetchInv(); }, 1500);
    return () => clearInterval(id);
  }, [fetchState, fetchInv, fetchKiosks]);
  const{toasts,add:toast,rm:toastRm}=useToast();

  // THEME — persists across refresh
  const[theme,setTheme]=useState(()=>localStorage.getItem('aura-theme')||'light');
  useEffect(()=>{
    document.documentElement.setAttribute('data-theme',theme);
    localStorage.setItem('aura-theme',theme);
  },[theme]);
  const toggleTheme=useCallback(()=>setTheme(t=>t==='light'?'dark':'light'),[]);

  // DECORATOR chain log state
  const[decLog,setDecLog]=useState([]);
  const[decActive,setDecActive]=useState(null); // which wrapper is lit
  const[lastMs,setLastMs]=useState(null);

  // ── DUMMY OPERATION: Automated Walkthrough ──────
  const[demoStep,setDemoStep]=useState(null);
  
  const runDummyDemo=useCallback(async()=>{
    if(page!=='kiosk') setPage('kiosk');
    
    const steps=[
      {t:'USER INTERACTION', msg:'Customer selects Paracetamol (Essential)...', wait:1500},
      {t:'SYSTEM CHECK',     msg:'Validating kiosk operational mode... ACTIVE.', wait:1800},
      {t:'PRICING ENGINE',   msg:'Applying active pricing policy for category...', wait:1800},
      {t:'SECURITY',         msg:'Validating purchase constraints...', wait:2000},
      {t:'SYSTEM BACKUP',    msg:'Creating recovery snapshot before commit...', wait:1800},
      {t:'HARDWARE OP',      msg:'Authorizing payment and dispensing item...', wait:2000},
      {t:'NETWORK',          msg:'Syncing data with central dashboard...', wait:1500},
    ];

    for(const s of steps){
      setDemoStep(s);
      if(s.t==='HARDWARE OP'){
        // Trigger the actual purchase logic using the first available product in current kiosk
        const firstProd = inv[0];
        if(firstProd) {
          doTxn('purchase',{pid:firstProd.id, qty:1, amount:firstProd.price, cat:firstProd.cat});
        }
      }
      await new Promise(r=>setTimeout(r,s.wait));
    }
    setDemoStep({t:'TRANSACTION COMPLETE', msg:'Thank you! Live stock and revenue updated.'});
    setTimeout(()=>setDemoStep(null),4000);
  },[page, doTxn]);

  // Simulate decorator chain animation for any command type
  const runDecChain=useCallback(async(cmdName,cat='purchase',cb)=>{
    setDecLog([]);
    const layers=[
      {id:'tim',label:'TimingDecorator',   color:'var(--violet,#a855f7)',tag:'Timing',   show: cat==='purchase'},
      {id:'log',label:'LoggingDecorator',  color:'var(--blue-d,#00c8ff)',tag:'Logging',  show: true},
      {id:'val',label:'ValidationDecorator',color:'var(--warn,#8B6914)',tag:'Validation',show: cat==='purchase'},
      {id:'cmd',label:cmdName,             color:'var(--success,#4A7C59)',tag:'Command',  show: true},
    ].filter(l=>l.show);

    const push=(msg,cls='mc')=>setDecLog(p=>[...p,{id:uid(),time:ts(),kind:cls,type:'Decorator',msg}]);
    const t0=performance.now();

    // PRE-phase — outer to inner
    for(const l of layers.slice(0,-1)){
      setDecActive(l.id);
      await new Promise(r=>setTimeout(r,480));
      push(`[${l.label}] PRE → calling inner.execute()…`,'mc');
    }
    // Core command
    setDecActive('cmd');
    await new Promise(r=>setTimeout(r,420));
    push(`[${cmdName}] execute() — business logic running`,'tx');
    const ok=await cb(); // actual state mutation
    push(`[${cmdName}] → ${ok!==false?'✅ SUCCESS':'❌ FAILED'}`,'tx');
    await new Promise(r=>setTimeout(r,350));

    // POST-phase — inner to outer
    const postLayers=[...layers.slice(0,-1)].reverse();
    for(const l of postLayers){
      setDecActive(l.id);
      await new Promise(r=>setTimeout(r,400));
      push(`[${l.label}] POST ← result propagated up`,'rb');
    }

    const elapsed=+(performance.now()-t0).toFixed(1);
    setLastMs(elapsed);
    push(`[TimingDecorator] Total wall-clock: ${elapsed} ms ⏱`,'mc');
    setDecActive(null);
  },[]);

  const addEvt=useCallback((kind,type,msg)=>{
    setEvts(p=>[...p,{id:uid(),time:ts(),kind,type,msg}]);
    bus.pub(type,{msg});
  },[]);

  const modeChange=useCallback(async(next)=>{
    try {
      const res = await fetch('http://127.0.0.1:5000/api/mode', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ mode: next.key })
      });
      if(res.ok){ fetchState(); toast('info','Mode Transition',`Kiosk now in ${next.label} mode.`); }
    } catch(e){}
  },[fetchState,toast]);

  const stratChange = useCallback(async (k) => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/strategy', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ strat: k })
      });
      if (res.ok) {
        setStrat(k);
        toast('info', 'Strategy Updated', STRATS[k].desc);
      }
    } catch(e) {}
  }, [toast]);

  const doTxn=useCallback(async(type,data)=>{
    const urlMap = {
      purchase: '/api/purchase',
      refund: '/api/refund',
      restock: '/api/restock',
      undo: '/api/undo'
    };
    
    if(type==='purchase'){
       runDecChain('PurchaseCommand','purchase', async () => {
         try {
           const res = await fetch(`http://127.0.0.1:5000${urlMap[type]}`, {
             method: 'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)
           });
           if (!res.ok) {
             const j = await res.json();
             toast('error', 'Purchase Denied', j.error || 'Server rejected transaction');
             return false;
           }
           fetchInv(); fetchState();
           toast('success', 'Purchase Complete', `${data.qty}x ${data.pid}`);
           return true;
         } catch(e) { return false; }
       });
    } else {
       try {
         const res = await fetch(`http://127.0.0.1:5000${urlMap[type]}`, {
           method: 'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data||{})
         });
         if (!res.ok) { 
            const j = await res.json();
            toast('error', 'Action failed', j.error || 'Check server logs'); 
            return; 
         }
         fetchInv(); fetchState();
         toast('success', `Action Complete: ${type}`);
       } catch(e) {}
    }
  },[fetchState, fetchInv, runDecChain, toast]);

  const revenue=useMemo(()=>txns.filter(t=>t.type==='purchase').reduce((s,t)=>s+t.amount,0),[txns]);
  const totalQty=useMemo(()=>inv.reduce((s,p)=>s+p.qty,0),[inv]);
  const lowStk=useMemo(()=>inv.filter(p=>Math.max(0,p.qty-p.res-p.hw)<=5).length,[inv]);
  const purCount=txns.filter(t=>t.type==='purchase').length;
  const latestEvt=events[events.length-1];

  return(
    <>
      {showSplash&&<WelcomeSplash onEnter={()=>setShowSplash(false)}/>}

      <div className="app">
        {/* Sidebar */}
        <aside className="sb">
          <div className="sb-logo">
            <div className="logo-n">AURA OS</div>
            <div className="logo-t">Kiosk Intelligence</div>
          </div>
          <div className="sb-team">⚡ Team SoloMid</div>
          
          <div style={{padding:'0 16px', marginBottom: 12}}>
            <div className="nav-sec" style={{marginBottom: 8}}>SELECT KIOSK</div>
            <select 
              className="finp fsel" 
              style={{width:'100%', padding:'8px', fontSize:'.7rem'}}
              value={activeKiosk.id}
              onChange={(e) => switchKiosk(e.target.value)}
            >
              {kiosks.map(k => (
                <option key={k.id} value={k.id}>{k.type} ({k.id})</option>
              ))}
            </select>
          </div>

          <div className="kchip" style={{cursor:'default'}}>
            <span className={`kchip-dot ${mode.key}`}/>
            <div style={{flex:1,minWidth:0}}>
              <div className="kchip-id">{activeKiosk.id}</div>
              <div className="kchip-mode">{mode.label} Mode</div>
            </div>
            <span>{mode.emoji}</span>
          </div>
          <nav className="sb-nav">
            {['MONITOR','OPERATE','SYSTEM'].map(sec=>(
              <div key={sec}>
                <div className="nav-sec">{sec}</div>
                {NAV.filter(n=>n.sec===sec).map(n=>(
                  <div key={n.id} className={`nav-btn${page===n.id?' on':''}`} onClick={()=>setPage(n.id)}>
                    <span className="nav-ic">{n.icon}</span>
                    <span>{n.label}</span>
                    {n.id==='txn'&&txns.length>0&&<span className="nav-badge">{txns.length}</span>}
                  </div>
                ))}
              </div>
            ))}
          </nav>
          <div className="sb-foot">
            <div className="sb-ver">AURA OS v2.0 · Professional Edition · Team SoloMid</div>
          </div>
        </aside>

        {/* Main content */}
        <div className="main">
          {/* Topbar */}
          <header className="topbar">
            <div>
              <div className="tb-t">{NAV.find(n=>n.id===page)?.label||'Dashboard'} — <span style={{color:'var(--t3)'}}>{activeKiosk.location}</span></div>
              <div className="tb-s">{activeKiosk.type} · {NAV.find(n=>n.id===page)?.sec||''} · Team SoloMid</div>
            </div>
            <div className="tb-r">
              {latestEvt&&(
                <div className="ticker">
                  <span className="tick-d"/>
                  <span className="tick-t">{latestEvt.type}: {latestEvt.msg}</span>
                </div>
              )}
              <span className={`mpill ${mode.key}`}>{mode.label}</span>
              {txns.length>0&&<button className="btn btn-sec btn-sm" onClick={()=>doTxn('undo',{})}>↩ Undo</button>}
              <button className="btn btn-pri btn-sm" onClick={runDummyDemo} style={{boxShadow:'0 4px 15px rgba(107,48,53,0.3)'}}>🚀 Start Demo</button>
              <button className="theme-toggle" onClick={toggleTheme} title={`Switch to ${theme==='light'?'dark':'light'} mode`}>
                <span>{theme==='light'?'🌙':'☀️'}</span>
                <span>{theme==='light'?'Dark Mode':'Light Mode'}</span>
              </button>
            </div>
          </header>

          {/* Pages */}
          <main className="page">
            {page==='dash'&&<DashPage mode={mode} inv={inv} txns={txns} evts={events} strat={strat} mems={mems} revenue={revenue} totalQty={totalQty} lowStk={lowStk} purCount={purCount} onMode={modeChange} onStrat={stratChange}/>}
            {page==='txn' &&<TxnPage  mode={mode} inv={inv} strat={strat} txns={txns} mems={mems} doTxn={doTxn} decLog={decLog} decActive={decActive} lastMs={lastMs}/>}
            {page==='inv' &&<InvPage  inv={inv} strat={strat}/>}
            {page==='kiosk'&&<KioskPage inv={inv} strat={strat} demoStep={demoStep} doTxn={doTxn}/>}
            {page==='hw'  &&<HwPage   addEvt={addEvt} toast={toast}/>}
          </main>
        </div>
      </div>

      <Toasts toasts={toasts} rm={toastRm}/>
    </>
  );
}

// ════════════════════════════════════════════════
// DASHBOARD
// ════════════════════════════════════════════════
function DashPage({mode,inv,txns,evts,strat,mems,revenue,totalQty,lowStk,purCount,onMode,onStrat}){
  return(
    <div className="fade">
      <div className="stats mb5">
        <Stat cls="s-blue"    iCls="si-blue"    ic="📦" vc="c-blue"    v={totalQty}              lbl="Total Stock Units"  badge={`${inv.length} SKUs`} bc="bg-flat"/>
        <Stat cls="s-cream"   iCls="si-cream"   ic="⚡" vc="c-tan"     v={purCount}              lbl="Total Purchases"    badge={purCount?`+${purCount}`:'None'} bc={purCount?'bg-up':'bg-flat'}/>
        <Stat cls="s-success" iCls="si-success" ic="₹" vc="c-success"  v={`${revenue.toFixed(0)}`} lbl="Revenue (₹)"     badge="LIVE" bc="bg-up"/>
        <Stat cls="s-wine"    iCls="si-wine"    ic="⚠️" vc="c-wine"    v={lowStk}                lbl="Critical Stock"     badge={lowStk?'Alert':'All OK'} bc={lowStk?'bg-down':'bg-flat'}/>
      </div>

      <div className="g32 mb5">
        <div className="card">
          <div className="ch">
            <span className="ct">⚙️ Kiosk Operating Mode</span>
            <span className={`mpill ${mode.key}`}>{mode.label}</span>
          </div>
          <div className="cb"><StateMachine mode={mode} onMode={onMode}/></div>
        </div>
        <div className="card tan">
          <div className="ch">
            <span className="ct">📡 Live System Monitor</span>
            <span style={{fontSize:'.65rem',color:'var(--t3)'}}>{evts.length} events</span>
          </div>
          <div className="cb"><EvFeed evts={evts}/></div>
        </div>
      </div>

      <div className="g23 mb5">
        <div className="card">
          <div className="ch">
            <span className="ct">📸 State Recovery Snapshots</span>
            <span style={{fontSize:'.65rem',color:'var(--t3)'}}>{mems.length} active</span>
          </div>
          <div className="cb">
            {!mems.length
              ?<div className="empty"><div className="empty-ic">📸</div><div className="empty-t">No active snapshots. Make a purchase to see one!</div></div>
              :<div className="mem-list">{mems.map(m=>(
                <div key={m.id} className="mem">
                  <span className="mem-ic">📸</span>
                  <div style={{flex:1}}>
                    <div className="mem-id">TXN-{m.id}</div>
                    <div className="mem-d">{m.pid} · qty: {m.qty} · ₹{m.amount}</div>
                  </div>
                  <div className="mem-t">{m.time}</div>
                </div>
              ))}</div>
            }
          </div>
        </div>
        <div className="card">
          <div className="ch">
            <span className="ct">📐 Pricing Policy Management</span>
          </div>
          <div className="cb"><StratPanel strat={strat} onStrat={onStrat}/></div>
        </div>
      </div>
    </div>
  );
}

function Stat({cls,iCls,ic,vc,v,lbl,badge,bc}){
  return(
    <div className={`stat ${cls}`}>
      <div className={`s-ic ${iCls}`}>{ic}</div>
      <div className={`s-val ${vc}`}>{v}</div>
      <div className="s-lbl">{lbl}</div>
      <span className={`s-badge ${bc}`}>{badge}</span>
    </div>
  );
}

function StateMachine({mode,onMode}){
  const states=Object.values(KSTATES);
  return(
    <div>
      <div className="sm-nodes">
        {states.map((s,i)=>(
          <React.Fragment key={s.key}>
            <div className="sm-node" onClick={()=>onMode(s)}>
              <div className={`sm-circ ${s.cls}${mode.key===s.key?' cur':''}`} title={s.desc}>{s.emoji}</div>
              <span className={`sm-lbl ${s.clst}`}>{s.label}</span>
            </div>
            {i<states.length-1&&<div className="sm-arrow">⟷</div>}
          </React.Fragment>
        ))}
      </div>
      <p style={{textAlign:'center',fontSize:'.62rem',color:'var(--t3)',marginBottom:10}}>Click any state node to trigger a transition</p>
      <div className="sm-btns">
        {states.filter(s=>s.key!==mode.key).map(s=>(
          <button key={s.key} className={`sm-btn ${s.btnCls}`} onClick={()=>onMode(s)}>
            <span>{s.emoji}</span><span>→ {s.label}</span>
            <span style={{marginLeft:'auto',fontSize:'.57rem',opacity:.65}}>{s.desc}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function EvFeed({evts}){
  const ref=useRef(null);
  useEffect(()=>{if(ref.current)ref.current.scrollTop=ref.current.scrollHeight;},[evts]);
  if(!evts.length)return<div className="empty"><div className="empty-ic">📡</div><div className="empty-t">No events yet</div></div>;
  return(
    <div className="ef" ref={ref}>
      {evts.slice(-30).map(e=>(
        <div key={e.id} className={`ev ${e.kind}`}>
          <span className="ev-time">{e.time}</span>
          <div><div className="ev-type">{e.type}</div><div className="ev-msg">{e.msg}</div></div>
        </div>
      ))}
    </div>
  );
}

function StratPanel({strat,onStrat}){
  const[base,setBase]=useState(100);
  const[cat,setCat]=useState('general');
  const s=STRATS[strat];
  const price=s.calc(parseFloat(base)||0,1,{cat,tier:'standard'});
  return(
    <div>
      <div className="strats">
        {Object.values(STRATS).map(s=>(
          <div key={s.key} className={`strat ${s.cls}${strat===s.key?' sel':''}`} onClick={()=>onStrat(s.key)}>
            <div className="strat-ic">{s.emoji}</div>
            <div className="strat-nm">{s.nm}</div>
            <div className="strat-dc">{s.desc}</div>
          </div>
        ))}
      </div>
      <div className="pr-result">
        <div style={{display:'flex',alignItems:'flex-end',gap:10,flexWrap:'wrap'}}>
          <div>
            <div className="pr-lbl">Base Price (₹)</div>
            <input type="number" className="pr-inp" value={base} min="0" onChange={e=>setBase(e.target.value)}/>
          </div>
          <div>
            <div className="pr-lbl">Category</div>
            <select className="finp fsel" style={{width:115,padding:'6px 28px 6px 10px'}} value={cat} onChange={e=>setCat(e.target.value)}>
              <option value="essential">Essential</option>
              <option value="general">General</option>
              <option value="premium">Premium</option>
            </select>
          </div>
        </div>
        <div style={{textAlign:'right'}}>
          <div className="pr-val-lbl">{s.nm} price</div>
          <div className="pr-val">₹{price}</div>
        </div>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════
// DECORATOR CHAIN VISUALIZER COMPONENT
// ════════════════════════════════════════════════
const DEC_LAYERS=[
  {id:'tim',emoji:'⏱',label:'Network Ping',  sub:'Measuring latency',  purchaseOnly:true},
  {id:'log',emoji:'📋',label:'Audit Trail',  sub:'Generating compliance log',   purchaseOnly:false},
  {id:'val',emoji:'✅',label:'Verification',sub:'Validating security token',  purchaseOnly:true},
  {id:'cmd',emoji:'⚡',label:'Hardware Trigger',   sub:'Executing machine instruction',       purchaseOnly:false,isCore:true},
];

function DecoratorChain({decActive,decLog,lastMs,strat}){
  const logRef=useRef(null);
  useEffect(()=>{if(logRef.current)logRef.current.scrollTop=logRef.current.scrollHeight;},[decLog]);
  const idle=!decActive&&decLog.length===0;

  return(
    <div className="card mb5" style={{border:'1.5px solid var(--border-b)'}}>
      <div className="ch">
        <span className="ct">
          ⚙️ Diagnostic Pipeline — Live Execution
        </span>
        {lastMs!=null&&(
          <span style={{fontFamily:'var(--mono)',fontSize:'.7rem',color:'var(--success)',fontWeight:800,display:'flex',alignItems:'center',gap:5}}>
            ⏱ {lastMs} ms total
          </span>
        )}
      </div>
      <div className="cb">
        {/* Layer stack visual */}
        <div style={{display:'flex',alignItems:'center',gap:0,marginBottom:14,overflowX:'auto',paddingBottom:4}}>
          {/* Wrapper nesting labels */}
          {DEC_LAYERS.map((l,i)=>{
            const active=decActive===l.id;
            const colors={
              tim:{border:'var(--tan)',bg:'rgba(155,138,102,.08)',ac:'rgba(155,138,102,.22)'},
              log:{border:'var(--blue-d)',bg:'rgba(155,180,192,.08)',ac:'rgba(155,180,192,.22)'},
              val:{border:'var(--warn)',bg:'rgba(139,105,20,.07)',ac:'rgba(139,105,20,.2)'},
              cmd:{border:'var(--success)',bg:'rgba(74,124,89,.07)',ac:'rgba(74,124,89,.2)'},
            };
            const c=colors[l.id];
            const isDark=document.documentElement.getAttribute('data-theme')==='dark';
            return(
              <React.Fragment key={l.id}>
                <div style={{
                  padding:'12px 15px',borderRadius:12,minWidth:130,textAlign:'center',
                  border:`2px solid ${c.border}`,
                  background:active?c.ac:c.bg,
                  transition:'all .3s',
                  boxShadow:active?`0 0 18px ${c.border}40`:'none',
                  transform:active?'scale(1.05)':'scale(1)',
                  flexShrink:0,
                  position:'relative',
                }}>
                  {active&&<div style={{position:'absolute',top:-7,left:'50%',transform:'translateX(-50%)',
                    background:c.border,color:'#fff',fontSize:'.52rem',fontWeight:900,padding:'1px 7px',
                    borderRadius:6,letterSpacing:'1px',textTransform:'uppercase',fontFamily:'var(--mono)',whiteSpace:'nowrap'}}>
                    ACTIVE
                  </div>}
                  <div style={{fontSize:'1.3rem',marginBottom:4}}>{l.emoji}</div>
                  <div style={{fontFamily:'var(--mono)',fontSize:'.6rem',fontWeight:800,color:c.border,letterSpacing:'.8px',marginBottom:2}}>{l.label}</div>
                  <div style={{fontSize:'.57rem',color:'var(--t3)'}}>{l.sub}</div>
                  {l.isCore&&<div style={{marginTop:4,fontSize:'.52rem',fontFamily:'var(--mono)',color:'var(--success)',fontWeight:800}}>CORE</div>}
                </div>
                {i<DEC_LAYERS.length-1&&(
                  <div style={{padding:'0 4px',color:'var(--t4)',fontSize:'.85rem',flexShrink:0,display:'flex',flexDirection:'column',alignItems:'center',gap:2}}>
                    <span style={{fontSize:'.5rem',color:'var(--t4)',fontFamily:'var(--mono)'}}>wraps</span>
                    <span>→</span>
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Architecture note */}
        <div style={{
          padding:'8px 12px',borderRadius:9,
          background:'var(--bg)',border:'1px solid var(--border)',
          fontSize:'.65rem',color:'var(--t3)',fontFamily:'var(--mono)',
          marginBottom:12,lineHeight:1.8
        }}>
          <span style={{color:'var(--blue-d)',fontWeight:700}}>Network Connected →</span>
          <span style={{color:'var(--tan)',fontWeight:700}}> Audit Synced →</span>
          <span style={{color:'var(--warn)',fontWeight:700}}> Token Verified →</span>
          <span style={{color:'var(--success)',fontWeight:700}}> Commanded Hardware</span>
        </div>

        {/* Decorator log feed */}
        {decLog.length>0?(
          <div ref={logRef} style={{
            maxHeight:120,overflowY:'auto',fontFamily:'var(--mono)',fontSize:'.64rem',
            background:'var(--bg)',border:'1px solid var(--border)',borderRadius:9,padding:'8px 12px',
            lineHeight:2.1
          }}>
            {decLog.map(e=>(
              <div key={e.id} style={{
                color:e.kind==='tx'?'var(--success)':e.kind==='rb'?'var(--tan)':'var(--blue-d)',
                animation:'sl-in .2s ease'
              }}>
                <span style={{color:'var(--t4)',marginRight:8}}>{e.time}</span>{e.msg}
              </div>
            ))}
          </div>
        ):(
          <div className="empty" style={{padding:'12px'}}>
            <div className="empty-ic" style={{fontSize:'1.2rem'}}>🎨</div>
            <div className="empty-t">Execute a Purchase to watch the Decorator chain animate in real time</div>
          </div>
        )}
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════
// TRANSACTIONS
// ════════════════════════════════════════════════
function TxnPage({mode,inv,strat,txns,mems,doTxn,decLog,decActive,lastMs}){
  const[pid,setPid]=useState('');
  const[qty,setQty]=useState(1);
  const[u,setU]=useState('USER001');
  const[rtid,setRtid]=useState('');
  const[ramt,setRamt]=useState('');
  const[rpid,setRpid]=useState('');
  const[rqty,setRqty]=useState(1);
  const[spid,setSpid]=useState('');
  const[sqty,setSqty]=useState(10);

  // Sync selection when inventory loads
  useEffect(() => {
    if (inv.length > 0) {
      if (!inv.find(p => p.id === pid)) setPid(inv[0].id);
      if (!inv.find(p => p.id === rpid)) setRpid(inv[0].id);
      if (!inv.find(p => p.id === spid)) setSpid(inv[0].id);
    }
  }, [inv]);

  const prod=inv.find(p=>p.id===pid);
  const avail=prod?Math.max(0,prod.qty-prod.res-prod.hw):0;
  const ctx={cat:prod?.cat||'general',tier:'standard'};
  const price=prod?STRATS[strat].calc(prod.price,parseInt(qty)||1,ctx):0;
  const denied=mode.canBuy(parseInt(qty)||1,prod?.cat)?null
    :mode.key==='maintenance'?'Kiosk is under maintenance — purchases suspended.'
    :'Emergency mode: ALL items limited to 2 units per transaction.';

  return(
    <div className="fade">
      <div className="sec-title">Transaction Processing Pipeline</div>

      {/* DECORATOR CHAIN VISUALIZER */}
      <DecoratorChain decActive={decActive} decLog={decLog} lastMs={lastMs} strat={strat}/>

      <div className="g2 mb5">
        <div className="card">
          <div className="ch"><span className="ct">🛒 Process New Transaction</span></div>
          <div className="cb">
            <div className="form">
              <div className="fg">
                <label className="flbl">Product</label>
                <select className="finp fsel" value={pid} onChange={e=>setPid(e.target.value)}>
                  {inv.map(p=><option key={p.id} value={p.id}>{p.nm} (avail: {Math.max(0,p.qty-p.res-p.hw)})</option>)}
                </select>
              </div>
              <div className="frow">
                <div className="fg"><label className="flbl">Quantity</label><input type="number" className="finp" min="1" value={qty} onChange={e=>setQty(e.target.value)}/></div>
                <div className="fg"><label className="flbl">User ID</label><input type="text" className="finp" value={u} onChange={e=>setU(e.target.value)}/></div>
              </div>
              {prod&&(
                <div className="finfo">
                  <span style={{display:'flex',alignItems:'center',gap:7}}>
                    <span className={`cat-tag c-${prod.cat}`}>{prod.cat}</span>
                    <span style={{color:'var(--t3)',fontSize:'.65rem'}}>avail:</span>
                    <strong style={{color:'var(--blue-d)',fontFamily:'var(--mono)'}}>{avail}</strong>
                  </span>
                  <span><span style={{color:'var(--t3)',fontSize:'.68rem'}}>Policy: </span><strong style={{color:'var(--tan)'}}>{STRATS[strat].nm}</strong></span>
                  <span style={{fontFamily:'var(--mono)',fontWeight:900,color:'var(--success)'}}>₹{price}</span>
                </div>
              )}
              {denied&&<div className="fwarn">⚠️ {denied}</div>}
              <button className="btn btn-pri btn-full" disabled={!!denied||avail<(parseInt(qty)||1)}
                onClick={()=>doTxn('purchase',{pid,qty:parseInt(qty)||1,amount:price,cat:prod?.cat})}>
                ⚡ Execute Transaction
              </button>
            </div>
          </div>
        </div>

        <div className="col">
          <div className="card wine">
            <div className="ch"><span className="ct">↩️ Process Refund</span></div>
            <div className="cb">
              <div className="form">
                <div className="frow">
                  <div className="fg"><label className="flbl">Transaction ID</label><input type="text" className="finp" placeholder="e.g. AB12CD" value={rtid} onChange={e=>setRtid(e.target.value)}/></div>
                  <div className="fg"><label className="flbl">Amount (₹)</label><input type="number" className="finp" min="0" value={ramt} onChange={e=>setRamt(e.target.value)}/></div>
                </div>
                <div className="frow">
                  <div className="fg"><label className="flbl">Product</label>
                    <select className="finp fsel" value={rpid} onChange={e=>setRpid(e.target.value)}>
                      {inv.map(p=><option key={p.id} value={p.id}>{p.nm}</option>)}
                    </select>
                  </div>
                  <div className="fg" style={{maxWidth:80}}><label className="flbl">Qty</label><input type="number" className="finp" min="1" value={rqty} onChange={e=>setRqty(e.target.value)}/></div>
                </div>
                <button className="btn btn-danger btn-full" onClick={()=>doTxn('refund',{tid:rtid,amount:parseFloat(ramt)||0,pid:rpid,qty:parseInt(rqty)||1})}>↩️ Issue Refund</button>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="ch"><span className="ct">📦 Process Restock</span></div>
            <div className="cb">
              <div className="form">
                <div className="frow">
                  <div className="fg"><label className="flbl">Product</label>
                    <select className="finp fsel" value={spid} onChange={e=>setSpid(e.target.value)}>
                      {inv.map(p=><option key={p.id} value={p.id}>{p.nm}</option>)}
                    </select>
                  </div>
                  <div className="fg" style={{maxWidth:90}}><label className="flbl">Qty to Add</label><input type="number" className="finp" min="1" value={sqty} onChange={e=>setSqty(e.target.value)}/></div>
                </div>
                <button className="btn btn-emer btn-full" disabled={mode.key!=='active'&&mode.key!=='maintenance'}
                  onClick={()=>doTxn('restock',{pid:spid,qty:parseInt(sqty)||1})}>📦 Update Inventory</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="ch">
          <span className="ct">📋 Operations Log</span>
          <span style={{fontSize:'.65rem',color:'var(--t3)'}}>{txns.length} operations</span>
        </div>
        <div className="cb">
          {!txns.length
            ?<div className="empty"><div className="empty-ic">📋</div><div className="empty-t">No operations executed yet.</div></div>
            :<div className="txs">{[...txns].reverse().map(t=>(
              <div key={t.id} className="tx">
                <span className={`txbadge b-${t.type==='purchase'?'pur':t.type==='refund'?'ref':t.type==='restock'?'res':'und'}`}>{t.type}</span>
                <div className="tx-info"><div className="tx-d">{t.desc}</div><div className="tx-t">{t.time} · KIOSK-01</div></div>
                {t.amount!=null&&<span className="tx-amt">₹{t.amount?.toFixed(2)}</span>}
              </div>
            ))}</div>
          }
        </div>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════
// INVENTORY
// ════════════════════════════════════════════════
function InvPage({inv,strat}){
  return(
    <div className="fade">
      <div className="sec-title">Live Inventory Tracker</div>
      <div className="card">
        <div className="ch"><span className="ct">📦 Stock Catalogue</span><span style={{fontSize:'.65rem',color:'var(--t3)',fontFamily:'var(--mono)'}}>{inv.length} products</span></div>
        <div style={{overflowX:'auto'}}>
          <table className="itbl">
            <thead>
              <tr><th>Product</th><th>Category</th><th>Total</th><th>Reserved</th><th>HW Fault</th><th>Available</th><th>Level</th><th>Base ₹</th><th>Live ₹</th></tr>
            </thead>
            <tbody>
              {inv.map(p=>{
                const av=Math.max(0,p.qty-p.res-p.hw);
                const pct=Math.round((av/p.max)*100);
                const bc=pct>50?'hi':pct>20?'md':'lo';
                const live=STRATS[strat].calc(p.price,1,{cat:p.cat,tier:'standard'});
                return(
                  <tr key={p.id}>
                    <td><div style={{fontWeight:700,fontSize:'.77rem'}}>{p.nm}</div><div style={{fontSize:'.6rem',color:'var(--t3)',fontFamily:'var(--mono)'}}>{p.id}</div></td>
                    <td><span className={`cat-tag c-${p.cat}`}>{p.cat}</span></td>
                    <td style={{fontFamily:'var(--mono)',fontWeight:700}}>{p.qty}</td>
                    <td style={{color:'var(--warn)',fontFamily:'var(--mono)'}}>{p.res}</td>
                    <td style={{color:'var(--wine)',fontFamily:'var(--mono)'}}>{p.hw}</td>
                    <td style={{fontFamily:'var(--mono)',fontWeight:800,color:av<=5?'var(--wine)':av<=15?'var(--warn)':'var(--success)'}}>{av}</td>
                    <td><div style={{display:'flex',alignItems:'center',gap:7}}><div className="sbar-w"><div className={`sbar ${bc}`} style={{width:`${pct}%`}}/></div><span style={{fontSize:'.6rem',color:'var(--t3)'}}>{pct}%</span></div></td>
                    <td style={{fontFamily:'var(--mono)',color:'var(--t2)'}}>₹{p.price}</td>
                    <td style={{fontFamily:'var(--mono)',fontWeight:800,color:'var(--tan-d)'}}><strong>₹{live}</strong></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════
// HARDWARE — Chain of Responsibility
// ════════════════════════════════════════════════
function HwPage({addEvt,toast}){
  const[lit,setLit]=useState(null);
  const[log,setLog]=useState([]);
  const[running,setRunning]=useState(false);

  const simulate=useCallback(async(fix)=>{
    setRunning(true);setLog([]);setLit(null);
    addEvt('hw','HardwareFailureEvent','Dispenser fault detected — Chain of Responsibility initiated.');
    const push=(cls,txt)=>setLog(p=>[...p,{cls,txt}]);

    for(let i=0;i<HANDLERS.length;i++){
      const h=HANDLERS[i];
      setLit(h.id);
      await new Promise(r=>setTimeout(r,700));
      if(h.id==='retry'){
        push('lr','[RetryHandler] Attempt 1/3 … failed');
        push('lr','[RetryHandler] Attempt 2/3 … failed');
        push('lr','[RetryHandler] Attempt 3/3 … failed → escalating');
        if(fix==='retry'){push('ls-ok','[RetryHandler] ✅ Recovered on retry!');toast('success','Recovered','RetryHandler resolved the failure.');addEvt('tx','HardwareRecovered','Chain resolved at RetryHandler.');break;}
      } else if(h.id==='recal'){
        push('lv','[RecalibrationHandler] Recalibrating motor…');push('lv','[RecalibrationHandler] Sensor zeroed');
        if(fix==='recal'){push('ls-ok','[RecalibrationHandler] ✅ Recalibrated!');toast('success','Recovered','RecalibrationHandler resolved the failure.');addEvt('tx','HardwareRecovered','Chain resolved at RecalibrationHandler.');break;}
      } else if(h.id==='tech'){
        push('lp','[TechnicianAlert] 📟 Paging technician…');push('lp','[TechnicianAlert] HardwareFailureEvent → EventBus published');
        if(fix!=='none'){push('ls-ok','[TechnicianAlert] ✅ Technician resolved!');toast('success','Recovered','Technician resolved at site.');addEvt('tx','HardwareRecovered','Chain resolved by technician.');}
        else{push('lf','[TechnicianAlert] ❌ Chain exhausted — manual intervention required');toast('error','Chain Exhausted','All handlers failed. Manual intervention needed.');addEvt('hw','ChainExhausted','All handlers failed — kiosk flagged for maintenance.');}
        break;
      }
      await new Promise(r=>setTimeout(r,350));
    }
    setLit(null);setRunning(false);
  },[addEvt,toast]);

  return(
    <div className="fade">
      <div className="sec-title">Hardware Diagnostics</div>
      <div className="card mb5">
        <div className="ch"><span className="ct">⛓️ Automated Diagnostic Escalation</span></div>
        <div className="cb">
          <div className="chain">
            {HANDLERS.map((h,i)=>(
              <React.Fragment key={h.id}>
                <div className={`ch-node ${h.cls}${lit===h.id?' lit':''}`}>
                  <div className="ch-ic">{h.emoji}</div>
                  <div className="ch-nm">{h.nm}</div>
                  <div className="ch-dc">{h.desc}</div>
                </div>
                {i<HANDLERS.length-1&&<div className="ch-arrow">→</div>}
              </React.Fragment>
            ))}
          </div>
          <div style={{marginTop:14,display:'flex',alignItems:'center',gap:8,flexWrap:'wrap'}}>
            <span style={{fontSize:'.7rem',color:'var(--t3)'}}>Simulate failure, resolve at:</span>
            {HANDLERS.map(h=>(<button key={h.id} className="btn btn-sec btn-sm" disabled={running} onClick={()=>simulate(h.id)}>{h.emoji} {h.nm.replace('Handler','').replace('Technician','Tech').replace('Recalibration','Recal.')}</button>))}
            <button className="btn btn-danger btn-sm" disabled={running} onClick={()=>simulate('none')}>❌ Full Failure</button>
          </div>
          {log.length>0&&(<div className="flog">{log.map((l,i)=><div key={i} className={l.cls}>{l.txt}</div>)}</div>)}
        </div>
      </div>
      <div className="g2">
        <div className="card">
          <div className="ch"><span className="ct">🔧 SpiralDispenser</span></div>
          <div className="cb">
            {[['Type','SpiralDispenser','c-blue'],['Status','OPERATIONAL','c-success'],['Motor','Active · 48 RPM','c-tan'],['Sensor','Infrared — OK','c-success']].map(([k,v,c])=>(
              <div key={k} className="hw-row"><span className="hw-k">{k}</span><span className={`hw-v ${c}`}>{v}</span></div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="ch"><span className="ct">💳 Payment Processor</span></div>
          <div className="cb">
            {[['Provider','UPI + Card Gateway','c-wine'],['Status','ONLINE','c-success'],['Latency','~120ms','c-blue'],['Refund','Enabled','c-success']].map(([k,v,c])=>(
              <div key={k} className="hw-row"><span className="hw-k">{k}</span><span className={`hw-v ${c}`}>{v}</span></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}


// ════════════════════════════════════════════════
// KIOSK SIMULATOR (DUMMY OPERATION VIEW)
// ════════════════════════════════════════════════
function KioskPage({inv,strat,demoStep,doTxn}){
  const cats={essential:'🍱',general:'📦',premium:'💎',otc:'💊',prescription:'📜',controlled_substance:'⚠️'};
  
  return(
    <div className="fade" style={{display:'flex',justifyContent:'center',paddingTop:10}}>
      <div style={{position:'relative'}}>
        <div className="kiosk-sim-frame">
          <div className="kiosk-sim-screen">
            <header className="kiosk-sim-header">AURA KIOSK — Hospital Unit 01</header>
            
            <div className="kiosk-sim-body">
              <div style={{marginBottom:15}}>
                <div style={{fontSize:'.8rem',fontWeight:900,marginBottom:10,color: 'var(--t2)' }}>CHOOSE PRODUCT</div>
                <div className="kiosk-product-grid">
                  {inv.slice(0,4).map(p=>{
                    const live=STRATS[strat].calc(p.price,1,{cat:p.cat,tier:'standard'});
                    return(
                      <div key={p.id} className="kiosk-item" onClick={()=>!demoStep && doTxn('purchase',{pid:p.id,qty:1,amount:live,cat:p.cat})}>
                        <div className="kiosk-item-img">{cats[p.cat]||'📦'}</div>
                        <div className="kiosk-item-name">{p.nm}</div>
                        <div className="kiosk-item-price">₹{live}</div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div style={{background:'var(--bg2)',borderRadius:12,padding:12,border:'1px dashed var(--border-b)'}}>
                <div style={{fontSize:'.6rem',fontWeight:800,color:'var(--t3)',marginBottom:6,textTransform:'uppercase'}}>Payment Terminal</div>
                <div style={{display:'flex',gap:6}}>
                   {['💳','📱','⌚'].map(i=><div key={i} style={{width:35,height:25,background:'var(--card)',borderRadius:4,display:'flex',alignItems:'center',justifyContent:'center',fontSize:'.8rem',border:'1px solid var(--border)'}}>{i}</div>)}
                </div>
              </div>
            </div>

            <footer style={{padding:12,background:'var(--bg)',borderTop:'1px solid var(--border)',textAlign:'center'}}>
              <div style={{fontSize:'.55rem',color:'var(--t4)',fontFamily:'var(--mono)'}}>ID: PHARM-001 | SYS: AURA OS 2.0</div>
            </footer>

            {/* Simulation Overlay */}
            {demoStep && (
              <div className="demo-step-overlay">
                <div className="demo-step-title">{demoStep.t}</div>
                <div className="demo-step-msg">{demoStep.msg}</div>
              </div>
            )}
          </div>
        </div>

        <div style={{textAlign:'center',marginTop:20,fontSize:'.7rem',color:'var(--t3)',fontFamily:'var(--mono)'}}>
          Physical Kiosk Hardware Target: RoboticArmDispenser v4
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App/>);

