import React, { useRef, useState, useEffect } from 'react';

interface DemoSandboxProps {
  uiSchema?: any;
}

const DemoSandbox: React.FC<DemoSandboxProps> = ({ uiSchema }) => {
  const sandboxRef = useRef<HTMLIFrameElement>(null);
  const [isAnnotationMode, setIsAnnotationMode] = useState(false);
  const [currentStyle, setCurrentStyle] = useState('government');
  
  // Presentation Coach States
  const [isCoachActive, setIsCoachActive] = useState(false);
  const [currentScriptIndex, setCurrentScriptIndex] = useState(0);
  const [coachTimer, setCoachTimer] = useState(0);

  // Simulated Presentation Guide (In real system, fetched from backend/AI)
  const presentationGuide = {
    timeline: [
      { time: 0, focus: "Overview", script: "各位评委好，现在进入系统的全景演示。本方案基于分布式 AI 架构，确保了业务逻辑的高可靠性。" },
      { time: 10, focus: "Scanner", script: "针对标书提到的安全性需求（第24页），我们的实时扫描模块实现了 100% 的抓标精度。" },
      { time: 25, focus: "Analytics", script: "此处的数据看板完美对齐了贵方对实时分析的要求。所有的关键绩效指标均可动态追溯。" },
      { time: 45, focus: "Closure", script: "总结而言，本系统不仅满足当前标书要求，更具备未来的平滑扩展能力。演示结束。" }
    ]
  };

  // Simulated Pain Points matching EXPANSION_RESULT
  const painPoints = [
    { id: 1, x: '20%', y: '15%', desc: '此处解决您提到的审批流转慢问题 (Fast-Approval Flow)' },
    { id: 2, x: '50%', y: '60%', desc: '100%匹配人脸抓标参数 ★' }
  ];

  const themes: Record<string, string> = {
    'government': '--brand-bg: #F4F7F9; --brand-primary: #003399; --brand-radius: 4px; --brand-text: #333333; --brand-surface: #FFFFFF; --brand-accent: #0288D1;',
    'sci-fi': '--brand-bg: #050510; --brand-primary: #00FFCC; --brand-radius: 0px; --brand-text: #FFFFFF; --brand-surface: #111122; --brand-accent: #A855F7;'
  };

  const injectStyles = () => {
    if (sandboxRef.current && sandboxRef.current.contentDocument) {
      const doc = sandboxRef.current.contentDocument;
      
      const existingStyle = doc.getElementById('dynamic-theme');
      if (existingStyle) existingStyle.remove();

      const styleTag = doc.createElement('style');
      styleTag.id = 'dynamic-theme';
      styleTag.textContent = `
        :root { ${themes[currentStyle]} }
        body { 
          background-color: var(--brand-bg) !important; 
          color: var(--brand-text) !important; 
          transition: background-color 0.5s ease, color 0.5s ease;
          margin: 0;
          font-family: system-ui, sans-serif;
        }
        .header { text-align: center; border-bottom: 2px solid var(--brand-primary); padding-bottom: 10px; margin-bottom: 15px; }
        .header h1 { font-size: 16px; color: var(--brand-primary); margin: 0; font-weight: 800; }
        .card { background: var(--brand-surface); padding: 15px; border-radius: var(--brand-radius); border-left: 4px solid var(--brand-accent); box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 12px; }
        .label { font-size: 10px; opacity: 0.7; text-transform: uppercase; margin-bottom: 4px; }
        .value { font-size: 24px; font-weight: 700; color: var(--brand-primary); }
        .scan-box { height: 120px; border: 2px dashed var(--brand-primary); border-radius: var(--brand-radius); margin-bottom: 15px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.02); }
      `;
      doc.head.appendChild(styleTag);
    }
  };

  // Coach logic effect
  useEffect(() => {
    let interval: any;
    if (isCoachActive) {
      interval = setInterval(() => {
        setCoachTimer(prev => prev + 1);
      }, 1000);
    } else {
      setCoachTimer(0);
      setCurrentScriptIndex(0);
    }
    return () => clearInterval(interval);
  }, [isCoachActive]);

  useEffect(() => {
    if (isCoachActive) {
      const currentStage = presentationGuide.timeline.findLast(step => coachTimer >= step.time);
      if (currentStage) {
        const index = presentationGuide.timeline.indexOf(currentStage);
        setCurrentScriptIndex(index);
      }
      if (coachTimer > 60) setIsCoachActive(false); // Auto stop after 60s for demo
    }
  }, [coachTimer, isCoachActive]);

  // Re-inject styles whenever language/style changes
  useEffect(() => {
    injectStyles();
  }, [currentStyle]);

  const generateSchemaHtml = () => {
    if (!uiSchema || !uiSchema.components) return '';
    const name = uiSchema?.canvas?.name || "PreBid Demo";
    
    let compsHtml = uiSchema.components.map((c: any) => {
      if (c.type === 'LiveFaceScanner') return '<div class="scan-box"><div style="color:var(--brand-primary); font-size:12px; font-weight:bold;">[ LIVE FEED ACTIVE ]</div></div>';
      if (c.type === 'DynamicScoreColumn') return '<div class="card"><div class="label">' + c.props.label + '</div><div class="value">' + c.props.value + '</div></div>';
      if (c.type === 'MetricList') {
        const itemsHtml = c.props.items.map((m: any) => '<div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px; border-bottom:1px solid rgba(0,0,0,0.05); padding-bottom:4px;"><span>' + m.label + '</span><strong>' + m.value + '</strong></div>').join('');
        return '<div class="card">' + itemsHtml + '</div>';
      }
      return '';
    }).join('');

    return `
      <!DOCTYPE html>
      <html>
        <head></head>
        <body style="padding: 16px;">
          <div class="header"><h1>${name}</h1></div>
          ${compsHtml}
        </body>
      </html>
    `;
  };

  const iframeContent = uiSchema ? generateSchemaHtml() : `
    <!DOCTYPE html>
    <html>
      <head></head>
      <body style="padding: 16px; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100vh;">
        <h2 style="color: var(--brand-primary); opacity: 0.5;">AWAITING SYNTHESIS...</h2>
      </body>
    </html>
  `;

    return (
    <div className="flex flex-col items-center justify-center w-full h-full p-4">
      {/* 9:16 Canvas Frame */}
      <div 
        className="relative shadow-[0_0_50px_rgba(0,0,0,0.8)] border-[12px] border-[#1e293b] rounded-[3rem] bg-black overflow-hidden"
        style={{ width: '360px', height: '640px' }}
      >
        {/* Iframe Sandbox Engine */}
        <iframe
          ref={sandboxRef}
          className="w-full h-full bg-white transition-all duration-700"
          srcDoc={iframeContent}
          sandbox="allow-scripts allow-same-origin"
          onLoad={injectStyles}
          title="Demo Sandbox"
        />

        {/* Dynamic Annotation Overlay */}
        {isAnnotationMode && (
          <div className="absolute inset-0 pointer-events-none z-10 transition-opacity duration-300">
            {painPoints.map((point) => (
              <div 
                key={point.id}
                style={{ top: point.y, left: point.x }}
                className="absolute pointer-events-auto group cursor-pointer"
              >
                <div className="flex items-center justify-center relative w-6 h-6">
                  <div className="absolute w-full h-full bg-red-500 rounded-full animate-ping opacity-75"></div>
                  <div className="relative w-3 h-3 bg-red-600 rounded-full border-2 border-white"></div>
                </div>
                
                <div className="absolute left-8 -top-2 w-48 bg-white text-slate-800 p-3 rounded-lg shadow-2xl text-xs font-bold tracking-tight opacity-0 scale-95 transition-all duration-300 group-hover:opacity-100 group-hover:scale-100 border-l-4 border-red-500 pointer-events-none origin-left">
                  {point.desc}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Presentation Coach Teleprompter */}
        {isCoachActive && (
          <div className="absolute bottom-6 left-6 right-6 bg-black/90 text-white p-4 rounded-2xl backdrop-blur-xl border border-white/10 shadow-2xl z-20 animate-in fade-in slide-in-from-bottom-5">
            <div className="flex justify-between items-center mb-3">
              <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400 flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                PRESENTATION_COACH
              </span>
              <span className="text-[10px] font-mono opacity-50">
                {Math.floor(coachTimer / 60)}:{(coachTimer % 60).toString().padStart(2, '0')}
              </span>
            </div>
            
            <div className="min-h-[60px] text-xs leading-relaxed font-medium mb-4 text-slate-100 italic transition-all duration-500">
              "{presentationGuide.timeline[currentScriptIndex]?.script}"
            </div>

            <div className="w-full bg-white/10 h-1 rounded-full overflow-hidden">
              <div 
                className="bg-emerald-500 h-full transition-all duration-1000 ease-linear" 
                style={{ width: `${(coachTimer / 60) * 100}%` }}
              ></div>
            </div>
            
            <div className="mt-4 flex gap-2">
              <button 
                onClick={() => setIsCoachActive(false)}
                className="text-[9px] font-black uppercase tracking-tighter bg-red-500 text-white px-3 py-1.5 rounded-md hover:bg-red-600 transition-colors"
              >
                TERMINATE_DEMO
              </button>
              <div className="flex-1"></div>
              <span className="text-[9px] font-bold opacity-40 uppercase">Stage: {presentationGuide.timeline[currentScriptIndex]?.focus}</span>
            </div>
          </div>
        )}
      </div>
      
      {/* Control Deck */}
      <div className="mt-8 flex gap-4">
        <button 
          onClick={() => setCurrentStyle('government')} 
          className={`px-6 py-2 rounded-md text-xs font-bold font-mono transition-all duration-300 ${currentStyle === 'government' ? 'bg-blue-600 text-white shadow-[0_0_15px_rgba(37,99,235,0.5)]' : 'border border-blue-500 text-blue-400 hover:bg-blue-900/40'}`}
        >
          GOV-BIZ
        </button>
        <button 
          onClick={() => setCurrentStyle('sci-fi')} 
          className={`px-6 py-2 rounded-md text-xs font-bold font-mono transition-all duration-300 ${currentStyle === 'sci-fi' ? 'bg-cyan-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.5)]' : 'border border-cyan-500 text-cyan-400 hover:bg-cyan-900/40'}`}
        >
          SCI-FI NEO
        </button>
        <div className="w-[1px] h-8 bg-slate-700 mx-2"></div>
        <button 
          onClick={() => setIsAnnotationMode(!isAnnotationMode)} 
          className={`px-6 py-2 rounded-md text-xs font-bold font-mono transition-all duration-300 flex items-center gap-2 ${isAnnotationMode ? 'bg-white text-black shadow-[0_0_15px_rgba(255,255,255,0.3)]' : 'border border-slate-500 text-slate-300 hover:bg-slate-800'}`}
        >
          {isAnnotationMode ? 'ANNOTATIONS_ON' : 'ANNOTATIONS_OFF'}
        </button>
        <button 
          onClick={() => setIsCoachActive(!isCoachActive)} 
          className={`px-6 py-2 rounded-md text-xs font-bold font-mono transition-all duration-300 flex items-center gap-2 ${isCoachActive ? 'bg-emerald-500 text-black' : 'bg-slate-800 text-emerald-400 border border-emerald-900/50 hover:bg-emerald-900/20'}`}
        >
          {isCoachActive ? 'STOP_COACH' : 'ACTIVATE_COACH'}
        </button>
      </div>
    </div>
  );
};

export default DemoSandbox;
