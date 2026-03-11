import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, Unlock } from 'lucide-react';

const PurgeButton = ({ onPurge }: { onPurge: () => void }) => {
    const [isArmed, setIsArmed] = useState(false); // 翻盖状态

    return (
        <div className="fixed bottom-10 right-10 z-[110] flex flex-col items-center">
            {/* 翻盖警示灯 */}
            <div className={`w-2 h-2 rounded-full mb-2 ${isArmed ? 'bg-red-500 animate-ping' : 'bg-red-900'}`} />

            <div className="relative group">
                {/* 保护盖 (Cover) */}
                <motion.div
                    animate={{ rotateX: isArmed ? -110 : 0 }}
                    transition={{ type: "spring", stiffness: 100 }}
                    onClick={() => setIsArmed(!isArmed)}
                    className="absolute inset-0 z-10 bg-red-900/80 border-2 border-red-500 flex items-center justify-center cursor-pointer origin-top"
                    style={{ transformStyle: 'preserve-3d' }}
                >
                    <ShieldAlert size={20} className="text-red-200" />
                </motion.div>

                {/* 内部按钮 (Internal Button) */}
                <button
                    onClick={() => {
                        if (isArmed) {
                            onPurge();
                            setIsArmed(false);
                        }
                    }}
                    className="w-16 h-16 bg-red-600 border-2 border-red-400 flex items-center justify-center shadow-[0_0_20px_rgba(239,68,68,0.5)] active:scale-90 transition-transform"
                >
                    <span className="text-[10px] font-black text-white leading-none text-center uppercase">
                        PRESS<br />PURGE
                    </span>
                </button>
            </div>

            <span className="mt-2 text-[8px] text-red-900 font-bold tracking-widest uppercase">
                {isArmed ? 'SYSTEM_ARMED' : 'VALVE_LOCKED'}
            </span>
        </div>
    );
};

export default PurgeButton;
