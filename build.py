import subprocess
from ffmpeg_setup import setup_ffmpeg

def build(setup_kwargs):
    subprocess.call(["make", "buzz/whisper_cpp.py"])
    setup_ffmpeg()



if __name__ == "__main__":
    build({})
