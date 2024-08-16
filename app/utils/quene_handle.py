from queue import Queue
import pynvml

# 并发限制
CONCURRENT_LIMIT = 5
request_queue = Queue(maxsize=CONCURRENT_LIMIT)

# GPU 监控
# pynvml.nvmlInit()
# device_count = pynvml.nvmlDeviceGetCount()
# gpu_usage_threshold = 80  # GPU 使用率阈值

# def get_gpu_usage():
#     handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # 假设只监控第一个 GPU
#     util = pynvml.nvmlDeviceGetUtilizationRates(handle)
#     return util.gpu

async def process_request(request_func, *args, **kwargs):
    try:
        await request_func(*args, **kwargs)
    finally:
        request_queue.get()
        request_queue.task_done()