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
    """
    向指定会话发送一条消息，由 AI 生成回复。

    前端调用: POST /api/sessions/{session_id}/messages
    请求体:   { content }
    期望返回: { messages: [{ role, content, timestamp }] }

    你需要在此实现:
      1. 输入校验（空值等）→ 返回错误提示
      2. 将用户消息持久化到该会话
      3. 调用 AI 大模型生成回复
      4. 将 AI 回复持久化
      5. 返回该会话的完整消息列表
    """
    # TODO: 实现消息处理 + AI 调用逻辑
    return JSONResponse(
        content={"feedback": "AI 交互逻辑尚未实现"},
        status_code=501,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)