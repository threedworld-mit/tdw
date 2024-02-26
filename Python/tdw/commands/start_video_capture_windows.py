# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.start_video_capture_command import StartVideoCaptureCommand
from typing import Dict


class StartVideoCaptureWindows(StartVideoCaptureCommand):
    """
    Start video capture using ffmpeg. This command can only be used on Windows.
    """

    def __init__(self, output_path: str, audio_device: str = "", audio_buffer_size: int = 5, draw_mouse: bool = False, ffmpeg: str = "", overwrite: bool = True, framerate: int = 60, position: Dict[str, int] = None, audio: bool = True, audio_codec: str = "aac", video_codec: str = "h264", preset: str = "ultrafast", qp: int = 1, pixel_format: str = "yuv420p", log_args: bool = False, override_args: str = ""):
        """
        :param output_path: The absolute path to the output file, e.g. /home/user/video.mp4
        :param audio_device: The name of the audio device. Ignored if audio == False. To get a list of devices: ffmpeg -list_devices true -f dshow -i dummy
        :param audio_buffer_size: The audio buffer size in ms. This should always be greater than 0. Adjust this if the audio doesn't sync with the video. See: [https://ffmpeg.org/ffmpeg-devices.html](https://ffmpeg.org/ffmpeg-devices.html) (search for audio_buffer_size).
        :param draw_mouse: If True, show the mouse in the video.
        :param ffmpeg: The path to the ffmpeg process. Set this parameter only if you're using a non-standard path.
        :param overwrite: If True, overwrite the video if it already exists.
        :param framerate: The framerate of the output video.
        :param position: The top-left corner of the screen region that will be captured. On Windows, this is ignored if window_capture == True.
        :param audio: If True, audio will be captured.
        :param audio_codec: The audio codec. You should usually keep this set to the default value. See: [https://ffmpeg.org/ffmpeg-codecs.html](https://ffmpeg.org/ffmpeg-codecs.html)
        :param video_codec: The video codec. You should usually keep this set to the default value. See: [https://ffmpeg.org/ffmpeg-codecs.html](https://ffmpeg.org/ffmpeg-codecs.html)
        :param preset: H.264 video encoding only. A preset of parameters that affect encoding speed and compression. See: [https://trac.ffmpeg.org/wiki/Encode/H.264](https://trac.ffmpeg.org/wiki/Encode/H.264)
        :param qp: H.264 video encoding only. This controls the video quality. 0 is lossless.
        :param pixel_format: The pixel format. You should almost never need to set this to anything other than the default value.
        :param log_args: If True, log the command-line arguments to the player log (this can additionally be received by the controller via the send_log_messages command).
        :param override_args: If not empty, replace the ffmpeg arguments with this string. Usually, you won't want to set this. If you want to use ffmpeg for something other than screen recording, consider launching it from a Python script using subprocess.call().
        """

        super().__init__(output_path=output_path, ffmpeg=ffmpeg, overwrite=overwrite, framerate=framerate, position=position, audio=audio, audio_codec=audio_codec, video_codec=video_codec, preset=preset, qp=qp, pixel_format=pixel_format, log_args=log_args, override_args=override_args)
        """:field
        The name of the audio device. Ignored if audio == False. To get a list of devices: ffmpeg -list_devices true -f dshow -i dummy
        """
        self.audio_device: str = audio_device
        """:field
        The audio buffer size in ms. This should always be greater than 0. Adjust this if the audio doesn't sync with the video. See: [https://ffmpeg.org/ffmpeg-devices.html](https://ffmpeg.org/ffmpeg-devices.html) (search for audio_buffer_size).
        """
        self.audio_buffer_size: int = audio_buffer_size
        """:field
        If True, show the mouse in the video.
        """
        self.draw_mouse: bool = draw_mouse
