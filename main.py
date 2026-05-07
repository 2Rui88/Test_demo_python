"""
汉字谜盒 · AI字谜对话 — 后端入口
所有业务逻辑（会话管理、AI 交互、校验）由你自行在对应函数中实现。

REST API 端点:
  GET    /api/sessions                    → 获取会话列表
  POST   /api/sessions                    → 新建会话
  GET    /api/sessions/{session_id}       → 获取指定会话（含消息记录）
  DELETE /api/sessions/{session_id}       → 删除会话
  POST   /api/sessions/{session_id}/messages  → 发送消息并获取 AI 回复
"""

import json
import os
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI

# ============================================================
# 数据文件路径
# ============================================================
DATA_DIR = "data"
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

# 确保 data/ 目录存在
os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# JSON 文件读写辅助函数
# ============================================================

def read_json(filepath):
    """读取 JSON 文件，返回 Python 对象。文件不存在则返回空列表。"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filepath, data):
    """将 Python 对象写入 JSON 文件。"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_iso():
    """返回当前时间的 ISO 格式字符串（东八区）。"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).isoformat()


def new_id():
    """生成一个短的唯一 ID。"""
    return uuid.uuid4().hex[:12]

# ============================================================
# AI 大模型配置（请填入你的 API Key 和 Base URL）
# ============================================================
AI_API_KEY = ""                          # 替换为你的 API Key
AI_BASE_URL = ""                         # 模型兼容地址
AI_MODEL = ""                            # 模型名称

# OpenAI 兼容客户端
ai_client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)


def call_ai(system_prompt: str, messages: list):
    """
    调用 AI 大模型，返回回复文本。

    system_prompt: 系统角色设定（从 sessions.json 取）
    messages:     历史消息列表 [{role, content}, ...]
    """
    chat_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        chat_messages.append({"role": m["role"], "content": m["content"]})

    response = ai_client.chat.completions.create(
        model=AI_MODEL,
        messages=chat_messages
    )
    return response.choices[0].message.content

# ============================================================
# FastAPI 应用实例
# ============================================================
app = FastAPI(title="汉字谜盒 · AI 字谜对话", version="0.2.0")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================
# Pydantic 模型
# ============================================================

class CreateSessionRequest(BaseModel):
    """新建会话请求体"""
    name: str = "新会话"


class SendMessageRequest(BaseModel):
    """发送消息请求体"""
    content: str    # 用户输入内容（原样透传，后端负责校验）


# ============================================================
# 根路径
# ============================================================

@app.get("/")
def root():
    return FileResponse("static/index.html")


# ============================================================
# API 接口
# ============================================================

# ---------- ① 获取会话列表 ----------

@app.get("/api/sessions")
def list_sessions():
    """返回所有会话，按创建时间倒序。"""
    sessions = read_json(SESSIONS_FILE)
    sessions.sort(key=lambda s: s.get("createdAt", ""), reverse=True)
    return {"sessions": sessions}


# ---------- ② 新建会话 ----------

@app.post("/api/sessions")
def create_session(body: CreateSessionRequest):
    """创建一个新会话，持久化到 sessions.json。"""
    sessions = read_json(SESSIONS_FILE)
    session = {
        "id": new_id(),
        "name": body.name.strip() or "新会话",
        "createdAt": now_iso(),
        "systemPrompt": "你是一个汉字谜语助手，请用有趣的方式与用户互动字谜。"
    }
    sessions.append(session)
    write_json(SESSIONS_FILE, sessions)
    return session


# ---------- ③ 获取指定会话 ----------

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    """返回指定会话的元信息 + 所属的全部消息。"""
    sessions = read_json(SESSIONS_FILE)
    for s in sessions:
        if s["id"] == session_id:
            messages = read_json(MESSAGES_FILE)
            session_messages = [m for m in messages if m.get("sessionId") == session_id]
            session_messages.sort(key=lambda m: m.get("timestamp", ""))
            return {
                "id": s["id"],
                "name": s["name"],
                "messages": session_messages
            }
    return JSONResponse(
        content={"feedback": "会话不存在"},
        status_code=404,
    )


# ---------- ④ 删除会话 ----------

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """删除指定会话及其所有消息记录。"""
    sessions = read_json(SESSIONS_FILE)
    sessions = [s for s in sessions if s["id"] != session_id]
    write_json(SESSIONS_FILE, sessions)

    messages = read_json(MESSAGES_FILE)
    messages = [m for m in messages if m.get("sessionId") != session_id]
    write_json(MESSAGES_FILE, messages)

    return {"feedback": "会话已删除"}

# ---------- ⑤ 发送消息（与 AI 交互） ----------

@app.post("/api/sessions/{session_id}/messages")
def send_message(session_id: str, body: SendMessageRequest):
    # ① 输入校验
    content = body.content.strip()
    if not content:
        return JSONResponse(
            content={"feedback": "消息不能为空"},
            status_code=400,
        )

    # ② 持久化用户消息
    messages = read_json(MESSAGES_FILE)
    user_msg = {
        "sessionId": session_id,
        "role": "user",
        "content": content,
        "timestamp": now_iso()
    }
    messages.append(user_msg)
    write_json(MESSAGES_FILE, messages)

    # ③ 调用 AI 大模型生成回复
    sessions = read_json(SESSIONS_FILE)
    system_prompt = "你是一个汉字谜语助手。"
    for s in sessions:
        if s["id"] == session_id:
            system_prompt = s.get("systemPrompt", system_prompt)
            break

    history = [m for m in messages if m.get("sessionId") == session_id]
    ai_reply = call_ai(system_prompt, history)

    # ④ 持久化 AI 回复
    assistant_msg = {
        "sessionId": session_id,
        "role": "assistant",
        "content": ai_reply,
        "timestamp": now_iso()
    }
    messages.append(assistant_msg)
    write_json(MESSAGES_FILE, messages)

    # ⑤ 返回该会话的完整消息列表
    session_messages = [m for m in messages if m.get("sessionId") == session_id]
    session_messages.sort(key=lambda m: m.get("timestamp", ""))
    return {"messages": session_messages}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)