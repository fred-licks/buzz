import os
import sys
import platform
import shutil
import urllib.request
import zipfile
import tarfile
import tempfile
import subprocess
from pathlib import Path

# URLs para download do FFmpeg por plataforma
FFMPEG_DOWNLOADS = {
    "Windows": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
    "Darwin": "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip",
    "Linux": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
}


def get_platform():
    """Retorna a plataforma do sistema"""
    return platform.system()


def download_ffmpeg():
    """Baixa o FFmpeg para a plataforma atual"""
    system = get_platform()

    if system not in FFMPEG_DOWNLOADS:
        print(f"Plataforma não suportada: {system}", file=sys.stderr)
        return None

    url = FFMPEG_DOWNLOADS[system]
    print(f"Baixando FFmpeg de {url}...")

    temp_dir = tempfile.mkdtemp()
    try:
        # Baixar o arquivo
        temp_file = os.path.join(
            temp_dir, f"ffmpeg-{system}.zip" if system != "Linux" else "ffmpeg-linux.tar.xz")
        urllib.request.urlretrieve(url, temp_file)

        # Extrair para o diretório temporário
        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)

        if system == "Linux":
            with tarfile.open(temp_file) as tar:
                tar.extractall(path=extract_dir)
        else:
            with zipfile.ZipFile(temp_file) as zip_ref:
                zip_ref.extractall(extract_dir)

        # Procurar pelo executável do FFmpeg
        ffmpeg_exe = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file == "ffmpeg" or file == "ffmpeg.exe":
                    ffmpeg_exe = os.path.join(root, file)
                    break
            if ffmpeg_exe:
                break

        if not ffmpeg_exe:
            print(
                "Não foi possível encontrar o executável do FFmpeg no arquivo baixado", file=sys.stderr)
            return None

        # Tornar executável no Linux/Mac
        if system != "Windows":
            os.chmod(ffmpeg_exe, 0o755)

        return ffmpeg_exe

    except Exception as e:
        print(f"Erro ao baixar ou extrair o FFmpeg: {e}", file=sys.stderr)
        return None


def ensure_ffmpeg_in_dist():
    """Garante que o FFmpeg esteja na pasta de distribuição"""
    system = get_platform()
    dist_dir = Path("dist/Buzz_PCRS/ffmpeg")
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Tentar localizar o FFmpeg existente
    try:
        # Tentar via imageio-ffmpeg primeiro
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_exe = get_ffmpeg_exe()
        print(f"FFmpeg encontrado via imageio-ffmpeg: {ffmpeg_exe}")
    except:
        # Se falhar, tentar baixar
        print("Tentando baixar o FFmpeg...")
        ffmpeg_exe = download_ffmpeg()

    if not ffmpeg_exe:
        print("Não foi possível obter o FFmpeg. A aplicação pode não funcionar corretamente.", file=sys.stderr)
        return False

    # Copiar para o diretório de distribuição
    dest_file = dist_dir / ("ffmpeg.exe" if system == "Windows" else "ffmpeg")
    shutil.copy2(ffmpeg_exe, dest_file)
    print(f"FFmpeg copiado para: {dest_file}")

    # No Windows, procurar DLLs necessárias
    if system == "Windows":
        ffmpeg_dir = Path(ffmpeg_exe).parent
        for file in ffmpeg_dir.glob("*.dll"):
            dest_dll = dist_dir / file.name
            shutil.copy2(file, dest_dll)
            print(f"Copiada DLL: {dest_dll}")

    return True


if __name__ == "__main__":
    if ensure_ffmpeg_in_dist():
        print("FFmpeg configurado com sucesso para a distribuição!")
        sys.exit(0)
    else:
        print("Falha ao configurar o FFmpeg!", file=sys.stderr)
        sys.exit(1)
