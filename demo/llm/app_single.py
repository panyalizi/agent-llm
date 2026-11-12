"""
单文件版 Demo：既提供网页，也提供调用 quick_chat 的接口。

运行方法：
    uvicorn demo.llm.app_single:app --reload

然后在浏览器访问 http://127.0.0.1:8000 即可。
"""

from __future__ import annotations

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .llm import quick_chat


app = FastAPI(title="Minimal LLM Single File Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <title>单文件 LLM Demo</title>
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f1f5f9;
        margin: 0;
        padding: 40px;
      }}
      .card {{
        max-width: 720px;
        margin: 0 auto;
        background: #fff;
        padding: 32px;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(15, 23, 42, 0.18);
      }}
      textarea {{
        width: 100%;
        min-height: 150px;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #cbd5f5;
        font-size: 16px;
      }}
      button {{
        margin-top: 16px;
        padding: 14px 28px;
        border: none;
        border-radius: 999px;
        background: linear-gradient(120deg, #2563eb, #7c3aed);
        color: #fff;
        font-size: 16px;
        cursor: pointer;
      }}
      .result {{
        margin-top: 24px;
        padding: 20px;
        border-radius: 16px;
        background: #0f172a;
        color: #e2e8f0;
        min-height: 100px;
        white-space: pre-wrap;
        line-height: 1.6;
      }}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>单文件 LLM Demo</h1>
      <form method="post" action="/chat">
        <label for="prompt">输入你的问题：</label>
        <textarea id="prompt" name="prompt" placeholder="请输入内容...">{prompt}</textarea>
        <button type="submit">搜索</button>
      </form>
      <div class="result">{result}</div>
    </div>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(TEMPLATE.format(prompt="", result="等待输入..."))


@app.post("/chat", response_class=HTMLResponse)
def chat(prompt: str = Form(...)) -> HTMLResponse:
    reply = quick_chat(prompt)
    return HTMLResponse(TEMPLATE.format(prompt=prompt, result=reply))


@app.get("/api/chat")
def api_chat(prompt: str) -> dict[str, str]:
    return {"prompt": prompt, "reply": quick_chat(prompt)}

