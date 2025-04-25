import os
import sys
import shutil
import zipfile
import urllib.request
import tempfile
import platform
import subprocess
from pathlib import Path

# URL para baixar o FFmpeg (versão que você mencionou que funciona)
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"


def download_and_extract_ffmpeg():
    """Baixa e extrai o FFmpeg para o diretório do projeto"""
    print("Baixando e extraindo o FFmpeg...")

    # Criar diretório ffmpeg se não existir
    ffmpeg_dir = Path("ffmpeg")
    if not ffmpeg_dir.exists():
        ffmpeg_dir.mkdir(parents=True)

    # Baixar o arquivo
    temp_dir = tempfile.mkdtemp()
    zip_file = os.path.join(temp_dir, "ffmpeg.zip")

    try:
        print(f"Baixando FFmpeg de {FFMPEG_URL}...")
        urllib.request.urlretrieve(FFMPEG_URL, zip_file)

        print("Extraindo arquivo...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Encontrar a pasta extraída (geralmente ffmpeg-master-latest-win64-gpl)
        extracted_dir = None
        for item in os.listdir(temp_dir):
            if os.path.isdir(os.path.join(temp_dir, item)) and item.startswith("ffmpeg"):
                extracted_dir = os.path.join(temp_dir, item)
                break

        if not extracted_dir:
            print(
                "Não foi possível encontrar o diretório do FFmpeg extraído", file=sys.stderr)
            return False

        # Copiar arquivos da pasta bin para o diretório ffmpeg do projeto
        bin_dir = os.path.join(extracted_dir, "bin")
        if os.path.exists(bin_dir):
            for file in os.listdir(bin_dir):
                src_file = os.path.join(bin_dir, file)
                dst_file = os.path.join("ffmpeg", file)
                shutil.copy2(src_file, dst_file)
                print(f"Copiado: {file}")

        print("FFmpeg preparado com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao baixar ou extrair o FFmpeg: {e}", file=sys.stderr)
        return False

    finally:
        # Limpar arquivos temporários
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def verify_ffmpeg():
    """Verifica se o FFmpeg está funcionando corretamente"""
    print("Verificando instalação do FFmpeg...")

    ffmpeg_exe = os.path.join("ffmpeg", "ffmpeg.exe")
    if not os.path.exists(ffmpeg_exe):
        print(f"Arquivo {ffmpeg_exe} não encontrado!", file=sys.stderr)
        return False

    try:
        result = subprocess.run(
            [ffmpeg_exe, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            print(f"FFmpeg instalado e funcionando corretamente:")
            print(result.stdout.splitlines()[0])
            return True
        else:
            print(f"Erro ao executar FFmpeg: {result.stderr}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"Erro ao verificar FFmpeg: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if platform.system() != "Windows":
        print("Este script é apenas para Windows.", file=sys.stderr)
        sys.exit(1)

    # Verificar se já existe
    if os.path.exists(os.path.join("ffmpeg", "ffmpeg.exe")):
        print("FFmpeg já está presente. Verificando...")
        if verify_ffmpeg():
            print("FFmpeg existente está OK!")
            sys.exit(0)
        else:
            print("FFmpeg existente apresenta problemas. Baixando novamente...")

    # Baixar e extrair
    if download_and_extract_ffmpeg():
        if verify_ffmpeg():
            print("Preparação do FFmpeg concluída com sucesso!")
            sys.exit(0)
        else:
            print("FFmpeg instalado mas apresenta problemas.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Falha ao preparar o FFmpeg.", file=sys.stderr)
        sys.exit(1)
