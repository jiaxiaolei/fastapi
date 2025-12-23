#!/usr/bin/env python
# coding=utf-8

import asyncio
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

# 模拟一个异步的数据库查询或耗时操作
async def get_mock_data(name: str):
    await asyncio.sleep(1)  # 非阻塞等待
    return {"item": name, "status": "active"}

@app.get("/")
async def index():
    return {"message": "Hello, Async FastAPI!"}

@app.get("/search/{user_id}")
async def search_user_data(user_id: int):
    """
    演示如何使用协程并发发起多个网络请求
    """
    # 使用 httpx 的异步客户端（需安装: pip install httpx）
    async with httpx.AsyncClient() as client:
    #async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            # 定义两个异步任务，但不立即执行
            task1 = client.get(f"https://jsonplaceholder.typicode.com/todos/{user_id}")
            task2 = get_mock_data(f"User-{user_id}")

            # 使用 asyncio.gather 并发执行
            # 两个请求会同时发出，总耗时取决于最慢的那一个（约1秒），而不是 1s + 网络耗时
            response, db_data = await asyncio.gather(task1, task2)
        except httpx.ConnectTimeout:
            raise HTTPException(status_code=504, detail="外部 API 连接超时")


    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="External API error")

    api_result = response.json()

    return {
        "user_id": user_id,
        "external_api": api_result,
        "internal_db": db_data
    }

if __name__ == "__main__":
    import uvicorn
    # 启动命令: uvicorn 脚本名:app --reload
    uvicorn.run(app, host="127.0.0.1", port=8000)
