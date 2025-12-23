#!/usr/bin/env python
# coding=utf-8


import asyncio
from concurrent.futures import ProcessPoolExecutor
from fastapi import FastAPI

app = FastAPI()

# 1. 建议在全局创建一个进程池，避免每个请求都销毁/创建进程（开销极大）
# 注意：在 Windows 下，这个 executor 应该放在 if __name__ == "__main__": 保护下
# 或者在 FastAPI 的 lifespan 事件中初始化
executor = ProcessPoolExecutor(max_workers=4)

def cpu_intensive_task(n: int):
    # 模拟 CPU 耗时计算
    count = 0
    for i in range(n):
        count += i
    return count

@app.get("/calculate")
async def calculate(n: int = 1000000):
    loop = asyncio.get_running_loop()

    # 2. 使用 loop.run_in_executor 将任务提交给进程池
    # 第一个参数是 executor，第二个是函数名，后面是参数
    result = await loop.run_in_executor(executor, cpu_intensive_task, n)

    return {"result": result}


# 无辜的路人接口 ---
@app.get("/ping")
async def ping():
    return {"message": "pong! (我应该瞬间返回)"}


# 3. (可选) 程序关闭时清理进程池
@app.on_event("shutdown")
def shutdown_event():
    print("come into on_event...")
    executor.shutdown()

