import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// 定义不同情绪下的 SVG 路径 (morphing)
const paths = {
    // 🟢 开心：圆润、上扬的眉毛和嘴巴
    happy: {
        brows: 'M 30,35 Q 50,25 70,35 M 30,35 Q 50,25 70,35',
        eyes: 'M 35,55 Q 50,45 65,55 M 35,55 Q 50,45 65,55',
        mouth: 'M 30,80 Q 50,95 70,80 Q 50,95 30,80',
        color: '#4ade80', // 黑客绿
    },
    // 🔵 严肃：平直、深沉的眉毛和嘴巴
    serious: {
        brows: 'M 30,35 Q 50,35 70,35 M 30,35 Q 50,35 70,35',
        eyes: 'M 35,55 Q 50,55 65,55 M 35,55 Q 50,55 65,55',
        mouth: 'M 30,80 Q 50,80 70,80 Q 50,80 30,80',
        color: '#22d3ee', // 赛博青
    },
    // 🔴 故障：扭曲、破碎的路径 (模拟)
    glitch: {
        brows: 'M 25,30 Q 50,45 75,30 M 25,30 Q 50,45 75,30',
        eyes: 'M 30,50 Q 50,65 70,50 M 30,50 Q 50,65 70,50',
        mouth: 'M 25,75 Q 50,60 75,75 Q 50,60 25,75',
        color: '#f43f5e', // 警示红
    }
};

interface AIAvatarProps {
    sentiment: 'happy' | 'serious' | 'glitch';
}

const AIAvatar: React.FC<AIAvatarProps> = ({ sentiment }) => {
    const currentPath = paths[sentiment];

    return (
        <div className="w-full h-full flex items-center justify-center p-6 relative">
            <AnimatePresence>
                {sentiment === 'glitch' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: [0, 1, 0] }}
                        transition={{ repeat: Infinity, duration: 0.1 }}
                        className="absolute inset-0 bg-red-900/10 blur-sm"
                    />
                )}
            </AnimatePresence>

            <svg viewBox="0 0 100 110" className="w-4/5 h-4/5">
                <defs>
                    <filter id="neon">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                <g filter="url(#neon)" stroke={currentPath.color} strokeWidth="3" fill="none">
                    {/* 眉毛 */}
                    <motion.path
                        d={currentPath.brows}
                        animate={{ d: currentPath.brows, stroke: currentPath.color }}
                        transition={{ type: 'spring', stiffness: 100, damping: 10 }}
                    />
                    {/* 眼睛 */}
                    <motion.path
                        d={currentPath.eyes}
                        animate={{ d: currentPath.eyes, stroke: currentPath.color }}
                        transition={{ type: 'spring', stiffness: 100, damping: 10, delay: 0.1 }}
                    />
                    {/* 嘴巴 */}
                    <motion.path
                        d={currentPath.mouth}
                        animate={{ d: currentPath.mouth, stroke: currentPath.color }}
                        transition={{ type: 'spring', stiffness: 100, damping: 10, delay: 0.2 }}
                    />
                </g>
            </svg>
        </div>
    );
};

export default AIAvatar;
