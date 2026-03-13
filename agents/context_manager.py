class ContextWindow:
    def __init__(self, max_tokens=8000):
        self.history = []
        self.max_tokens = max_tokens

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        self.compress_if_needed()

    def compress_if_needed(self):
        """
        进化逻辑：当上下文过长时，保留首尾，压缩中间
        1. 保留 System Prompt 和 RFP 核心背景
        2. 压缩中间的交互细节
        3. 保留最近的 3 轮对话
        """
        if len(self.history) > 10:
            # 这里的逻辑可以调用 DOM Slimming 进一步瘦身
            head = self.history[:2]  # 背景
            tail = self.history[-4:] # 最近交互
            self.history = head + [{"role": "system", "content": "...[已折叠冗余上下文]..."}] + tail

    def get_context(self):
        return self.history
