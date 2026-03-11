/**
 * DAILM Neural Voice Interface v1.0
 * 关键词驱动的本地语音识别引擎
 */
import { CyberSound } from './CyberSoundEngine';

export const useVoiceCommander = (onCommand: (cmd: string) => void, onEnd: () => void) => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn("Speech Recognition API not supported in this browser.");
        return { startListening: () => { } };
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US'; // 建议使用英文指令，识别率更符合黑客语境
    recognition.continuous = false;
    recognition.interimResults = false;

    const startListening = () => {
        try {
            recognition.start();
            // 🔊 播报一个独特的高频启动音
            CyberSound.playDataPulse();
        } catch (e) {
            console.error("Voice Engine busy or failed to start.", e);
            onEnd();
        }
    };

    recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript.toUpperCase();
        console.log(`[VOICE_IN]: ${transcript}`);

        // 模糊匹配逻辑：例如喊出 "RECON" 触发 "INITIATE_WORKFLOW_RECON"
        if (transcript.includes("RECON") || transcript.includes("WORKFLOW")) {
            onCommand("INITIATE_WORKFLOW_RECON");
        } else if (transcript.includes("ANALYZE") || transcript.includes("METRICS")) {
            onCommand("ANALYZE_YOUTUBE_METRICS");
        } else if (transcript.includes("EXPORT") || transcript.includes("SAVE")) {
            onCommand("EXPORT_MISSION_ARCHIVE");
        } else if (transcript.includes("GLITCH")) {
            onCommand("ACTIVATE_GLITCH_PROTOCOL");
        } else if (transcript.includes("SYNC")) {
            onCommand("SYNC_NEURAL_LINK");
        } else if (transcript.includes("PURGE") || transcript.includes("CLEAR")) {
            onCommand("PURGE_TEMP_DATA");
        }
    };

    recognition.onerror = (event: any) => {
        console.error("Voice recognition error", event.error);
        onEnd();
    }

    recognition.onend = () => {
        onEnd();
    }

    return { startListening };
};
