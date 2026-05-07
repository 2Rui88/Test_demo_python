# 汉字谜盒

AI 字谜对话系统，该项目用于测试环境。


## 技术栈

- 后端：FastAPI + OpenAI 兼容 SDK
- 前端：HTML / CSS / JavaScript（零框架）
- 存储：JSON 文件
- AI 模型：（可替换）

## 快速启动

```bash
pip install fastapi uvicorn openai
python main.py
```

访问 ``

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sessions` | 会话列表 |
| POST | `/api/sessions` | 新建会话 |
| GET | `/api/sessions/{id}` | 会话详情 |
| DELETE | `/api/sessions/{id}` | 删除会话 |
| POST | `/api/sessions/{id}/messages` | 发送消息 |

## 配置

在 `main.py` 中填入 AI 配置：

```python
AI_API_KEY = "your-key"
AI_BASE_URL = ""
AI_MODEL = ""
```
