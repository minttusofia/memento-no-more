import torch

def print_gpu_utilization():
    from pyrsmi import rocml
    rocml.smi_initialize()
    ndevices = rocml.smi_get_device_count()
    used = [rocml.smi_get_device_memory_used(i) for i in range(ndevices)]
    s = "GPU memory used (MB): "
    for i in range(ndevices):
        s += f"[{i}]:{used[i]//1024**2} "
    print(s)
    rocml.smi_shutdown()
    return used

def print_gpu_utilization_cuda():
    import pynvml

    pynvml.nvmlInit()
    ndevices = pynvml.nvmlDeviceGetCount()
    used = []
    s = "GPU memory used (MB): "
    for i in range(ndevices):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        used_memory_mb = mem_info.used // 1024**3
        used.append(used_memory_mb)
        s += f"[{i}]:{used_memory_mb} "
    print(s)
    pynvml.nvmlShutdown()
    return used

def print_cuda_memory_utilization(rank=0):
    used = torch.cuda.memory_allocated(rank)
    print(f"CUDA[{rank}] memory allocated: {used//1024**2} MB.")
