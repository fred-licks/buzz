Criação do arquivo de tradução

## Preparo pré-compilação

conda activate buzz

**# 1. Verificar que está no ambiente correto (deve mostrar (buzz))**
**echo**"Ambiente ativo: **$env**:CONDA_DEFAULT_ENV"

**# 2. Copiar DLLs (se ainda não fez)**
**Copy-Item**-Recurse **-**Force **"dll_backup\*"**"buzz\"

**Verificar: execução de setup_arquivos_precompilados.ps1**

## **Compilação do Buzz no Windows**

Assume-se que você tenha Git e Python instalados e adicionados ao PATH.

### Instale o gerenciador de pacotes chocolatey para Windows:

```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol =~ [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Instale o GNU make

```
choco install make
```

### Instale o ffmpeg:

```
choco install ffmpeg
```

### Instale o MSYS2:

Siga as instruções encontradas em https://sajidifti.medium.com/how-to-install-gcc-and-gdb-on-windows-using-msys2-tutorial-0fceb7e66454. O passo a passo se encontra traduzido ao final deste tutorial.

### Instale o Poetry:

Cole os seguinte comandos no Windows PowerShell, linha por linha:

```
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -[Environment]::SetEnvironmentVariable("Path", $env:Path + ";%APPDATA%\\pypoetry\\venv\\Scripts", "User")Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Adicione o poetry ao PATH:

Usar a expressão: '%APPDATA%\\Python\\Scripts'

### Reinicie o Windows.

### Clone o repositório do Buzz:

```
git clone --recursive https://github.com/chidiwilliams/buzz.git
```

### Entre na pasta do repositório:

```
cd buzz
```

### Instale o plugin de ambiente virtual:

```
poetry self add poetry-plugin-shell
```

### Ative o ambiente virtual:

```
poetry shell
```

Implemente a tradução:

```
make translation_mo
```

Instale as dependências:

```
poetry install
```

Faça o backup de dlls:

```
cp -r .\\dll_backup\\ .\\buzz\\
```

Compile o Buzz:

```
poetry build
```

Execute o Buzz:

```
python -m buzz
```

Note: It should be safe to ignore any "syntax errors" you see during the build. Buzz will work. Also you can ignore any errors for FFmpeg. Buzz tries to load FFmpeg by several different means and some of them throw errors, but FFmpeg should eventually be found and work.

### Solução de erros

Para problemas relacionados ao ambiente de desenvolvimento, fazer tudo do zero. Comece executando:

```
poetry env remove

```

```
poetry cache clear . --all

```

Em seguida, delete o arquivo poetry.lock. Então execute:

```
poetry install
```

Se enfrentar problemas ao executar o programa no ambiente de desenvolvimento, faça o seguinte:

```
pip uninstall torch torchaudio
pip install torch==2.6.0+cu124 torchaudio==2.6.0+cu124 --index-url https://download.pytorch.org/whl/cu124
pip install nvidia-cublas-cu12==12.4.5.8 nvidia-cuda-cupti-cu12==12.4.127 nvidia-cuda-nvrtc-cu12==12.4.127 nvidia-cuda-runtime-cu12==12.4.127 nvidia-cufft-cu12==11.2.1.3 nvidia-curand-cu12==10.3.5.147 nvidia-cusolver-cu12==11.6.1.9 nvidia-cusparse-cu12==12.3.1.170 nvidia-nvtx-cu12==12.4.127
```

Se ainda não funcionar, tente verificar se há erros relacionados ao FFmpeg na inicialização:

```
set BUZZ_FORCE_CPU=true
```

# Criação da versão para distribuição

## Windows

### Método adotado pelo Fred Licks (funciona):

**# Para compilação com console de debug**

```
$env:PYINSTALLER_DEBUG="1"
pyinstaller **--**noconfirm Buzz**.**spec

```

**# Para compilação sem console (produção)**

```
$env:PYINSTALLER_DEBUG=""
pyinstaller **--noconfirm Buzz.**spec
```

### Método recomendado pelo autor do Buzz (não funciona):

Execute o comando:

```
make dist/Buzz
```

# Criação de um instalador para a versão de distribuição:

Execute o comando:

```
iscc installer.iss
```

## **Instalação do MSYS2**

Etapa 1: Baixar o MSYS2 em https://github.com/msys2/msys2-installer/releases/download/2025-02-21/msys2-x86_64-20250221.exe

Etapa 2: Atualize o sistema e instale os pacotes base

Depois que o MSYS2 estiver instalado, abra o terminal MSYS2 MinGW e atualize o banco de dados de pacotes junto com os pacotes base usando os seguintes comandos, um de cada vez:

```
pacman -Syu
```

```
pacman -Su

```

Dica: Ctrl+V ou Ctrl+Shift+V podem não funcionar na janela do shell do MSYS2. Use o clique direito para colar qualquer coisa. Além disso, apenas pressione Enter sempre que houver um prompt no terminal. Ele assumirá "Y" ou "Sim" como padrão. Você também pode digitar "Y" e depois pressionar Enter. Ambos funcionam.

### Etapa 3: Instale o GCC para C e C++

Agora, abra novamente o shell do MSYS2. Para instalar o GCC para as arquiteturas 32-bit e 64-bit, use os seguintes comandos:

Para 64-bit:

```
pacman -S mingw-w64-x86_64-gcc
```

### Etapa 4: Instale o GDB para C e C++ (Opcional)

Para instalar o GDB para depuração, use os seguintes comandos:

Para 64-bit:

```
pacman -S mingw-w64-x86_64-gdb
```

### Etapa 5: Verifique as Instalações no MSYS2

Após instalar o GCC e o GDB, verifique as versões para garantir que as instalações foram bem-sucedidas no MSYS2:

```
gcc --version
```

```
g++ --version

```

```
gdb --version
```

### Etapa 6: Configure a Variável de Ambiente PATH

Para tornar as ferramentas instaladas acessíveis globalmente a partir do terminal, adicione o diretório binário do MSYS2 à variável de ambiente PATH do sistema. Para isso:

*6.1. Localize os Binários do MSYS2 MINGW64*
Encontre e copie o caminho da pasta bin dentro de mingw64. Ele deve estar no local onde o MSYS2 foi instalado, geralmente no drive C.

Exemplo de caminho:

```
C:\msys64\mingw64\bin
```

*6.2. Abra o Painel de Edição de Variáveis de Ambiente*
Abra o menu Iniciar e pesquise por "Editar variáveis de ambiente da conta". Abra essa opção.

*6.3. Clique no Botão de Variáveis de Ambiente*
Clique no botão "Variáveis de Ambiente".

*6.4. Edite a Variável PATH*
Na aba "Variáveis do sistema", selecione "Path" e clique no botão "Editar".

*6.5. Adicione o Caminho Copiado*
Clique em "Novo" e cole o caminho copiado (C:\msys64\mingw64\bin).
Clique em "OK" em todas as janelas abertas.

*6.6. Verifique a Instalação no Windows*
Abra o PowerShell ou o Terminal do Windows e execute os seguintes comandos:

```
gcc --version
```

```
g++ --version

```

```
gdb --version
```

Se tudo estiver correto, você verá a versão de cada ferramenta exibida.

Tudo pronto! Agora você pode usar o GCC e o GDB no seu Windows.
