#!/usr/bin/env python
# coding=utf-8


import asyncio
from fastapi import FastAPI

app = FastAPI()


async def my_coroutine():
    return "Hello"

result = my_coroutine()
print(result)
# 输出类似: <coroutine object my_coroutine at 0x104b...>
# 注意：它没有输出 "Hello"，而是输出了一个对象。

async def fetch_data_from_db():
    await asyncio.sleep(2) # 模拟 2 秒延迟
    return "DB Data"

async def fetch_data_from_api():
    await asyncio.sleep(2) # 模拟 2 秒延迟
    return "API Data"

@app.get("/parallel")
async def get_data():
    # 如果你这么写，总耗时是 4 秒（串行）：
    # d1 = await fetch_data_from_db()
    # d2 = await fetch_data_from_api()

    # 如果你这么写，总耗时只有 2 秒（真正的协程并发）：
    # 这里我们利用了 asyncio 提供的工具来管理协程
    d1, d2 = await asyncio.gather(fetch_data_from_db(), fetch_data_from_api())

    return {"data": [d1, d2]}

