"""DeepSeek API integration for AI-generated interview questions"""
import os
import json
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


def get_api_key():
    """每次调用时实时读取，OS 环境变量优先，fallback 到 .env 文件"""
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        return key
    # OS 没有 → 尝试读 .env 文件（不用 dotenv，直接解析）
    try:
        from pathlib import Path
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val and val != "sk-your-key-here":
                        return val
    except Exception:
        pass
    return ""


def generate_questions(stack_names, count=5):
    """Call DeepSeek API to generate interview questions with answers"""
    api_key = get_api_key()
    if not api_key:
        print("[LLM] DEEPSEEK_API_KEY 未设置，AI 出题不可用")
        return []

    stacks_str = "、".join(stack_names)
    prompt = f"""你是资深后端面试官。请为以下技术栈生成{count}道面试题，每题附带参考答案。

技术栈: {stacks_str}

要求:
1. 题目要有深度，能区分初级和高级工程师
2. 答案要包含核心知识点和面试金句
3. 输出 JSON 数组格式: [{{"title": "题目", "answer": "参考答案"}}]

只输出 JSON 数组，不要其他内容。"""

    try:
        req = Request(
            BASE_URL,
            data=json.dumps({
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 4096,
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        resp = urlopen(req, timeout=30)
        data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"]

        # Extract JSON array from response
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content[:-3]
        return json.loads(content)

    except Exception as e:
        print(f"AI question generation failed: {e}")
        return []
