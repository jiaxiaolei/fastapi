

https://www.cnblogs.com/geekbruce/articles/19332537




如何理解FastAPI中的run_in_threadpool方法，什么场景下该使用该方法？实例理解，一文带你彻底弄懂！

https://www.cnblogs.com/geekbruce/articles/19332537


简介：


这个方法导入的具体路径如下：

from fastapi.concurrency import run_in_threadpool
这个函数是 FastAPI 给开发者提供的一颗**“后悔药”或者说是“救生圈”**。

它的核心作用是：在异步函数（async def）中，安全地运行同步（阻塞）代码，而不会卡死整个服务器。

为了让你理解得更透彻，我们需要先讲一下背景。

1. 背景：FastAPI 的“单行道”危机
FastAPI 是基于 AsyncIO（异步 I/O）的。你可以把 FastAPI 的主线程想象成一条高速公路的单行道（事件循环 Event Loop）。

理想情况：所有的车（请求）都是跑车（异步代码），速度极快，不会停下来。

危机情况：突然开进来一辆压路机（同步阻塞代码，比如繁重的 CPU 计算、或者不支持异步的旧库）。

因为是单行道，这辆压路机一上来，后面的所有跑车（其他用户的请求）都得跟在屁股后面慢慢挪。

结果：只要有一个人请求了这个慢接口，整个服务器对所有人都卡住了。


2. 这个函数的作用
run_in_threadpool 的作用就是把这辆压路机（同步代码）从主干道上挪走，放到旁边的一条辅路（线程池）上去跑。

这样，主干道（事件循环）依然畅通无阻，可以继续处理其他人的请求。等辅路上的压路机跑完了，再把结果拿回来。


3. 代码对比
为了让你直观地感受到威力，我们需要设计一个**“服务器假死”实验**。

我们需要两个角色：

“捣乱者”：一个执行耗时操作（比如睡 5 秒）的请求。

“无辜路人”：一个非常简单的请求（Ping），本该 0.01 秒就返回。

我们将对比两种写法：

写法 A（作死写法）：在 async 函数里直接运行同步阻塞代码。

写法 B（正确写法）：使用 run_in_threadpool 拯救世界。

1. 实验代码 (main.py)
复制代码
import time
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

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
    result = await run_in_threadpool(heavy_task)
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
复制代码
开始体验（请动手操作——增加实际感受）
启动服务后，打开两个浏览器标签页（或者用 Postman）。

实验一：体验“服务器假死”（不使用 run_in_threadpool）
标签页 A 准备访问：http://127.0.0.1:8000/block_server （先别回车）

标签页 B 准备访问：http://127.0.0.1:8000/ping

操作：

先在 标签页 A 按回车（触发耗时任务）。

立刻、马上 切换到 标签页 B 按回车。

结果观测：

你会发现 标签页 B（那个本来应该瞬间返回的 /ping）一直在转圈圈！

它必须足足等 5 秒，直到 A 结束了，B 才能拿到结果。

结论：一个人调用了烂代码，全服瘫痪。

image

 结果如上， 左侧的服务开启后，导致右侧服务不能立刻得到响应返回。




实验二：体验“丝般顺滑”（使用 run_in_threadpool）
标签页 A 准备访问：http://127.0.0.1:8000/no_block （这是优化过的接口）

标签页 B 准备访问：http://127.0.0.1:8000/ping

操作：

先在 标签页 A 按回车。

立刻、马上 切换到 标签页 B 按回车。

结果观测：

标签页 B 瞬间返回了 pong!。

标签页 A 依然在转圈等待那 5 秒。

结论：耗时任务自己在后台慢慢跑，完全不影响其他用户的正常访问。

image

 左侧服务一启动，虽然还是处于阻塞状态，但是右侧的服务丝毫不受印象，一启动就立刻得到了响应返回结果。



原理图解
为了帮你更深理解，想象一下银行柜台：

FastAPI 主线程 = 银行唯一的一个 VIP 窗口。

Run_in_threadpool = 把客户带到旁边的普通柜台处理。

