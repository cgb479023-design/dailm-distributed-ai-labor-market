import fs from 'fs-extra';
import path from 'path';
import archiver from 'archiver';

const __dirname = import.meta.dirname;

/**
 * PreBid Master AI 离线包自动化打包引擎
 * 目标：生成可在 U 盘中直接运行的 9:16 高仿真 Demo
 */
async function buildOfflinePackage(projectId = 'HAINAN_TEST_001') {
    const rootDir = path.join(__dirname, '..');
    const distDir = path.join(rootDir, 'dist_package');
    const outputZip = path.join(rootDir, `PreBid_Demo_${projectId}_OFFLINE.zip`);

    console.log(`🚀 开始构建离线包: ${projectId}...`);

    try {
        // 1. 清理并创建发布目录
        if (fs.existsSync(distDir)) fs.removeSync(distDir);
        fs.ensureDirSync(path.join(distDir, 'data'));
        fs.ensureDirSync(path.join(distDir, 'assets'));

        // 2. 复制前端渲染引擎 (从工程 workbench 目录)
        // 包含 index.html, tailwind.css, renderer.js 等
        console.log('📦 正在注入 UI 渲染引擎...');
        const workbenchSrc = path.join(rootDir, 'workbench');

        // Let's ensure workbench directory exists and has at least an index.html if we are copying it.
        // We know prebid_workbench.html was created earlier, we can use that as the index.
        const targetIndex = path.join(distDir, 'index.html');
        if (fs.existsSync(path.join(rootDir, 'prebid_workbench.html'))) {
            fs.copySync(path.join(rootDir, 'prebid_workbench.html'), targetIndex);
        } else if (fs.existsSync(workbenchSrc)) {
            await fs.copy(workbenchSrc, distDir);
        }

        // 3. 注入 AI 生成的业务数据 (从 EXPANSION_RESULT 转化)
        console.log('🤖 正在同步 AI 决策数据...');
        let expansionContent = "Demo Fallback Data";
        try {
            expansionContent = fs.readFileSync(path.join(rootDir, 'EXPANSION_RESULT.txt'), 'utf-8');
        } catch (e) {
            console.log("⚠️ EXPANSION_RESULT.txt not found, using fallback data.");
        }

        // 将文本转化为前端可识别的 JSON 结构
        const schemaData = {
            projectId,
            timestamp: new Date().toISOString(),
            content: expansionContent, // 实际应用中建议通过 strict_json_handshake 预处理
            config: {
                ratio: "9:16",
                theme: "government-blue" // 默认风格
            }
        };
        fs.writeFileSync(path.join(distDir, 'data/schema.json'), JSON.stringify(schemaData, null, 2));

        // 4. 创建执行脚本 (双击即用)
        const readme = `
# PreBid Master AI 离线演示包
- 运行环境：建议使用 Chrome / Edge 浏览器
- 操作说明：双击 index.html 即可开启 9:16 高仿真演示
- 安全提醒：本包为静态资源，不包含真实数据库连接
        `;
        fs.writeFileSync(path.join(distDir, 'README.txt'), readme.trim());

        // 5. 执行压缩
        console.log('🗜️ 正在生成压缩归档...');
        const output = fs.createWriteStream(outputZip);
        const archive = archiver('zip', { zlib: { level: 9 } });

        output.on('close', () => {
            console.log(`✅ 打包完成！总计: ${(archive.pointer() / 1024 / 1024).toFixed(2)} MB`);
            console.log(`📍 离线包位置: ${outputZip} `);
        });

        archive.pipe(output);
        archive.directory(distDir, false);
        await archive.finalize();

    } catch (err) {
        console.error('❌ 打包失败:', err);
    }
}

// 执行
buildOfflinePackage(process.argv[2]);
