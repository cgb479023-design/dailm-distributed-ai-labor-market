import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// 定义不同阶段的故障文本，模拟损坏
const corruptedTexts = [
    '#@@$%^^&',
    'G$&&_M%__DIRECTOR',
    'T@#K_S@##E$$',
    'T-A-S-K__S-U-C-C-E-S-S',
    'SUCCESS',
];

interface SuccessGlitchProps {
    show: boolean;
    onComplete: () => void; // 动画完成后的回调
}

const SuccessGlitch: React.FC<SuccessGlitchProps> = ({ show, onComplete }) => {
    const [glitchText, setGlitchText] = useState(corruptedTexts[0]);

    useEffect(() => {
        if (show) {
            // 模拟文本疯狂损坏和恢复
            let currentTextIndex = 0;
            const interval = setInterval(() => {
                setGlitchText(corruptedTexts[currentTextIndex]);
                currentTextIndex = (currentTextIndex + 1) % corruptedTexts.length;
            }, 50); // 每 50 毫秒变化一次

            // 1.5 秒后完成动画并消失
            const timeout = setTimeout(() => {
                clearInterval(interval);
                onComplete();
            }, 1500);

            return () => {
                clearInterval(interval);
                clearTimeout(timeout);
            };
        }
    }, [show, onComplete]);

    // Framer Motion 混沌动画变体
    const variants = {
        initial: { opacity: 0, scale: 1.1, skewX: 0, skewY: 0 },
        animate: {
            opacity: [0, 1, 0, 1, 0, 0.8, 1], // 霓虹灯闪烁
            scale: [1.1, 1.05, 1, 1.1, 1],
            x: [0, 20, -10, 30, -20, 0], // X轴像素级抖动
            y: [0, -15, 10, -30, 20, 0], // Y轴像素级抖动
            skewX: [0, 5, -5, 10, -10, 0], // X轴扭曲
            skewY: [0, -5, 5, -10, 10, 0], // Y轴扭曲
            transition: {
                duration: 1.5,
                times: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 1], // 动画关键帧时间
                ease: 'easeInOut',
            },
        },
        exit: {
            opacity: 0,
            scale: 1.1,
            transition: { duration: 0.3 },
        },
    };

    return (
        <AnimatePresence>
            {show && (
                <motion.div
                    initial="initial"
                    animate="animate"
                    exit="exit"
                    variants={variants}
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-[#020617]/90 backdrop-blur-sm"
                >
                    {/* 背景扫描线与像素网格 */}
                    <div className="absolute inset-0 pointer-events-none opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] brightness-50"></div>
                    <div className="absolute inset-0 pointer-events-none scanlines"></div>

                    {/* 霓虹故障文字 */}
                    <div className="relative">
                        <h1
                            className="text-8xl font-black uppercase tracking-widest neon-text-glitch"
                            style={{
                                textShadow: '0 0 10px #22d3ee, 0 0 20px #22d3ee, 0 0 30px #c084fc, 0 0 40px #c084fc',
                            }}
                        >
                            {glitchText}
                        </h1>
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-[120%] h-[120%] border border-cyan-500/30 blur-sm shadow-[0_0_20px_#22d3ee/50] animate-pulse"></div>
                        </div>
                    </div>

                    {/* 随机出现的图形伪影 */}
                    {[...Array(20)].map((_, i) => (
                        <motion.div
                            key={i}
                            animate={{
                                opacity: [0, 0.5, 0],
                                x: [0, Math.random() * 200 - 100, 0],
                                y: [0, Math.random() * 200 - 100, 0],
                            }}
                            transition={{
                                duration: 0.1,
                                repeat: Infinity,
                                repeatType: "mirror",
                                delay: Math.random() * 1.5,
                            }}
                            className={`absolute w-10 h-1 ${Math.random() > 0.5 ? 'bg-cyan-500' : 'bg-purple-500'} blur-sm shadow-[0_0_5px_#22d3ee]`}
                            style={{
                                top: `${Math.random() * 100}%`,
                                left: `${Math.random() * 100}%`,
                            }}
                        />
                    ))}
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default SuccessGlitch;
