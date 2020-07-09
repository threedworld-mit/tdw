import platform
import psutil
from argparse import ArgumentParser
from benchmark_utils import PATH


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('machine', type=str, default='legion_lenovo')
    args = parser.parse_args()

    keys = {"legion_lenovo": "$MACHINE_WINDOWS", "braintree": "$MACHINE_BRAINTREE", "node11": "$MACHINE_NODE11"}

    txt = PATH.read_text()

    os_name = platform.system()
    cpu = str(psutil.cpu_freq()[0] / 1000.0) + " GHz " + str(psutil.cpu_count() + " Cores")
    memory = str(round(round(psutil.virtual_memory().total / 1000000000))) + " GB"
    py_version = platform.python_version()

    # Get the GPU info.
    if platform.system() == "Windows":
        import wmi
        gpus = ", ".join(map(str, [gpu.Name for gpu in wmi.WMI().Win32_VideoController()]))
    else:
        from subprocess import check_output
        from re import search

        gpus = ", ".join(map(str, ["NVIDIA " + search(r":(.*)\(UUID", p.decode('utf-8')).group(1) for p in
                                   check_output(["nvidia-smi", "-L"]).split(b'\n') if p != b'']))

    row = "| `" + args.machine + "` | " + os_name + " | " + cpu + " | " + memory + " | " + gpus + " | " + py_version + " |"
    print(row)

