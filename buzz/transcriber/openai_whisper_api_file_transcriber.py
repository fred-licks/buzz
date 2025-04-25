import logging
import math
import os
import tempfile
from typing import Optional, List

from PyQt6.QtCore import QObject
from openai import OpenAI

from buzz.settings.settings import Settings
from buzz.model_loader import get_custom_api_whisper_model
from buzz.transcriber.file_transcriber import FileTranscriber
from buzz.transcriber.transcriber import FileTranscriptionTask, Segment, Task
# Importar o novo módulo do diretório correto
from buzz.ffmpeg_utils import run_ffmpeg_command, get_platform


class OpenAIWhisperAPIFileTranscriber(FileTranscriber):
    def __init__(self, task: FileTranscriptionTask, parent: Optional["QObject"] = None):
        super().__init__(task=task, parent=parent)
        settings = Settings()
        custom_openai_base_url = settings.value(
            key=Settings.Key.CUSTOM_OPENAI_BASE_URL, default_value=""
        )
        self.task = task.transcription_options.task
        self.openai_client = OpenAI(
            api_key=self.transcription_task.transcription_options.openai_access_token,
            base_url=custom_openai_base_url if custom_openai_base_url else None
        )
        self.whisper_api_model = get_custom_api_whisper_model(
            custom_openai_base_url)
        logging.debug("Will use whisper API on %s, %s",
                      custom_openai_base_url, self.whisper_api_model)

    def transcribe(self) -> List[Segment]:
        logging.debug(
            "Starting OpenAI Whisper API file transcription, file path = %s, task = %s",
            self.transcription_task.file_path,
            self.task,
        )

        mp3_file = tempfile.mktemp() + ".mp3"

        # Usar o novo módulo ffmpeg_utils para conversão do arquivo de áudio
        cmd = [
            "-threads", "0",
            "-loglevel", "panic",
            "-i", self.transcription_task.file_path, mp3_file
        ]

        success, error_msg = run_ffmpeg_command(cmd)

        if not success:
            logging.warning(f"FFMPEG audio load error. Error: {error_msg}")
            raise Exception(f"FFMPEG Failed to load audio: {error_msg}")

        # Usar o ffprobe para obter a duração do arquivo
        # Primeiro tentamos obter o caminho do ffprobe baseado no caminho do ffmpeg
        ffprobe_cmd = [
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            mp3_file
        ]

        # Tentar usar o ffprobe através da nossa utilidade
        import subprocess
        from pathlib import Path

        # Obter o caminho do ffmpeg para tentar localizar o ffprobe no mesmo diretório
        ffmpeg_path = None
        from buzz.ffmpeg_utils import get_ffmpeg_path
        ffmpeg_path = get_ffmpeg_path()

        duration_secs = 0

        if ffmpeg_path:
            # Tentar encontrar o ffprobe no mesmo diretório do ffmpeg
            ffprobe_path = os.path.join(
                os.path.dirname(ffmpeg_path), "ffprobe")
            if os.path.exists(ffprobe_path) or os.path.exists(ffprobe_path + ".exe"):
                ffprobe_executable = ffprobe_path if not get_platform() == "Windows" else (
                    ffprobe_path if os.path.exists(
                        ffprobe_path) else ffprobe_path + ".exe"
                )

                startupinfo = None
                if get_platform() == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE

                try:
                    # Executar ffprobe diretamente
                    result = subprocess.run(
                        [ffprobe_executable] + ffprobe_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        startupinfo=startupinfo,
                        check=True
                    )
                    duration_secs = float(
                        result.stdout.decode("utf-8").strip())
                    logging.debug(
                        f"File duration from ffprobe: {duration_secs} seconds")
                except Exception as e:
                    logging.warning(f"Error using ffprobe directly: {str(e)}")
                    # Valor padrão se falhar
                    duration_secs = 0
            else:
                # Se não encontrar o ffprobe, tentar executar o comando como "ffprobe"
                try:
                    cmd_result = run_ffmpeg_command(
                        ffprobe_cmd, executable="ffprobe")
                    if cmd_result[0]:  # Se bem-sucedido
                        duration_secs = float(
                            cmd_result[1].decode("utf-8").strip())
                        logging.debug(
                            f"File duration from ffprobe command: {duration_secs} seconds")
                except Exception as e:
                    logging.warning(f"Error using ffprobe command: {str(e)}")
                    duration_secs = 0

        # Se não conseguiu obter a duração, usar uma estimativa baseada no tamanho do arquivo
        if duration_secs <= 0:
            # Estimativa aproximada: 1MB ~= 1 minuto para MP3 de qualidade média
            file_size_mb = os.path.getsize(mp3_file) / (1024 * 1024)
            duration_secs = file_size_mb * 60  # Estimativa grosseira
            logging.debug(
                f"Estimated duration from file size: {duration_secs} seconds")

        total_size = os.path.getsize(mp3_file)
        max_chunk_size = 25 * 1024 * 1024

        self.progress.emit((0, 100))

        if total_size < max_chunk_size:
            return self.get_segments_for_file(mp3_file)

        # Se o arquivo for maior que 25MB, dividir em chunks
        # e transcrever cada chunk separadamente
        num_chunks = math.ceil(total_size / max_chunk_size)
        # 60 segundos padrão se não temos duração
        chunk_duration = duration_secs / num_chunks if duration_secs > 0 else 60

        segments = []

        for i in range(num_chunks):
            chunk_start = i * chunk_duration
            chunk_end = min((i + 1) * chunk_duration,
                            duration_secs if duration_secs > 0 else float("inf"))

            chunk_file = tempfile.mktemp() + ".mp3"

            # Usar o novo módulo ffmpeg_utils para cortar o chunk
            chunk_cmd = [
                "-i", mp3_file,
                "-ss", str(chunk_start),
                "-to", str(chunk_end),
                "-c", "copy",
                chunk_file
            ]

            success, error_msg = run_ffmpeg_command(chunk_cmd)

            if not success:
                logging.warning(
                    f"Failed to create chunk file. Skipping chunk {i+1}/{num_chunks}: {error_msg}")
                continue

            logging.debug(f'Created chunk file "{chunk_file}"')

            segments.extend(
                self.get_segments_for_file(
                    chunk_file, offset_ms=int(chunk_start * 1000)
                )
            )
            os.remove(chunk_file)
            self.progress.emit((i + 1, num_chunks))

        return segments

    def get_segments_for_file(self, file: str, offset_ms: int = 0):
        with open(file, "rb") as file:
            options = {
                "model": self.whisper_api_model,
                "file": file,
                "response_format": "verbose_json",
                "prompt": self.transcription_task.transcription_options.initial_prompt,
            }
            transcript = (
                self.openai_client.audio.transcriptions.create(
                    **options,
                    language=self.transcription_task.transcription_options.language,
                )
                if self.transcription_task.transcription_options.task == Task.TRANSCRIBE
                else self.openai_client.audio.translations.create(**options)
            )

            return [
                Segment(
                    int(segment["start"] * 1000 + offset_ms),
                    int(segment["end"] * 1000 + offset_ms),
                    segment["text"],
                )
                for segment in transcript.model_extra["segments"]
            ]

    def stop(self):
        pass
