import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { Font, FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';

interface MatrixRain3DProps {
    zIndex?: number;
    color?: string;
}

const MatrixRain3D: React.FC<MatrixRain3DProps> = ({ zIndex = -1, color = '#22d3ee' }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const materialRef = useRef<THREE.MeshBasicMaterial | null>(null);

    // 监听颜色变化并实时更新 WebGL 材质
    useEffect(() => {
        if (materialRef.current) {
            materialRef.current.color.set(color);
            // 增加发光强度模拟“热量”
            materialRef.current.opacity = color === '#f43f5e' ? 1.0 : 0.8;
        }
    }, [color]);

    useEffect(() => {
        if (!containerRef.current) return;

        // --- THREE.js 核心初始化 ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 2000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        containerRef.current.appendChild(renderer.domElement);

        // --- 代码流粒子系统 ---
        const characterSets = [
            'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン', // Katakana
            'abcdefghijklmnopqrstuvwxyz', // Latin
            '0123456789' // Digits
        ];
        const charArray = characterSets.join('').split('');
        const fontHeight = 16;
        const charCount = 30; // 每个流的代码长度
        const numStreams = Math.ceil(window.innerWidth / fontHeight) * 2; // 代码流的数量

        // 创建字体加载器
        const loader = new FontLoader();
        // 使用下载的本地字体
        loader.load('/fonts/helvetiker_regular.typeface.json', (font: Font) => {
            const textMaterial = new THREE.MeshBasicMaterial({
                color: color,
                transparent: true,
                opacity: color === '#f43f5e' ? 1.0 : 0.8,
                blending: THREE.AdditiveBlending // 霓虹发光效果
            });
            materialRef.current = textMaterial;

            const streams: THREE.Group[] = [];
            for (let i = 0; i < numStreams; i++) {
                const streamGroup = new THREE.Group();
                streamGroup.position.set(
                    (Math.random() - 0.5) * window.innerWidth * 2.5, // 宽阔的 Z 轴覆盖
                    window.innerHeight + Math.random() * window.innerHeight * 2,
                    (Math.random() - 0.5) * 2000 // 深度 Z 轴延伸
                );

                // 为每个流创建文本 Mesh
                for (let j = 0; j < charCount; j++) {
                    const char = charArray[Math.floor(Math.random() * charArray.length)];
                    const geometry = new TextGeometry(char, {
                        font: font,
                        size: fontHeight,
                        depth: 1,
                        curveSegments: 2,
                        bevelEnabled: false
                    });

                    const charMesh = new THREE.Mesh(geometry, textMaterial.clone());
                    charMesh.position.y = -j * fontHeight;
                    charMesh.material.opacity = 1 - (j / charCount); // 头部最亮，尾部消失

                    // 随机旋转，增加混沌感
                    charMesh.rotation.y = (Math.random() - 0.5) * 0.1;

                    streamGroup.add(charMesh);
                }

                // 赋予每个流不同的掉落速度
                (streamGroup as any).speed = (Math.random() * 5 + 2) * (window.innerHeight / 1000);
                scene.add(streamGroup);
                streams.push(streamGroup);
            }

            // --- 动画循环 ---
            const animate = () => {
                requestAnimationFrame(animate);

                streams.forEach(stream => {
                    stream.position.y -= (stream as any).speed;

                    // 随机更换字符，模拟代码抖动
                    stream.children.forEach(char => {
                        if (Math.random() > 0.99) {
                            const randomChar = charArray[Math.floor(Math.random() * charArray.length)];
                            ((char as THREE.Mesh).geometry as TextGeometry).dispose();
                            (char as THREE.Mesh).geometry = new TextGeometry(randomChar, {
                                font: font,
                                size: fontHeight,
                                depth: 1,
                                curveSegments: 2,
                                bevelEnabled: false
                            });
                        }
                    });

                    // 当流到达底部时，重置到顶部
                    if (stream.position.y < -window.innerHeight) {
                        stream.position.y = window.innerHeight + Math.random() * window.innerHeight;
                        stream.position.x = (Math.random() - 0.5) * window.innerWidth * 2.5;
                        // 随机改变 Z 轴深度，模拟无限空间
                        stream.position.z = (Math.random() - 0.5) * 2000;
                    }
                });

                renderer.render(scene, camera);
            };
            animate();
        });

        // --- 窗口重置处理 ---
        const handleResize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };
        window.addEventListener('resize', handleResize);

        // --- 清理逻辑 ---
        return () => {
            window.removeEventListener('resize', handleResize);
            if (containerRef.current) {
                containerRef.current.removeChild(renderer.domElement);
            }
            // scene.clear() OR recursive dispose is better, but this handles simple unmount
            scene.clear();
            renderer.dispose();
        };
    }, []);

    return (
        <div
            ref={containerRef}
            className="fixed inset-0 pointer-events-none"
            style={{ zIndex }}
        />
    );
};

export default MatrixRain3D;
