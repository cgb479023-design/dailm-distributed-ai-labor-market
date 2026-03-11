/**
 * DAILM Semantic Vision Slimmer v2.0
 * 核心逻辑：提取交互元素 + 嗅探关键视觉帧
 */
(function () {
    const getKeyFrames = () => {
        const images = Array.from(document.querySelectorAll('img, canvas, video'));
        return images
            .map(el => {
                let src = '';
                if (el.tagName === 'CANVAS') {
                    // Try to catch canvas data 
                    try {
                        src = el.toDataURL('image/webp', 0.5); // 压缩画布数据
                    } catch (e) {
                        src = '';
                    }
                } else if (el.tagName === 'VIDEO') {
                    // 抓取视频当前帧预览
                    try {
                        const canvas = document.createElement('canvas');
                        canvas.width = el.videoWidth / 4;
                        canvas.height = el.videoHeight / 4;
                        canvas.getContext('2d').drawImage(el, 0, 0, canvas.width, canvas.height);
                        src = canvas.toDataURL('image/webp');
                    } catch (e) {
                        src = '';
                    }
                } else {
                    src = el.src;
                }

                // 评分机制：优先抓取大图（封面）或带特定标识的图
                const rect = el.getBoundingClientRect();
                const score = (rect.width * rect.height) + (el.className.includes('thumbnail') ? 10000 : 0);

                return { src, score, alt: el.alt || 'untagged_frame' };
            })
            .filter(img => img.src && (img.src.startsWith('http') || img.src.startsWith('data:')))
            .sort((a, b) => b.score - a.score)
            .slice(0, 3); // 只取前三张最具代表性的“关键帧”
    };

    const interactables = Array.from(document.querySelectorAll('button, a, input, textarea, [role="button"]'))
        .map(el => ({
            tag: el.tagName,
            text: el.innerText || el.placeholder || el.ariaLabel,
            id: el.id || el.className
        })).slice(0, 50);

    return JSON.stringify({
        frames: getKeyFrames(),
        elements: interactables,
        timestamp: Date.now()
    });
})();
