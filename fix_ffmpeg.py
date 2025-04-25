"""
Script para corrigir problemas com o FFmpeg após a instalação do Buzz.
Este script busca pelo FFmpeg no computador e o configura corretamente para o Buzz.
CORRIGE INSTALAÇÕES DO BUZZ
EXECUTAR DENTRO DO DIRETÓRIO DO APLICATIVO INSTALADO

Detecta se o FFmpeg está instalado e funcionando
Se não estiver, baixa e instala a versão correta do FFmpeg
Modifica o arquivo ffmpeg_utils.py para melhorar a detecção do FFmpeg (apenas em ambiente de desenvolvimento)

Este script pode ser executado:

Durante o desenvolvimento para garantir que o FFmpeg esteja configurado corretamente
Após a instalação do pacote para corrigir problemas com o FFmpeg
"""

import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess
import tempfile
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# URL para baixar o FFmpeg
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"


def get_app_dir():
    """Retorna o diretório da aplicação Buzz"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def download_ffmpeg(dest_dir):
    """Baixa o FFmpeg e extrai para o diretório de destino"""
    logging.info(f"Baixando FFmpeg de {FFMPEG_URL}...")

    try:
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        zip_file = os.path.join(temp_dir, "ffmpeg.zip")

        # Baixar o arquivo
        urllib.request.urlretrieve(FFMPEG_URL, zip_file)
        logging.info("Download concluído. Extraindo...")

        # Extrair os arquivos
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Encontrar o diretório extraído
        extracted_dir = None
        for item in os.listdir(temp_dir):
            if os.path.isdir(os.path.join(temp_dir, item)) and item.startswith("ffmpeg"):
                extracted_dir = os.path.join(temp_dir, item)
                break

        if not extracted_dir:
            logging.error(
                "Não foi possível encontrar o diretório do FFmpeg extraído")
            return False

        # Copiar os arquivos do diretório bin para o destino
        bin_dir = os.path.join(extracted_dir, "bin")
        if not os.path.exists(bin_dir):
            logging.error(f"Diretório 'bin' não encontrado em {extracted_dir}")
            return False

        # Criar diretório de destino
        os.makedirs(dest_dir, exist_ok=True)

        # Copiar todos os arquivos de bin para o destino
        for file in os.listdir(bin_dir):
            src_path = os.path.join(bin_dir, file)
            dst_path = os.path.join(dest_dir, file)
            shutil.copy2(src_path, dst_path)
            logging.info(f"Copiado: {file}")

        logging.info(f"FFmpeg instalado com sucesso em {dest_dir}")
        return True

    except Exception as e:
        logging.error(f"Erro ao baixar ou extrair o FFmpeg: {e}")
        return False

    finally:
        # Limpar diretório temporário
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def test_ffmpeg(ffmpeg_path):
    """Testa se o FFmpeg está funcionando corretamente"""
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            logging.info(
                f"FFmpeg funcionando corretamente: {result.stdout.splitlines()[0]}")
            return True
        else:
            logging.error(f"Erro ao executar FFmpeg: {result.stderr}")
            return False

    except Exception as e:
        logging.error(f"Erro ao testar FFmpeg: {e}")
        return False


def check_and_fix_ffmpeg():
    """Verifica e corrige a instalação do FFmpeg"""
    app_dir = get_app_dir()
    logging.info(f"Diretório da aplicação: {app_dir}")

    # Caminhos possíveis para o FFmpeg
    ffmpeg_paths = [
        os.path.join(app_dir, "ffmpeg.exe"),
        os.path.join(app_dir, "ffmpeg", "ffmpeg.exe"),
        os.path.join(app_dir, "_internal", "ffmpeg.exe")
    ]

    # Verificar se o FFmpeg já existe e funciona
    for path in ffmpeg_paths:
        if os.path.exists(path) and test_ffmpeg(path):
            logging.info(
                f"FFmpeg existente está funcionando corretamente: {path}")
            return True

    # Se não encontrou um FFmpeg funcional, baixar e instalar
    logging.info(
        "Nenhum FFmpeg funcional encontrado. Baixando e instalando...")

    # Diretório de destino para o FFmpeg
    ffmpeg_dir = os.path.join(app_dir, "ffmpeg")

    # Baixar e instalar o FFmpeg
    if download_ffmpeg(ffmpeg_dir):
        # Testar a instalação
        if test_ffmpeg(os.path.join(ffmpeg_dir, "ffmpeg.exe")):
            logging.info("FFmpeg instalado e funcionando corretamente!")
            return True
        else:
            logging.error(
                "FFmpeg instalado mas não está funcionando corretamente.")
            return False
    else:
        logging.error("Falha ao baixar e instalar o FFmpeg.")
        return False


def create_modified_ffmpeg_utils():
    """Cria uma versão modificada do ffmpeg_utils.py para usar o FFmpeg correto"""
    app_dir = get_app_dir()

    # Caminho para o arquivo ffmpeg_utils.py
    if getattr(sys, "frozen", False):
        # Em versões empacotadas, não podemos modificar diretamente
        logging.warning(
            "Não é possível modificar ffmpeg_utils.py em versões empacotadas")
        return False

    # Em versões de desenvolvimento
    ffmpeg_utils_path = os.path.join(app_dir, "buzz", "ffmpeg_utils.py")
    if not os.path.exists(ffmpeg_utils_path):
        logging.error(
            f"Arquivo ffmpeg_utils.py não encontrado em {ffmpeg_utils_path}")
        return False

    # Conteúdo modificado
    new_content = """import os
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
    Verifica múltiplos locais em ordem de prioridade.
    """
    # Determinar a plataforma
    system = get_platform()

    # Nome do executável dependendo da plataforma
    executable_name = "ffmpeg.exe" if system == WINDOWS else "ffmpeg"

    # Determinar o diretório base da aplicação
    if getattr(sys, 'frozen', False):
        # Se for versão empacotada, usa o diretório do executável
        app_dir = os.path.dirname(sys.executable)
    else:
        # Durante o desenvolvimento
        try:
            from buzz.assets import APP_BASE_DIR
            app_dir = APP_BASE_DIR
        except ImportError:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Log de debug
    logging.debug(f"Diretório base da aplicação: {app_dir}")
    
    # Lista de possíveis caminhos para o ffmpeg
    possible_paths = [
        os.path.join(app_dir, "ffmpeg", "ffmpeg.exe"),
        os.path.join(app_dir, "ffmpeg"),
        os.path.join(app_dir, "ffmpeg.exe"),
        os.path.join(app_dir, executable_name),
        os.path.join(app_dir, "_internal", executable_name),
        os.path.join(app_dir, "dll_backup", executable_name)
    ]
    
    # Verificar cada caminho
    for path in possible_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                # Se for diretório, procurar executável dentro dele
                exe_path = os.path.join(path, executable_name)
                if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                    logging.debug(f"FFmpeg encontrado em: {exe_path}")
                    return exe_path
            elif os.path.isfile(path) and os.access(path, os.X_OK):
                logging.debug(f"FFmpeg encontrado em: {path}")
                return path
    
    # Se não encontrou nos caminhos específicos, tenta usar o imageio-ffmpeg
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
        logging.debug(f"FFmpeg encontrado via imageio-ffmpeg: {ffmpeg_path}")
        return ffmpeg_path
    except (ImportError, Exception) as e:
        logging.debug(f"Não foi possível obter FFmpeg via imageio-ffmpeg: {e}")
    
    # Finalmente, tenta verificar no PATH
    try:
        if system == WINDOWS:
            # No Windows, usa o comando 'where'
            try:
                cmd = subprocess.run(
                    ["where", "ffmpeg"], 
                    capture_output=True, 
                    text=True, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if cmd.returncode == 0:
                    path = cmd.stdout.strip().splitlines()[0]
                    logging.debug(f"FFmpeg encontrado no PATH: {path}")
                    return path
            except Exception as e:
                logging.debug(f"Erro ao usar 'where' para encontrar ffmpeg: {e}")
        else:
            # No Linux/Mac, usa o comando 'which'
            try:
                cmd = subprocess.run(
                    ["which", "ffmpeg"], 
                    capture_output=True, 
                    text=True
                )
                if cmd.returncode == 0:
                    path = cmd.stdout.strip()
                    logging.debug(f"FFmpeg encontrado no PATH: {path}")
                    return path
            except Exception as e:
                logging.debug(f"Erro ao usar 'which' para encontrar ffmpeg: {e}")
        
        # Último recurso: verificar se 'ffmpeg' está disponível diretamente
        try:
            cmd = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if system == WINDOWS else 0
            )
            if cmd.returncode == 0:
                logging.debug("FFmpeg encontrado no PATH como comando direto")
                return "ffmpeg"
        except Exception as e:
            logging.debug(f"Erro ao verificar versão do ffmpeg: {e}")
    except Exception as e:
        logging.warning(f"Erro ao verificar FFmpeg no PATH: {e}")
    
    logging.error("FFmpeg não encontrado. A transcrição de áudio pode não funcionar.")
    return None


def run_ffmpeg_command(args, input_data=None, hide_window=True):
    """
    Executa um comando FFmpeg com os argumentos fornecidos.

    Args:
        args: Lista de argumentos para passar ao FFmpeg
        input_data: Dados de entrada opcionais para passar para stdin
        hide_window: Se deve ocultar a janela de comando(só Windows)

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

        # Adicionar o diretório do FFmpeg ao PATH temporariamente
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        orig_path = os.environ.get('PATH', '')
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + orig_path

        result = subprocess.run(
            cmd,
            input=input_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=creation_flags,
            env=os.environ
        )

        # Restaurar PATH original
        os.environ['PATH'] = orig_path

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            logging.warning(f"Erro ao executar FFmpeg: {error_msg}")
            return False, error_msg

        return True, result.stdout
    except Exception as e:
        # Restaurar PATH original em caso de exceção
        if 'orig_path' in locals():
            os.environ['PATH'] = orig_path
        logging.error(f"Exceção ao executar FFmpeg: {str(e)}")
        return False, str(e)
