import os
import sys
import platform
import logging
import subprocess
from pathlib import Path

# Tipos de plataforma
WINDOWS = "Windows"
MACOS = "Darwin"
LINUX = "Linux"


def get_platform():
    """Retorna a plataforma do sistema operacional"""
    return platform.system()


def get_ffmpeg_path():
    """
    Retorna o caminho para o executável do FFmpeg.
    Verifica múltiplos locais em ordem de prioridade:
    1. Diretório FFmpeg específico da aplicação (para versões empacotadas)
    2. Diretório da aplicação (para versões empacotadas)
    3. Pacote imageio-ffmpeg (se instalado)
    4. PATH do sistema
    """
    # Determinar a plataforma
    system = get_platform()

    # Nome do executável dependendo da plataforma
    executable_name = "ffmpeg.exe" if system == WINDOWS else "ffmpeg"

    # Verificar no diretório da aplicação (para versões empacotadas)
    # Já que estamos no mesmo pacote, esta importação funciona
    from buzz.assets import APP_BASE_DIR

    # Lista de possíveis diretórios para verificar
    possible_dirs = [
        # Primeiro lugar a procurar - pasta ffmpeg específica
        os.path.join(APP_BASE_DIR, "ffmpeg"),
        APP_BASE_DIR,
        os.path.join(APP_BASE_DIR, "dll_backup"),
        os.path.join(APP_BASE_DIR, "_internal"),
    ]

    if getattr(sys, 'frozen', False):
        # Se for versão empacotada, adiciona o diretório do executável e seus subdiretórios
        exe_dir = os.path.dirname(sys.executable)
        possible_dirs.insert(0, exe_dir)
        # Adicionar diretório ffmpeg específico no diretório do executável
        possible_dirs.insert(0, os.path.join(exe_dir, "ffmpeg"))
        # _internal no diretório do executável
        possible_dirs.append(os.path.join(exe_dir, "_internal"))

    # Log de debug mostrando os diretórios que serão pesquisados
    logging.debug(
        f"Procurando FFmpeg nos seguintes diretórios: {possible_dirs}")

    # Verificar cada diretório por um executável válido do FFmpeg
    for dir_path in possible_dirs:
        if not os.path.exists(dir_path):
            continue

        ffmpeg_path = os.path.join(dir_path, executable_name)
        if os.path.isfile(ffmpeg_path) and os.access(ffmpeg_path, os.X_OK):
            logging.debug(f"FFmpeg encontrado em: {ffmpeg_path}")
            return ffmpeg_path

        # Verificar subdiretório bin se existir
        bin_dir = os.path.join(dir_path, "bin")
        if os.path.exists(bin_dir):
            ffmpeg_bin_path = os.path.join(bin_dir, executable_name)
            if os.path.isfile(ffmpeg_bin_path) and os.access(ffmpeg_bin_path, os.X_OK):
                logging.debug(f"FFmpeg encontrado em: {ffmpeg_bin_path}")
                return ffmpeg_bin_path

    # Tentar usar o imageio-ffmpeg se estiver disponível
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
        logging.debug(f"FFmpeg encontrado via imageio-ffmpeg: {ffmpeg_path}")
        return ffmpeg_path
    except (ImportError, Exception) as e:
        logging.debug(f"Não foi possível obter ffmpeg via imageio-ffmpeg: {e}")

    # Tentar encontrar no PATH como último recurso
    try:
        if system == WINDOWS:
            # No Windows, verifica explicitamente se ffmpeg.exe está no PATH
            result = subprocess.run(
                ["where", "ffmpeg"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                path = result.stdout.strip().splitlines()[0]
                logging.debug(f"FFmpeg encontrado no PATH: {path}")
                return path
        else:
            # No Linux/Mac, usa which
            result = subprocess.run(
                ["which", "ffmpeg"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                logging.debug(f"FFmpeg encontrado no PATH: {path}")
                return path

        # Se o comando acima não funcionou, tenta uma verificação simples da versão
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if system == WINDOWS else 0
        )
        logging.debug("FFmpeg disponível no PATH")
        return "ffmpeg"  # Só o nome, pois está no PATH
    except Exception as e:
        logging.warning(f"FFmpeg não encontrado no PATH: {e}")

    logging.error("Não foi possível encontrar o FFmpeg instalado no sistema")
    return None


def run_ffmpeg_command(args, input_data=None, hide_window=True):
    """
    Executa um comando FFmpeg com os argumentos fornecidos.
    
    Args:
        args: Lista de argumentos para passar ao FFmpeg
        input_data: Dados de entrada opcionais para passar para stdin
        hide_window: Se deve ocultar a janela de comando (só Windows)
        
    Returns:
        Tuple[bool, str]: (sucesso, saída ou mensagem de erro)
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return False, "FFmpeg não encontrado no sistema"

    cmd = [ffmpeg_path] + args

    # Log completo do comando que será executado
    logging.debug(f"Executando comando FFmpeg: {cmd}")

    try:
        # Configurações específicas para Windows
        startupinfo = None
        creation_flags = 0

        if get_platform() == WINDOWS and hide_window:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creation_flags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            cmd,
            input=input_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=creation_flags
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            logging.warning(f"Erro ao executar FFmpeg: {error_msg}")
            return False, error_msg

        return True, result.stdout
    except Exception as e:
        logging.error(f"Exceção ao executar FFmpeg: {str(e)}")
        return False, str(e)
