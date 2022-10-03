from pathlib import Path
from subprocess import call
from platform import system


class ImagesToVideo:
    """
    Convert humanoid animation images to video with ffmpeg.
    """

    def __init__(self, root_src_dir: Path):
        """
        :param root_src_dir: Root source directory of images.
        """

        self.root_src_dir = root_src_dir

        if system() == "Windows":
            ffmpeg_path = Path.home().joinpath("ffmpeg.exe")
            assert ffmpeg_path.exists(), f"ffmpeg.exe not found at {ffmpeg_path}"
            self.ffmpeg_path = str(ffmpeg_path.resolve())
        elif system() == "Linux":
            self.ffmpeg_path = "ffmpeg"
        else:
            raise Exception(f"OS not supported: {system()}")

    def ffmpeg(self, src: Path) -> None:
        """
        Turn an image directory into a video.

        :param src: The source directory.
        """

        call([self.ffmpeg_path,
              "-r",
              "30",
              "-s",
              "1280x720",
              "-i",
              str(src.joinpath("%04d.jpg").resolve()),
              str(self.root_src_dir.joinpath(src.stem + ".mp4").resolve())])

    def ffmpeg_all(self) -> None:
        """
        Turn each image directory into a video.
        """

        for d in self.root_src_dir.iterdir():
            if d.is_dir():
                self.ffmpeg(d)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--dir", type=str, default="D:/humanoid_video_output", help="Output directory")
    args = parser.parse_args()
    ImagesToVideo(Path(args.dir)).ffmpeg_all()
