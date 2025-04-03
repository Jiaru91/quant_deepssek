
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import settings
from app.api import endpoint

app = FastAPI(
    title="量化分析服务",
    description="提供股票市场分析和预测服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(endpoint.router, prefix="/api/v1/stock", tags=["stock"])

@app.get("/")
async def root():
    return {
        "message": "欢迎使用量化分析服务",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
