
import os
import sys
import shutil
from pathlib import Path

def copy_ffmpeg_files():
    """Copia os arquivos do ffmpeg para o diret�rio de distribui��o"""
    try:
        # Importar e usar imageio_ffmpeg
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_exe = get_ffmpeg_exe()
        print(f"FFmpeg encontrado em: {ffmpeg_exe}")
        
        # Diret�rio base do ffmpeg
        ffmpeg_dir = Path(ffmpeg_exe).parent
        
        # Diret�rio de destino na distribui��o
        dist_dir = Path("dist/Buzz_PCRS/ffmpeg")
        dist_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar o execut�vel principal
        dest_file = dist_dir / Path(ffmpeg_exe).name
        shutil.copy2(ffmpeg_exe, dest_file)
        print(f"Copiado: {dest_file}")
        
        # Procurar por DLLs ou outros arquivos relacionados
        for file in ffmpeg_dir.glob("*"):
            if file.is_file() and file.name != Path(ffmpeg_exe).name:
                dest_file = dist_dir / file.name
                shutil.copy2(file, dest_file)
                print(f"Copiado arquivo adicional: {dest_file}")
        
        print("C�pia dos arquivos do ffmpeg conclu�da")
        return 0
    except Exception as e:
        print(f"Erro ao copiar arquivos do ffmpeg: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(copy_ffmpeg_files())
