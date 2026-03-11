import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Clock, AlertTriangle, Activity } from 'lucide-react';

export interface TaskStepData {
    step_id: string;
    agent_type: string;
    goal: string;
    instructions: string;
    dependencies: string[];
    status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
    result?: any;
}

export interface TaskPlanData {
    goal: string;
    steps: TaskStepData[];
}

interface Props {
    plan: TaskPlanData | null;
}

const TaskPlanMonitor: React.FC<Props> = ({ plan }) => {
    if (!plan) return (
        <div className="flex flex-col items-center justify-center h-full opacity-20 pointer-events-none">
            <Activity size={48} className="mb-4 animate-pulse" />
            <p className="text-[10px] font-black tracking-[0.3em]">WAITING_FOR_NEURAL_PLAN...</p>
        </div>
    );

    const getStatusColor = (status: TaskStepData['status']) => {
        switch (status) {
            case 'COMPLETED': return 'text-green-400 border-green-500/50 bg-green-500/5';
            case 'IN_PROGRESS': return 'text-cyan-400 border-cyan-500/50 bg-cyan-500/20';
            case 'FAILED': return 'text-red-400 border-red-500/50 bg-red-500/10';
            default: return 'text-slate-500 border-slate-700/50 bg-slate-900/50';
        }
    };

    const getStatusIcon = (status: TaskStepData['status']) => {
        switch (status) {
            case 'COMPLETED': return <CheckCircle2 size={12} />;
            case 'IN_PROGRESS': return <Activity size={12} className="animate-spin" />;
            case 'FAILED': return <AlertTriangle size={12} />;
            default: return <Clock size={12} />;
        }
    };

    return (
        <div className="h-full flex flex-col p-4 bg-black/40 backdrop-blur-md border border-cyan-500/10 relative overflow-hidden">
            {/* Background Glitch Trace */}
            <div className="absolute inset-0 opacity-5 pointer-events-none">
                <div className="h-full w-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>
            </div>

            <header className="mb-4 border-b border-cyan-500/20 pb-2">
                <div className="flex justify-between items-end">
                    <h3 className="text-xs font-black tracking-widest text-cyan-400 uppercase">
                        Active_Plan: {plan.goal.substring(0, 40)}{plan.goal.length > 40 ? '...' : ''}
                    </h3>
                    <span className="text-[8px] text-cyan-800 tabular-nums">
                        {plan.steps.filter(s => s.status === 'COMPLETED').length}/{plan.steps.length} STEPS_LOCKED
                    </span>
                </div>
            </header>

            <div className="flex-1 overflow-y-auto pr-2 scrollbar-custom space-y-3 relative z-10">
                <AnimatePresence>
                    {plan.steps.map((step, index) => (
                        <motion.div
                            key={step.step_id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className={`p-3 border ${getStatusColor(step.status)} relative group transition-all duration-300`}
                        >
                            {/* Step Badge */}
                            <div className="absolute -top-2 -left-2 bg-black border border-inherit px-2 py-0.5 text-[8px] font-bold tracking-tighter">
                                STEP_{index + 1}
                            </div>

                            <div className="flex justify-between items-start mb-2">
                                <div className="flex items-center gap-2">
                                    <span className="text-[10px] font-black uppercase tracking-wider">{step.agent_type}</span>
                                    <div className="h-2 w-[1px] bg-white/10"></div>
                                    <span className="text-[10px] font-bold text-white/80">{step.goal}</span>
                                </div>
                                <div className="flex items-center gap-1 text-[9px] font-mono">
                                    {getStatusIcon(step.status)}
                                    <span className="opacity-70">{step.status}</span>
                                </div>
                            </div>

                            <p className="text-[9px] text-white/40 leading-relaxed italic line-clamp-2 transition-all group-hover:line-clamp-none">
                                {step.instructions}
                            </p>

                            {step.dependencies.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-inherit/20 flex gap-2">
                                    <span className="text-[8px] uppercase opacity-30 font-bold">Depends_On:</span>
                                    {step.dependencies.map(dep => (
                                        <span key={dep} className="text-[8px] bg-white/5 px-1 font-mono text-cyan-700">#{dep}</span>
                                    ))}
                                </div>
                            )}

                            {/* Progress bar for IN_PROGRESS */}
                            {step.status === 'IN_PROGRESS' && (
                                <motion.div 
                                    className="absolute bottom-0 left-0 h-0.5 bg-cyan-400"
                                    initial={{ width: '0%' }}
                                    animate={{ width: '100%' }}
                                    transition={{ duration: 15, ease: "linear" }}
                                />
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* Matrix Scanline Overlay */}
            <div className="fixed inset-0 pointer-events-none scanlines opacity-10"></div>
        </div>
    );
};

export default TaskPlanMonitor;