"""

    # Criar backup do arquivo original
    backup_path = ffmpeg_utils_path + ".bak"
    shutil.copy2(ffmpeg_utils_path, backup_path)
    logging.info(f"Backup do ffmpeg_utils.py criado em {backup_path}")

    # Escrever o novo conteúdo
    with open(ffmpeg_utils_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    logging.info(f"ffmpeg_utils.py modificado com sucesso")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Utilitário de correção do FFmpeg para o Buzz")
    print("=" * 60)

    if check_and_fix_ffmpeg():
        print("\nFFmpeg configurado com sucesso!")

        # Perguntar se deseja modificar o ffmpeg_utils.py
        if not getattr(sys, "frozen", False):
            response = input(
                "\nDeseja modificar o arquivo ffmpeg_utils.py para melhorar a detecção do FFmpeg? (s/n): ")
            if response.lower() in ["s", "sim", "y", "yes"]:
                if create_modified_ffmpeg_utils():
                    print("\nArquivo ffmpeg_utils.py modificado com sucesso!")
                else:
                    print("\nNão foi possível modificar o arquivo ffmpeg_utils.py.")

        print("\nO Buzz deve funcionar corretamente agora.")
        sys.exit(0)
    else:
        print("\nNão foi possível configurar o FFmpeg corretamente.")
        print("Por favor, entre em contato com o suporte.")
        sys.exit(1)