场景一（不用 run_in_threadpool）： 一个客户（请求 A）来办业务，但他要在柜台前数 5000 张钞票（耗时任务）。 因为只有一个窗口，后面排队的客户（请求 B）虽然只是想问个路（Ping），但也只能干等这哥们数完钱。这就是阻塞。

场景二（用 run_in_threadpool）： 客户（请求 A）刚拿出 5000 张钞票，VIP 窗口的柜员说：“先生，数钱业务请去旁边的 2 号窗口（线程池），那里有专人为您服务。” 于是 VIP 窗口立刻空出来了，马上接待了想问路的客户（请求 B）。这就是非阻塞并发。







FastApi框架异步调用同步问题
Fastapi项目，在接口中调用同步方法，如果该同步方法，耗时较长(比如连接redis超时)，会造成整个项目接口的阻塞，这是任何接口的访问都会被阻塞超时

https://www.cnblogs.com/ltyc/p/18664047


一、为什么会阻塞

FastAPI 是基于异步框架（如 asyncio 或 anyio）构建的，它的核心是一个事件循环（Event Loop）。事件循环负责调度和执行所有的异步任务。当你在异步函数中直接调用同步阻塞代码时，事件循环会被阻塞，无法继续处理其他任务，直到同步代码执行完毕。

复制代码
from fastapi import FastAPI
import time

app = FastAPI()

def sync_function():
    time.sleep(5)  # 模拟一个耗时的同步操作
    return "Done"

@app.get("/")
async def root():
    result = sync_function()  # 直接调用同步函数
    return {"result": result}
复制代码
在这个例子中time.sleep(5) 是一个同步阻塞操作，它会阻塞事件循环 5 秒钟。在这期间，FastAPI 无法处理其他请求，整个应用的并发性能会大幅下降。

二、如何避免阻塞

将同步代码放到线程池或进程池中执行，将同步代码改为异步实现。有以下几种常用解决方案

1. 使用 run_in_threadpool 或 asyncio.to_thread
将同步代码放到线程池中执行，避免阻塞事件循环。

复制代码
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
import time

app = FastAPI()

def sync_function():
    time.sleep(5)  # 模拟一个耗时的同步操作
    return "Done"

@app.get("/")
async def root():
    result = await run_in_threadpool(sync_function)  # 在线程池中运行
    return {"result": result}
复制代码
2 使用 run_in_processpool
对于 CPU 密集型的同步代码，可以使用进程池来避免阻塞事件循环。



复制代码
from fastapi import FastAPI
from fastapi.concurrency import run_in_processpool
import time

app = FastAPI()

def cpu_intensive_function():
    # 模拟一个 CPU 密集型的操作
    result = sum(i * i for i in range(10**6))
    return result

@app.get("/")
async def root():
    result = await run_in_processpool(cpu_intensive_function)  # 在进程池中运行
    return {"result": result}
复制代码
3. 将同步代码改为异步实现
如果可能，尽量将同步代码改为异步实现。例如，使用 asyncio.sleep 代替 time.sleep，或者使用异步库代替同步库。

复制代码
from fastapi import FastAPI
import asyncio

app = FastAPI()

async def async_function():
    await asyncio.sleep(5)  # 异步等待
    return "Done"

@app.get("/")
async def root():
    result = await async_function()  # 直接调用异步函数
    return {"result": result}
复制代码
4. 使用 anyio.to_thread.run_sync
如果你使用的是 anyio 库，可以使用 anyio.to_thread.run_sync 来运行同步代码。

复制代码
from fastapi import FastAPI
import anyio
import time

app = FastAPI()

def sync_function():
    time.sleep(5)  # 模拟一个耗时的同步操作
    return "Done"

@app.get("/")
async def root():
    result = await anyio.to_thread.run_sync(sync_function)  # 在线程池中运行
    return {"result": result}
复制代码
总结
直接调用同步代码会阻塞事件循环，导致整个应用的性能下降。

解决方案：

对于 I/O 密集型任务，使用 run_in_threadpool 或 asyncio.to_thread。

对于 CPU 密集型任务，使用 run_in_processpool。

尽量将同步代码改为异步实现。

最佳实践：在 FastAPI 中，尽量避免直接调用同步阻塞代码，始终使用异步或线程池/进程池来处理同步任务。




