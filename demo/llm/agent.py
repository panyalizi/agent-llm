"""天气 Agent：单轮最小闭环 + 多轮对话（感知 → 决策 → 行动 → 观察）。"""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
MODEL = os.getenv("OPENAI_MODEL") or "qwen-plus"


def get_weather(city: str, date: str = "today") -> dict:
    data = {
        "北京": {"today": ("晴", 25), "tomorrow": ("多云", 23)},
        "上海": {"today": ("小雨", 28), "tomorrow": ("阴", 27)},
        "广州": {"today": ("雷阵雨", 31), "tomorrow": ("晴", 33)},
    }
    key = "tomorrow" if date == "tomorrow" else "today"
    if city not in data:
        return {"error": f"暂不支持查询 {city} 的天气"}
    weather, temp = data[city][key]
    return {"city": city, "date": date, "weather": weather, "temperature": f"{temp}°C"}


TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询城市天气（today/tomorrow）",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名，如北京"},
                "date": {"type": "string", "description": "today 或 tomorrow"},
            },
            "required": ["city"],
        },
    },
}]
HANDLERS = {"get_weather": get_weather}


def run_tool_round(messages: list) -> str:
    """内层：工具循环，直到模型不再调用工具，返回最终文本。"""
    while True:
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        msg = resp.choices[0].message

        if not msg.tool_calls:
            messages.append(msg)
            return msg.content or ""

        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            print(f"🔧 调用: {call.function.name}({args})")
            handler = HANDLERS.get(call.function.name)
            result = handler(**args) if handler else {"error": f"未知工具: {call.function.name}"}
            print(f"📦 结果: {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })


def run_agent(question: str) -> str:
    """单轮问答（最小闭环）。"""
    messages = [{"role": "user", "content": question}]
    return run_tool_round(messages)


def run_agent_loop() -> None:
    """外层：多轮会话；内层：工具循环。messages 全程保留，形成记忆。"""
    messages = [
        {"role": "system", "content": "你是一个天气助手，帮用户查询天气。用自然语言回答。"},
    ]
    print("🌤️ 天气助手已启动，输入 quit / exit / 退出 结束\n")

    while True:
        user_input = input("👤 ").strip()
        if user_input.lower() in {"quit", "exit", "退出"}:
            print("👋 再见！")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        answer = run_tool_round(messages)
        print(f"🤖 {answer}\n")


if __name__ == "__main__":
    run_agent_loop()
