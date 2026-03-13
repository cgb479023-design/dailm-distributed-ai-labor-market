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
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const materialRef = useRef<THREE.MeshBasicMaterial | null>(null);
    const [reinitKey, setReinitKey] = React.useState(0);
    const requestRef = useRef<number | null>(null);
    const [isWebGLOk, setIsWebGLOk] = React.useState(true);

    // 监听颜色变化
    useEffect(() => {
        if (materialRef.current) {
            materialRef.current.color.set(color);
            materialRef.current.opacity = color === '#f43f5e' ? 0.9 : 0.6; // Slightly more balanced
        }
    }, [color]);

    useEffect(() => {
        if (!containerRef.current) return;

        // Try Three.js initialization
        let renderer: THREE.WebGLRenderer | null = null;
        let scene: THREE.Scene | null = null;
        
        try {
            console.log("Initializing Three.js Matrix Rain...");
            scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
            camera.position.z = 1000;
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            console.log("WebGL Renderer created.");
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.setClearColor(0x000000, 0); // Explicit transparency
            containerRef.current.appendChild(renderer.domElement);

            const loader = new FontLoader();
            console.log("Loading font: /fonts/helvetiker_regular.typeface.json");
            loader.load('/fonts/helvetiker_regular.typeface.json', (font: Font) => {
                console.log("Font loaded successfully.");
                const textMaterial = new THREE.MeshBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: 0.8,
                    blending: THREE.AdditiveBlending
                });
                materialRef.current = textMaterial;

                const streams: THREE.Group[] = [];
                const characterSets = ['アァカサタナハマヤャラワガザ达巴', 'abcdefg', '012345'];
                const charArray = characterSets.join('').split('');
                const fontHeight = 16;
                const charCount = 25;
                const numStreams = Math.ceil(window.innerWidth / fontHeight) * 2;

                for (let i = 0; i < numStreams; i++) {
                    const streamGroup = new THREE.Group();
                    // 确保流在相机视野内
                    const x = (Math.random() - 0.5) * window.innerWidth * 2;
                    const y = (Math.random() - 0.5) * window.innerHeight * 2;
                    const z = (Math.random() - 0.5) * 800;
                    streamGroup.position.set(x, y, z);
                    for (let j = 0; j < charCount; j++) {
                        const geometry = new TextGeometry(charArray[Math.floor(Math.random() * charArray.length)], { font, size: fontHeight, depth: 1 });
                        const charMesh = new THREE.Mesh(geometry, textMaterial.clone());
                        charMesh.position.y = -j * fontHeight;
                        charMesh.material.opacity = 1 - (j / charCount);
                        streamGroup.add(charMesh);
                    }
                    (streamGroup as any).speed = (Math.random() * 3 + 2);
                    scene!.add(streamGroup);
                    streams.push(streamGroup);
                }

                const animate = () => {
                    requestRef.current = requestAnimationFrame(animate);
                    streams.forEach(s => {
                        s.position.y -= (s as any).speed;
                        if (s.position.y < -window.innerHeight) s.position.y = window.innerHeight;
                    });
                    renderer?.render(scene!, camera);
                };
                animate();
            }, undefined, (err) => {
                console.error("Font Load Failed:", err);
                setIsWebGLOk(false);
            });
        } catch (e) {
            console.error("Three.js Init Failed:", e);
            setIsWebGLOk(false);
        }

        return () => {
            if (requestRef.current) cancelAnimationFrame(requestRef.current);
            if (renderer) {
                if (renderer.domElement.parentNode === containerRef.current) containerRef.current?.removeChild(renderer.domElement);
                renderer.dispose();
            }
        };
    }, [reinitKey]);

    // Fallback Canvas (Pure 2D Matrix Rain)
    useEffect(() => {
        if (isWebGLOk) return;
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const columns = Math.floor(canvas.width / 20);
        const drops = new Array(columns).fill(1);
        const chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ".split("");

        const draw = () => {
            ctx.fillStyle = "rgba(2, 6, 23, 0.1)"; // Trails
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = color;
            ctx.font = "15px monospace";
            for (let i = 0; i < drops.length; i++) {
                const text = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(text, i * 20, drops[i] * 20);
                if (drops[i] * 20 > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        };
        const interval = setInterval(draw, 50);
        return () => clearInterval(interval);
    }, [isWebGLOk, color, reinitKey]);

    return (
        <div ref={containerRef} className="fixed inset-0 pointer-events-none" style={{ zIndex, display: 'block' }}>
            {!isWebGLOk && <canvas ref={canvasRef} className="fixed inset-0" style={{ display: 'block' }} />}
        </div>
    );
};

export default MatrixRain3D;
