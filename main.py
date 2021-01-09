"""
ffmpeg wrapper
"""
import os
import shutil
import subprocess
import tempfile


class FFmpeg:
    """
    ffmpeg object
    """

    def __init__(self):
        self.path = tempfile.mkdtemp()
        self.file_list = os.path.join(self.path, "file_list.txt")
        self.parts = []

    def add_cover(self, file_image):
        """
        add a cover frame
        """
        second = 0.5
        output = os.path.join(self.path, "cover.mp4")
        cmd = [
            "ffmpeg",
            "-loglevel",
            "error",
            "-loop",
            "1",
            "-r",
            "10",
            "-i",
            file_image,
            "-vframes",
            f"{10*second}",
            "-pix_fmt",
            "yuv420p",
            "-y",
            output,
        ]
        subprocess.call(cmd, shell=False)
        with open(self.file_list, "w") as file_list:
            print("file 'cover.mp4'", file=file_list)

    def add_image(self, file_image):
        """
        add an image to queue
        """
        self.parts.append({"image": file_image, "audios": []})

    def add_audio(self, file_audio):
        """
        add an audio to queue
        """
        seconds = self.get_length(file_audio)
        self.parts[-1]["audios"].append(
            {
                "file": file_audio,
                "seconds": seconds,
            }
        )

    def add_silence(self, seconds=1):
        """
        add silence to queue
        """
        self.parts[-1]["silence"] = seconds

    @staticmethod
    def get_length(file_in):
        """
        get the length of file_in in seconds
        """
        length = float(
            subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    file_in,
                ],
                stdout=subprocess.PIPE,
                check=False,
            )
            .stdout.decode("utf-8")
            .replace('"', "")
        )
        return length

    def generate(self, file_output):
        """
        generate the video output
        """
        idx_last_part = len(self.parts) - 1
        with open(self.file_list, "a") as file_list:
            for idx_part, part in enumerate(self.parts):
                idx_last_audio = len(part["audios"]) - 1
                file_image = part["image"]
                for idx_audio, audio in enumerate(part["audios"]):
                    if idx_part == idx_last_part:
                        if idx_audio == idx_last_audio:
                            pass
                    output = f"{idx_part}-{idx_audio}.mp4"
                    self.generate_mov(
                        file_image,
                        audio,
                        output,
                    )
                    print(f"file '{output}'", file=file_list)
        self.concat_videos(file_output)
        print(f"========= path: {self.path}")
        shutil.rmtree(self.path)

    def generate_mov(self, file_image, audio, file_output):
        """generate mov using an image and a audio"""
        output = os.path.join(self.path, file_output)
        cmd = [
            "ffmpeg",
            "-loglevel",
            "error",
            "-framerate",
            f"1/{audio['seconds']+0.3}",
            "-i",
            file_image,
            "-i",
            audio["file"],
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            "-y",
            output,
        ]
        subprocess.call(cmd, shell=False)

    def concat_videos(self, file_output):
        """concat multiple videos"""
        cmd = [
            "ffmpeg",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-i",
            self.file_list,
            "-safe",
            "0",
            "-y",
            file_output,
        ]
        subprocess.call(cmd, shell=False)


def main():
    """main"""
    ffmpeg = FFmpeg()
    ffmpeg.add_cover("./zoo.png")
    ffmpeg.add_image("./above.png")
    ffmpeg.add_audio("./above.0.google.mp3")
    ffmpeg.add_audio("./above.1.youdao.mp3")
    ffmpeg.add_audio("./above.2.shanbay.mp3")
    ffmpeg.add_silence()
    ffmpeg.add_image("./and.png")
    ffmpeg.add_audio("./and.0.google.mp3")
    ffmpeg.add_audio("./and.1.youdao.mp3")
    ffmpeg.add_audio("./and.2.shanbay.mp3")
    ffmpeg.add_silence()
    ffmpeg.generate("out.mp4")


if __name__ == "__main__":
    main()
