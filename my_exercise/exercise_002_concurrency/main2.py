#!/usr/bin/env python
# coding=utf-8

from fastapi import FastAPI
import anyio
import time

app = FastAPI()

# --- 这是一个模拟 CPU 密集型或阻塞的同步函数 ---
def heavy_task():
    print("开始执行耗时任务（模拟 5 秒阻塞）...")
    time.sleep(5)  # 这里的 sleep 是 Python 原生的，会阻塞当前线程
    print("耗时任务结束！")
    return "终于算完了"

# --- 角色 1：无辜的路人接口 ---
@app.get("/ping")
async def ping():
    return {"message": "pong! (我应该瞬间返回)"}

# --- 角色 2：写法 A（作死版） ---
# 这是一个 async 接口，意味着它运行在主线程的事件循环上
@app.get("/block_server")
async def block_server():
    # ❌ 错误！在 async 函数里直接调用同步阻塞函数
    # 这会卡死整个主线程（Event Loop）
    result = heavy_task()
    return {"result": result}

# --- 角色 3：写法 B（正确版） ---
@app.get("/no_block")
async def no_block():
    # ✅ 正确！把同步阻塞函数扔到线程池去跑
    # 主线程依然自由，可以处理别人的请求
    #result = await run_in_threadpool(heavy_task)
    result = await anyio.to_thread.run_sync(heavy_task)  # 在线程池中运行
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

