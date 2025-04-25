import os
import sys
import subprocess
from pathlib import Path


def install_ffmpeg_dependency():
    """Instala o imageio-ffmpeg como dependência do Poetry"""
    try:
        subprocess.run(
            ["poetry", "run", "python", "-c", "import imageio_ffmpeg"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("imageio-ffmpeg já está instalado.")
        return True
    except subprocess.CalledProcessError:
        print("Instalando imageio-ffmpeg...")
        try:
            subprocess.run(["poetry", "add", "imageio-ffmpeg"], check=True)
            print("imageio-ffmpeg instalado com sucesso.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro ao instalar imageio-ffmpeg: {e}")
            return False


def create_ffmpeg_utils():
    """Cria o módulo de utilidades para o ffmpeg"""
    utils_dir = Path("buzz")
    utils_file = utils_dir / "ffmpeg_utils.py"

    if utils_file.exists():
        print("Módulo ffmpeg_utils.py já existe.")
        return True

    print("Criando módulo ffmpeg_utils.py...")
    utils_content = """
import os
import sys
import subprocess
from pathlib import Path

def get_ffmpeg_path():
    \"\"\"
    Retorna o caminho para o executável do ffmpeg.
    Primeiro tenta usar o imageio-ffmpeg, depois verifica no diretório da aplicação.
    \"\"\"
    # Primeiro, tente usar o imageio-ffmpeg se estiver disponível
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except (ImportError, Exception) as e:
        print(f"Não foi possível obter ffmpeg via imageio-ffmpeg: {e}", file=sys.stderr)
    
    # Se a importação falhar, tente localizar o ffmpeg no diretório da aplicação
    try:
        # Determinar o diretório base da aplicação
        if getattr(sys, 'frozen', False):
            # Se empacotado com alguma ferramenta
            base_dir = Path(sys.executable).parent
        else:
            # Durante o desenvolvimento
            base_dir = Path(__file__).parent.parent
        
        # Verificar vários caminhos possíveis
        potential_paths = [
            base_dir / "ffmpeg" / "ffmpeg.exe",
            base_dir / "ffmpeg" / "ffmpeg-win64-v4.2.2.exe",
            base_dir / "ffmpeg" / "ffmpeg",
        ]
        
        for path in potential_paths:
            if path.exists():
                return str(path)
        
        # Verificar no PATH como último recurso
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return "ffmpeg"  # Está no PATH
        except:
            pass
        
        print("Não foi possível encontrar o executável do ffmpeg", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Erro ao localizar ffmpeg: {e}", file=sys.stderr)
        return None

def run_ffmpeg(args):
    \"\"\"Executa o ffmpeg com os argumentos fornecidos\"\"\"
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return False, "Não foi possível encontrar o executável do ffmpeg"
    
    try:
        command = [ffmpeg_path] + args
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            return False, result.stderr
        return True, result.stdout
    except Exception as e:
        return False, f"Erro ao executar ffmpeg: {str(e)}"
"""

    with open(utils_file, "w") as f:
        f.write(utils_content)

    print("Módulo ffmpeg_utils.py criado com sucesso.")
    return True


def create_copy_script():
    """Cria o script para copiar os arquivos do ffmpeg"""
    copy_script = Path("copy_ffmpeg.py")

    if copy_script.exists():
        print("Script copy_ffmpeg.py já existe.")
        return True

    print("Criando script copy_ffmpeg.py...")
    script_content = """
import os
import sys
import shutil
from pathlib import Path

def copy_ffmpeg_files():
    \"\"\"Copia os arquivos do ffmpeg para o diretório de distribuição\"\"\"
    try:
        # Importar e usar imageio_ffmpeg
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_exe = get_ffmpeg_exe()
        print(f"FFmpeg encontrado em: {ffmpeg_exe}")
        
        # Diretório base do ffmpeg
        ffmpeg_dir = Path(ffmpeg_exe).parent
        
        # Diretório de destino na distribuição
        dist_dir = Path("dist/Buzz/ffmpeg")
        dist_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar o executável principal
        dest_file = dist_dir / Path(ffmpeg_exe).name
        shutil.copy2(ffmpeg_exe, dest_file)
        print(f"Copiado: {dest_file}")
        
        # Procurar por DLLs ou outros arquivos relacionados
        for file in ffmpeg_dir.glob("*"):
            if file.is_file() and file.name != Path(ffmpeg_exe).name:
                dest_file = dist_dir / file.name
                shutil.copy2(file, dest_file)
                print(f"Copiado arquivo adicional: {dest_file}")
        
        print("Cópia dos arquivos do ffmpeg concluída")
        return 0
    except Exception as e:
        print(f"Erro ao copiar arquivos do ffmpeg: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(copy_ffmpeg_files())
"""

    with open(copy_script, "w") as f:
        f.write(script_content)

    print("Script copy_ffmpeg.py criado com sucesso.")
    return True


def check_makefile():
    """Verifica o Makefile e fornece instruções"""
    print("\nVerifique seu Makefile e adicione a seguinte linha à regra bundle_windows:")
    print("bundle_windows: dist/Buzz")
    print("\tpoetry run python copy_ffmpeg.py")
    print("\tiscc //DAppVersion=${version} installer.iss")


def setup_ffmpeg():
    """Função principal para configurar o suporte ao ffmpeg"""
    print("Configurando suporte ao ffmpeg...")
    install_ffmpeg_dependency()
    create_ffmpeg_utils()
    create_copy_script()
    check_makefile()
    print("Configuração do ffmpeg concluída!")
