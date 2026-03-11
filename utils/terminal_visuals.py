import sys
import time
import random
import string

class CyberTerminal:
    @staticmethod
    def decrypt_bar(label, duration=2.0):
        """模拟数据解密进度的终端特效"""
        chars = string.ascii_uppercase + string.digits + "!@#$%^&*"
        width = 30
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            filled = int(width * progress)
            
            # 生成“乱码”部分
            scrambled = "".join(random.choice(chars) for _ in range(width - filled))
            # 生成“已解密”部分 (用方块表示)
            decrypted = "█" * filled
            
            # 颜色控制：已解密为青色，乱码为灰色
            sys.stdout.write(f"\r\033[96m{label}\033[0m: [{decrypted}\033[90m{scrambled}\033[0m] {int(progress*100)}%")
            sys.stdout.flush()
            
            if progress >= 1.0:
                sys.stdout.write(f"\r\033[92m{label}\033[0m: [SUCCESS_DECRYPTED] 100%          \n")
                break
            time.sleep(0.05)

    @staticmethod
    def matrix_stream(text, speed=0.02):
        """模拟流式文字输出"""
        for char in text:
            sys.stdout.write(f"\033[92m{char}\033[0m")
            sys.stdout.flush()
            time.sleep(speed)
        print()
