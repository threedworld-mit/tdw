import platform
import psutil
from tdw.version import __version__


if __name__ == "__main__":
    os_name = platform.system()
    cpu = f"{psutil.cpu_freq().current / 1000.0} Ghz {psutil.cpu_count()} Cores"
    memory = f"{round(round(psutil.virtual_memory().total / 1000000000))} GB"
    py_version = platform.python_version()

    # Get the GPU info.
    if os_name == "Windows":
        import wmi
        gpus = ", ".join(map(str, [gpu.Name for gpu in wmi.WMI().Win32_VideoController()]))
    else:
        from subprocess import check_output
        from re import search

        gpus = ", ".join(map(str, ["NVIDIA " + search(r":(.*)\(UUID", p.decode('utf-8')).group(1) for p in
                                   check_output(["nvidia-smi", "-L"]).split(b'\n') if p != b'']))

    print("| OS | CPU | Memory | GPU | Python | TDW |")
    print("| --- | --- | --- | --- | --- | --- |")
    print(f"| {os_name} | {cpu} | {memory} | {gpus} | {py_version} | {__version__} |")
