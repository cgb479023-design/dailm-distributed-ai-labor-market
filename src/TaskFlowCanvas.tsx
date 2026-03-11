import React from 'react';
import { motion } from 'framer-motion';

interface Connection {
    from: string; // 'gemini', 'claude', 'grok'
    to: 'monitor' | 'writer';
    active: boolean;
}

const TaskFlowCanvas = ({ activeConnection }: { activeConnection: Connection | null }) => {
    // 坐标映射逻辑：根据你左侧 Node 的实际位置进行微调
    const nodePositions: any = {
        gemini: { x: '12%', y: '25%' },
        claude: { x: '12%', y: '45%' },
        grok: { x: '12%', y: '65%' },
        monitor: { x: '50%', y: '40%' }
    };

    if (!activeConnection) return null;

    const start = nodePositions[activeConnection.from];
    const end = nodePositions[activeConnection.to];

    return (
        <svg className="fixed inset-0 w-full h-full pointer-events-none z-40">
            <defs>
                <filter id="neon-glow">
                    <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                    <feMerge>
                        <feMergeNode in="coloredBlur" />
                        <feMergeNode in="SourceGraphic" />
                    </feMerge>
                </filter>
            </defs>

            {/* 基础路径 */}
            <motion.path
                d={`M ${start.x} ${start.y} C 30% ${start.y}, 30% ${end.y}, ${end.x} ${end.y}`}
                fill="transparent"
                stroke="rgba(34, 211, 238, 0.1)"
                strokeWidth="1"
            />

            {/* 流光动画路径 */}
            <motion.path
                d={`M ${start.x} ${start.y} C 30% ${start.y}, 30% ${end.y}, ${end.x} ${end.y}`}
                fill="transparent"
                stroke="#22d3ee"
                strokeWidth="2"
                strokeDasharray="20, 100"
                filter="url(#neon-glow)"
                initial={{ strokeDashoffset: 120 }}
                animate={{ strokeDashoffset: -120 }}
                transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
            />
        </svg>
    );
};

export default TaskFlowCanvas;
