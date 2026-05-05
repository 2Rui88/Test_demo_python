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

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

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
    """
    获取所有会话的列表（不含消息内容）。

    前端调用: GET /api/sessions
    期望返回: { sessions: [{ id, name, createdAt }] }
    """
    # TODO: 从存储中读取所有会话，按创建时间倒序排列
    return {"sessions": []}


# ---------- ② 新建会话 ----------

@app.post("/api/sessions")
def create_session(body: CreateSessionRequest):
    """
    创建一个新会话。

    前端调用: POST /api/sessions
    请求体:   { name }
    期望返回: { id, name, createdAt }
    """
    # TODO: 生成唯一 ID、记录创建时间，持久化新会话
    return JSONResponse(
        content={"feedback": "创建逻辑尚未实现"},
        status_code=501,
    )


# ---------- ③ 获取指定会话 ----------

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    """
    获取指定会话的详细信息（含消息记录）。

    前端调用: GET /api/sessions/{session_id}
    期望返回: { id, name, messages: [{ role, content, timestamp }] }

    role 取值: "user" | "assistant"
    """
    # TODO: 根据 session_id 从存储中查出会话元信息 + 全部消息
    return JSONResponse(
        content={"feedback": "查询逻辑尚未实现"},
        status_code=501,
    )


# ---------- ④ 删除会话 ----------

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """
    删除指定会话及其所有消息记录。

    前端调用: DELETE /api/sessions/{session_id}
    期望返回: { feedback }
    """
    # TODO: 删除 session_id 对应的会话及消息
    return JSONResponse(
        content={"feedback": "删除逻辑尚未实现"},
        status_code=501,
    )


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


print("后端服务器已启动，访问 http://127.0.0.1,port=8000/ 查看前端界面")

# 以上代码提供了一个完整的 FastAPI 后端框架，包含了所有必要的 API 端点和数据模型定义。你需要在对应的 TODO 注释处实现具体的业务逻辑，如会话管理、消息存储、AI 交互等。
# 注意：目前所有 API 都返回 501 Not Implemented 状态码，表示功能尚未实现。你需要根据需求逐步完善每个接口的逻辑。

print("git第二次提交测试")