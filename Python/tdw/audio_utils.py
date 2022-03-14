from typing import Optional, Union, Tuple
from pathlib import Path
import os
from platform import system
from subprocess import check_output, Popen, call
import re
from psutil import pid_exists


class AudioUtils:
    """
    Utility class for recording audio in TDW using [fmedia](https://stsaz.github.io/fmedia/).

    Usage:

    ```python
    from tdw.audio_utils import AudioUtils
    from tdw.controller import Controller

    c = Controller()

    initialize_trial()  # Your code here.

    # Begin recording audio. Automatically stop recording at 10 seconds.
    AudioUtils.start(output_path="path/to/file.wav", until=(0, 10))

    do_trial()  # Your code here.

    # Stop recording.
    AudioUtils.stop()
    ```
    """

    # The process ID of the audio recorder.
    RECORDER_PID: Optional[int] = None
    # The audio capture device.
    DEVICE: Optional[str] = None

    @staticmethod
    def get_system_audio_device(device_name: str = None) -> str:
        """
        :param device_name: The name of the audio capture device. If None, defaults to `"Stereo Mix"` (Windows and Linux) or `"iShowU Audio Capture"` (OS X).

        :return: The audio device that can be used to capture system audio.
        """

        # Set a default device name.
        if device_name is None:
            if system() == "Darwin":
                device_name = "iShowU Audio Capture"
            else:
                device_name = "Stereo Mix"
        devices = check_output(["fmedia", "--list-dev"]).decode("utf-8").split("Capture:")[1]
        dev_search = re.search(f"device #(.*): {device_name}", devices, flags=re.MULTILINE)
        assert dev_search is not None, "No suitable audio capture device found:\n" + devices
        return dev_search.group(1)

    @staticmethod
    def start(output_path: Union[str, Path], until: Optional[Tuple[int, int]] = None, device_name: str = None) -> None:
        """
        Start recording audio.

        :param output_path: The path to the output file.
        :param until: If not None, fmedia will record until `minutes:seconds`. The value must be a tuple of 2 integers. If None, fmedia will record until you send `AudioUtils.stop()`.
        :param device_name: The name of the audio capture device. If None, defaults to `"Stereo Mix"` (Windows and Linux) or `"iShowU Audio Capture"` (OS X).
        """

        if isinstance(output_path, str):
            p = Path(output_path).resolve()
        else:
            p = output_path

        # Create the directory.
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        # Set the capture device.
        if AudioUtils.DEVICE is None:
            AudioUtils.DEVICE = AudioUtils.get_system_audio_device(device_name=device_name)
        fmedia_call = ["fmedia",
                       "--record",
                       f"--dev-capture={AudioUtils.DEVICE}",
                       f"--out={str(p.resolve())}",
                       "--globcmd=listen"]
        # Automatically stop recording.
        if until is not None:
            fmedia_call.append(f"--until={str(until[0]).zfill(2)}:{str(until[1]).zfill(2)}")
        with open(os.devnull, "w+") as f:
            AudioUtils.RECORDER_PID = Popen(fmedia_call,
                                            stderr=f).pid

    @staticmethod
    def stop() -> None:
        """
        Stop recording audio (if any fmedia process is running).
        """

        if AudioUtils.RECORDER_PID is not None:
            with open(os.devnull, "w+") as f:
                call(['fmedia', '--globcmd=quit'], stderr=f, stdout=f)
            AudioUtils.RECORDER_PID = None

    @staticmethod
    def is_recording() -> bool:
        """
        :return: True if the fmedia recording process still exists.
        """

        return AudioUtils.RECORDER_PID is not None and pid_exists(AudioUtils.RECORDER_PID)
