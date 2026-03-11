/**
 * DAILM Neural Audio Engine v1.0
 * 纯 Web Audio API 实现，无需外部资源
 */
let audioCtx: AudioContext | null = null;

export const CyberSound = {
    // 初始化方法，绑定到用户首次交互
    init: () => {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
    },

    // 1. 数据脉冲音 (用于点击或指令发送)
    playDataPulse: () => {
        if (!audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'square'; // 方波更有电子感
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(110, audioCtx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.1);
    },

    // 2. 机械快门音 (用于 Visual Feed 画面更新)
    playShutter: () => {
        if (!audioCtx) return;
        const noise = audioCtx.createBufferSource();
        const bufferSize = audioCtx.sampleRate * 0.05;
        const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;

        noise.buffer = buffer;
        const filter = audioCtx.createBiquadFilter();
        filter.type = 'highpass';
        filter.frequency.value = 2000;
        noise.connect(filter);
        filter.connect(audioCtx.destination);
        noise.start();
    },

    // 3. 混沌故障音 (配合 SuccessGlitch 特效)
    playGlitchBurst: () => {
        if (!audioCtx) return;
        const duration = 1.5;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        // 随机频率抖动，模拟数据损坏
        for (let i = 0; i < 20; i++) {
            osc.frequency.setValueAtTime(Math.random() * 1000 + 200, audioCtx.currentTime + (i * 0.07));
        }
        gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
    }
};
