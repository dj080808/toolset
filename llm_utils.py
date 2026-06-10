"""DeepSeek API integration for AI-generated interview questions"""
import os, json, re
from urllib.request import Request, urlopen

BASE_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


def get_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        return key
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


def generate_questions(stack_names, count=5, difficulty="senior"):
    api_key = get_api_key()
    if not api_key:
        return [], {}

    difficulty_prompts = {
        "junior": "面向初级工程师（1-2年经验）。题目侧重基础概念、常用API、基本配置。答案要简单直接。",
        "mid": "面向中级工程师（3-5年经验）。题目侧重原理理解、源码分析、性能调优。答案要有深度。",
        "senior": "面向高级工程师（5年+经验）。题目侧重架构设计、底层原理、故障排查、技术选型。答案要有体系化思维和面试金句。",
    }

    stacks_str = "、".join(stack_names)
    diff_req = difficulty_prompts.get(difficulty, difficulty_prompts["senior"])
    prompt = f"""你是资深后端面试官。为以下技术栈生成{count}道面试题。

技术栈: {stacks_str}
{diff_req}

输出纯 JSON: {{"questions":[{{"title":"题目","answer":"答案"}}]}}"""

    try:
        req = Request(BASE_URL, data=json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8, "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }).encode(), headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        })
        resp = urlopen(req, timeout=60)
        data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        # Parse JSON, with fixes for common LLM output errors
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        # Fix trailing commas
        content = re.sub(r",\s*([}\]])", r"\1", content)

        result = json.loads(content)
        questions = result.get("questions", result) if isinstance(result, dict) else result
        return questions, usage

    except Exception as e:
        print(f"[LLM] API call failed: {e}")
        return [], {}
