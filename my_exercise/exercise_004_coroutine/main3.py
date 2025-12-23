#!/usr/bin/env python
# coding=utf-8

import asyncio
import httpx
import time
from fastapi import FastAPI, HTTPException

app = FastAPI()

# 模拟任务1：模拟从数据库读取数据（耗时 1.5 秒）
async def get_db_data(user_id: int):
    await asyncio.sleep(1.5)
    return {"user_id": user_id, "name": "张三", "role": "admin"}

# 模拟任务2：模拟从另一个微服务获取积分（耗时 1.0 秒）
async def get_remote_score(user_id: int):
    await asyncio.sleep(1.0)
    return {"points": 100}

@app.get("/search/{user_id}")
async def search_user_data(user_id: int):
    start_time = time.perf_counter() # 记录开始时间

    # 1. 创建协程对象（此时任务还没开始运行）
    task1 = get_db_data(user_id)
    task2 = get_remote_score(user_id)

    print("--- 任务已准备好，开始并发执行 ---")

    # 2. 使用 gather 并发驱动这两个协程
    # 任务1耗时1.5s，任务2耗时1.0s。
    # 协程模式下，总耗时应该在 1.5s 左右，而不是 2.5s。
    db_res, score_res = await asyncio.gather(task1, task2)

    end_time = time.perf_counter() # 记录结束时间
    duration = end_time - start_time

    return {
        "status": "success",
        "total_duration_seconds": round(duration, 2),
        "data": {
            "profile": db_res,
            "score": score_res
        },
        "note": "可以看到总耗时仅约 1.5 秒，证明两个任务是并发执行的。"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

