import re
import json

def strict_json_handshake(raw_response: str):
    """
    进化版：即使 AI 输出 '好的，这是 JSON: { "key": "val" }' 也能正确提取
    """
    try:
        # 使用正则表达式匹配最外层的花括号或中括号
        json_match = re.search(r'(\{.*\}|\[.*\])', raw_response, re.DOTALL)
        if json_match:
            clean_json = json_match.group(1)
            # 修复常见的 AI 输出错误（如尾部多余逗号）
            clean_json = re.sub(r',\s*([\]}])', r'\1', clean_json)
            return json.loads(clean_json)
        else:
            raise ValueError("No valid JSON found in response")
    except Exception as e:
        # 这里的进化点：可以触发一个 'Retry' Agent 重新格式化
        return {"status": "error", "error_type": "handshake_failed", "raw": raw_response}
