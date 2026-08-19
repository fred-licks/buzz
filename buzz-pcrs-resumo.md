# Buzz PCRS — Resumo do Projeto

> Documento de contexto e handoff. Preparado para servir de base a um módulo do
> **Ancrim Tools**.
> Data: 18/08/2026 · Autor do projeto: Fred Licks (Dinova/DTIP — PCRS)
> Revisão 4 — incorpora os três adendos da sessão de 18/08/2026 (instalador e
> branding, ambiente de build e modo debug, cadeia ffmpeg/ffprobe) e fixa
> `D:\Github\fredlicks\buzz` como cópia canônica, com verificação direta do
> código-fonte que resolveu três lacunas da §9.

---

## 1. O que é

O **Buzz PCRS** é uma customização institucional do **Buzz**, um aplicativo
desktop de **transcrição e tradução de áudio/vídeo que roda 100% offline**, na
própria máquina do usuário, usando os modelos **Whisper** da OpenAI.

O ponto que justifica o projeto na Polícia Civil é exatamente esse: **o áudio
nunca sai do computador**. Material de investigação (interceptações,
depoimentos, áudios de WhatsApp apreendidos) pode ser transcrito sem enviar
nada para serviço em nuvem.

### Funcionalidades principais

| Função | Descrição |
|---|---|
| Transcrição de arquivo | Importa áudio/vídeo e gera transcrição com marcação de tempo |
| Transcrição ao vivo | Captura microfone / áudio do sistema e transcreve em tempo real |
| Tradução | Traduz a transcrição para outro idioma |
| Importação por URL | Baixa mídia via `yt-dlp` e transcreve |
| Exportação | TXT, SRT, VTT |
| Histórico | Banco SQLite local com transcrições e segmentos |
| Edição | Visualizador/editor de transcrição com player de áudio sincronizado |

### Motores de transcrição suportados

O Buzz não tem um motor só — ele abstrai vários por trás da mesma interface:

1. **Whisper (OpenAI, PyTorch)** — implementação de referência, usa GPU CUDA.
2. **Faster-Whisper (CTranslate2)** — mais rápido e mais leve em memória.
3. **Whisper.cpp** — biblioteca C++ compilada (`whisper.dll` no Windows),
   acessada via bindings `ctypes` gerados com `ctypesgen`. Roda bem em CPU.
4. **Transformers (Hugging Face)** — permite usar modelos Whisper de terceiros
   (ex.: modelos afinados para português).
5. **API da OpenAI** — *online*; existe no upstream, mas é justamente o modo
   que não interessa ao uso institucional.

---

## 2. De onde veio

```
chidiwilliams/buzz  (upstream, licença MIT)
        │
        └── fred-licks/buzz  (fork institucional → "Buzz PCRS")
                    │
                    └── whisper.cpp  (submódulo git, ggerganov/whisper.cpp)
```

- **Upstream:** <https://github.com/chidiwilliams/buzz> — projeto open source,
  licença MIT, autor Chidi Williams. Versão base do fork: **1.3.0**.
- **Fork de trabalho:** <https://github.com/fred-licks/buzz>, com o `upstream`
  configurado como segundo remote (permite puxar atualizações do projeto
  original).
- **Submódulo:** `whisper.cpp` do ggerganov. As DLLs pré-compiladas em
  `dll_backup/` foram extraídas do release **v1.6.2** — e o commit do submódulo
  precisa bater com o commit de onde as DLLs saíram, senão a ABI não confere.
<!-- #deletado - **Repositório local:** `E:\GitHub\third-party\buzz` (registro de adendo anterior) -->
- **Repositório local (canônico):** `D:\Github\fredlicks\buzz` — **definido pelo
  Fred em 18/08/2026 como a única cópia que conta.** Clone de `fred-licks/buzz`,
  gerenciado pelo GitHub Desktop.
- `E:\GitHub\third-party\buzz` — cópia antiga, **descartada**. Não usar como
  referência nem como origem de build.

> ⚠ **Consequência importante e não óbvia: os builds que apresentaram o crash
> saíram da cópia descartada.** Comparação dos dois diretórios:
>
> | | `D:\Github\fredlicks\buzz` **(canônico)** | `E:\GitHub\third-party\buzz` (descartado) |
> |---|---|---|
> | `installer.iss` | versão **PCRS atual** (5.809 bytes: publisher institucional, `HKCU\Software\PCRS\Buzz`, pasta de logs, detecção de instalação anterior) | versão **antiga** (publisher `Dinova/DTIP/PCRS`, saída `Buzz-1.0.0-windows`, sem chaves PCRS) |
> | Arquivo LEIAME | `README_PCRS.txt` (0 bytes) — **bate** com o `installer.iss` | `_leiame_buzz_pcrs.txt` — não bate |
> | `dist\` | **não existe** | `dist\Buzz\` residual (build antigo) |
> | Builds do PyInstaller | nenhum ainda | é aqui que rodaram |
>
> Ou seja: **nenhum build jamais foi gerado a partir da cópia canônica.** Toda a
> observação do crash descrita na §6.1 vem de binários produzidos na cópia
> descartada, com um `installer.iss` diferente do atual. Antes de investigar
> qualquer hipótese, o passo obrigatório é **recompilar do zero a partir de
> `D:\` e verificar se o sintoma ainda existe.**
>
> Nota: o `installer.iss` guardado no conhecimento deste projeto também é a
> versão **antiga** — não usá-lo como referência.

A licença MIT permite o fork, a customização e a redistribuição interna sem
maiores formalidades — basta manter o aviso de copyright original.

---

## 3. Arquitetura (mapa do código)

```
main.py                     → chama buzz.buzz.main()
buzz/
├── buzz.py                 → bootstrap: multiprocessing, PATH, DLLs, logging
├── cli.py                  → interface de linha de comando
├── model_loader.py         → download/cache/carregamento dos modelos Whisper
├── transformers_whisper.py → adaptador para modelos Hugging Face
├── translator.py           → tradução
├── whisper_audio.py        → leitura/decodificação de áudio (via ffmpeg)
├── transcriber/            → CAMADA DE TRANSCRIÇÃO (o núcleo reaproveitável)
│   ├── transcriber.py                        (classes-base: Segment, TranscriptionOptions)
│   ├── file_transcriber.py                   (base para transcrição de arquivo)
│   ├── whisper_file_transcriber.py           (Whisper/faster-whisper)
│   ├── whisper_cpp_file_transcriber.py       (whisper.cpp via ctypes)
│   ├── openai_whisper_api_file_transcriber.py(API OpenAI — online)
│   └── recording_transcriber.py              (tempo real)
├── file_transcriber_queue_worker.py → fila de tarefas de transcrição
├── db/                     → CAMADA DE DADOS (SQLite)
│   ├── db.py, migrator.py, schema.sql
│   ├── entity/  (Transcription, TranscriptionSegment)
│   ├── dao/     (acesso a dados)
│   └── service/ (regra de negócio)
├── widgets/                → CAMADA DE INTERFACE (PyQt6)
├── locale/                 → traduções (.po → .mo)
└── dll_backup/, SDL2.dll, whisper.dll → binários nativos
```

**Separação relevante para o Ancrim Tools:** o `transcriber/` + `model_loader.py`
+ `whisper_audio.py` formam um núcleo praticamente independente da interface
gráfica. A camada `widgets/` (PyQt6) e a camada `db/` (SQLite próprio do Buzz)
são descartáveis/substituíveis num porte.

### Stack

- Python ≥3.9 <3.13 · PyQt6 6.8.1 · Poetry (gerenciamento de dependências)
- torch 2.6.0+cu124 / torchaudio 2.6.0+cu124 (CUDA 12.4) · ctranslate2 4.3.1
- transformers **fixado em 4.49.0** (a 4.50.0 tem bug conhecido)
- ffmpeg/ffprobe empacotados junto com o executável — resolvidos por
  `shutil.which()` **no momento do build**, ou seja: são dependência da máquina
  que compila, não do usuário final (ver §8, item 6)
- PyInstaller (empacotamento) + Inno Setup (instalador Windows)

---

## 4. O que já foi feito no fork PCRS

Customizações efetivamente presentes no repositório:

**Identidade visual e institucional**

- `assets/buzz_pcrs.ico`, `buzz_pcrs.icns`, `brasao_pcrs.ico`
  (o ícone original preservado como `buzz_orig.ico`)
- Imagens do assistente de instalação: `wizard-image.bmp`, `wizard-small-image.bmp`
- Bundle identifier trocado para `br.gov.rs.pc.inova_dtip.buzzpcrs`
- Nome da pasta de distribuição: `Buzz PCRS`
- **AppId próprio:** `{C9C45D2A-029B-4E91-818E-03431D508869}`, substituindo o
  GUID herdado do upstream. Sem isso, o Windows trata Buzz PCRS e Buzz original
  como o mesmo produto (instalar um desinstala/sobrescreve o outro).
- **Paleta institucional da PCRS: preto e branco.** O brasão tem fundo vermelho,
  mas isso é do brasão, não da identidade da instituição. As imagens do
  assistente de instalação (`wizard-image.bmp` 164×314,
  `wizard-small-image.bmp` 55×55) usam fundo preto com texto branco.
- Nomenclatura consolidada: publisher **"Polícia Civil do Estado do Rio Grande
  do Sul – PCRS"**; descrição **"Sistema de Transcrição de Áudio"** — sem menção
  a tradução, ainda que o motor a suporte.

> ⚠ **Duas pastas `assets/` no repositório**, com papéis distintos — confundi-las
> faz o arquivo ser gerado no lugar errado e o `iscc` não encontrá-lo:
>
> - `assets/` (raiz) → recursos de **build/instalador**: `.ico`, `.icns`,
>   `wizard-*.bmp`. É daqui que o `installer.iss` lê.
> - `buzz/assets/` → recursos de **runtime**, empacotados pelo `Buzz.spec`
>   (`datas += [("buzz/assets/*", "assets")]`). O logo-fonte
>   `buzz-icon-1024_pcrs.png` está aqui.

**Instalador (`installer.iss`, Inno Setup) — reescrito**

- Publisher: "Polícia Civil do Estado do Rio Grande do Sul – PCRS"; URL institucional
- Instala em `%ProgramFiles%\PCRS\Buzz PCRS`; grupo do menu Iniciar "PCRS"
- Saída: `Buzz-PCRS-1.0.0-windows-x64.exe`
- Interface do instalador **somente em português do Brasil** (inglês comentado)
- Chave de registro própria: `HKCU\Software\PCRS\Buzz`, gravando
  `ui-locale=pt_BR`, `instituicao=PCRS`, `versao_instalacao` e `data_instalacao`
- Detecta instalação anterior e pergunta antes de atualizar
- Limpa `Buzz.exe` e `_internal` da instalação anterior antes de copiar
- Cria `%LocalAppData%\PCRS\Buzz\Logs`
- Prevê `LEIAME.txt` e `manual_usuario_pcrs.pdf` (opcional) no menu Iniciar
- Pergunta, na desinstalação, se o usuário quer apagar as configurações

**Empacotamento (`Buzz.spec`, PyInstaller)**

- Ícones PCRS; nome do COLLECT `Buzz PCRS`
- Inclusão explícita da pasta `dll_backup/` (com `SDL2.dll` e `whisper.dll`)
  tanto como *data* quanto como *binary*
- `ffmpeg` e `ffprobe` resolvidos por `shutil.which()` e embutidos
- Modo debug controlado por variável de ambiente `PYINSTALLER_DEBUG=1`
  (liga console e verbosidade do bootloader)

**Alterações no código do app** *(verificadas na cópia canônica)*

- `buzz/settings/settings.py`: acrescentado `APP_DISPLAY_NAME = "Buzz PCRS"`
  (o `APP_NAME` permanece `"Buzz"` — ver §6.4b).
- `buzz/locale.py`: idioma padrão da interface alterado para **`pt_BR`**
  (`settings.value(settings.Key.UI_LOCALE, "pt_BR")`). É isso que efetivamente
  faz a interface abrir em português — não a chave de registro do instalador.
- `buzz/assets/`: `buzz_pcrs.ico` e `buzz-icon-1024_pcrs.png` adicionados; ícone
  original preservado como `buzz_original.ico`.

**Documentação**

- `tutorial_compile_buzzpcrs.md` — tutorial próprio, em português, do ambiente
  de compilação no Windows (Chocolatey, make, ffmpeg, MSYS2/GCC, Poetry,
  clone recursivo, `make translation_mo`, cópia das DLLs, PyInstaller, Inno Setup)
- `README_PCRS.txt` — criado, ainda **vazio** (0 bytes)
- `CLAUDE.md` — guia de arquitetura e comandos do repositório

---

## 5. Cadeia de build (como se produz o instalador)

```
[1] Ambiente             conda activate buzz  /  poetry shell
[2] Bindings nativos     make buzz/whisper_cpp.py      (CMake + ctypesgen sobre whisper.cpp)
[3] Traduções            make translation_mo           (.po → .mo)
[4] DLLs                 copiar dll_backup\* → buzz\   (SDL2.dll, whisper.dll)
[5] Dependências         poetry install
<!-- #deletado [6] Executável   pyinstaller --noconfirm --console Buzz.spec  → dist\Buzz PCRS\ -->
[6] Executável           $env:PYINSTALLER_DEBUG="1"  (opcional, liga console)
                         pyinstaller --noconfirm Buzz.spec              → dist\Buzz PCRS\
[7] Instalador           iscc installer.iss                            → dist\Buzz-PCRS-1.0.0-windows-x64.exe
```

Observação registrada no tutorial: **o passo [6] só funciona com o comando
direto do PyInstaller**. O alvo `make dist/Buzz`, recomendado pelo autor do
projeto original, **não funciona** neste ambiente.

### 5.1 Como o modo debug é realmente ligado

`--console` **não é aceito** na linha de comando junto com um arquivo `.spec`.
Verificado em 18/08/2026 com PyInstaller 6.13.0:

```
ERROR: option(s) not allowed:
  --console/--nowindowed/--windowed/--noconsole
makespec options not valid when a .spec file is given
```

Essas flags pertencem ao `makespec`; quando existe um `.spec`, é ele quem manda.
O `Buzz.spec` já define `console=DEBUG` e `debug=DEBUG`, onde
`DEBUG = os.environ.get("PYINSTALLER_DEBUG", "")`. O console é ligado pela
variável de ambiente, **nunca** pela linha de comando:

```powershell
# PowerShell, em D:\Github\fredlicks\buzz, com o ambiente (buzz) ativo
$env:PYINSTALLER_DEBUG="1"      # liga console + bootloader verboso
pyinstaller --noconfirm Buzz.spec
```

Distinção que já causou confusão e vale fixar:

| Variável | Momento | Lida por | Efeito |
|---|---|---|---|
| `PYINSTALLER_DEBUG` | **build** | `Buzz.spec` | gera EXE com `console=True` e `debug=True` |
| `BUZZ_FORCE_CPU` | **runtime** | o app em execução | força inferência em CPU |

Definir `BUZZ_FORCE_CPU` antes do `pyinstaller` **não produz efeito algum** sobre
o executável gerado — ela precisa estar no ambiente de quem *executa* o app.

> 📌 **Pendência:** o `tutorial_compile_buzzpcrs.md` registra o comando errado
> (`pyinstaller --noconfirm --console Buzz.spec`) na seção "Método adotado pelo
> Fred Licks (funciona)". Precisa ser corrigido lá também.

### 5.2 Ambiente de build confirmado

Dados extraídos do cabeçalho de uma execução real do PyInstaller:

| Item | Valor |
|---|---|
| Repositório | `E:\GitHub\third-party\buzz` ⚠ **cópia descartada — reconfirmar em `D:\`** |
| Interpretador | Python 3.11.13 |
| Ambiente | **conda**, em `C:\Users\fredlicks\.conda\envs\buzz` |
| PyInstaller | 6.13.0 (contrib hooks 2025.3) |
| Sistema | Windows 11, build 10.0.26100 |

O build **não roda dentro da virtualenv do Poetry** — roda num ambiente conda
chamado `buzz`. Ver §6.5.

O ambiente conda em si provavelmente continua válido; o que precisa ser refeito
é o **local do build**, que passa a ser `D:\Github\fredlicks\buzz` (§2).

```powershell
# PowerShell, com (buzz) ativo, em D:\Github\fredlicks\buzz
$env:PYINSTALLER_DEBUG="1"
pyinstaller --noconfirm Buzz.spec
```

---

## 6. Dificuldades enfrentadas

### 6.1 O problema central, ainda em aberto

> **O Buzz funciona no ambiente de desenvolvimento, mas a versão compilada e
> instalada fecha inesperadamente ao adicionar um arquivo de mídia para
> transcrição.** (Windows 11)

> 🛑 **Ler antes de investigar qualquer hipótese abaixo.** Os binários em que o
> crash foi observado saíram de `E:\GitHub\third-party\buzz`, cópia agora
> descartada (§2), com um `installer.iss` diferente do atual. A cópia canônica
> `D:\Github\fredlicks\buzz` **nunca produziu um build**. O primeiro passo não é
> diagnosticar — é **recompilar do zero a partir de `D:\` e verificar se o
> sintoma ainda se reproduz.** É inteiramente possível que parte das hipóteses
> abaixo já não se aplique.

Ou seja: o empacotamento não é fiel ao ambiente de desenvolvimento. O aplicativo
abre, a interface carrega — e o crash acontece exatamente no momento em que a
transcrição de arquivo é disparada. Esse é o ponto do fluxo em que três coisas
acontecem ao mesmo tempo, e qualquer uma delas explicaria o fechamento silencioso:

1. **Multiprocessing** — o Buzz dispara a transcrição em processo separado.
   Sob PyInstaller no Windows (que usa `spawn`, não `fork`), o processo filho
   reexecuta o executável; se `multiprocessing.freeze_support()` não cobrir o
   caminho, o app pode reabrir ou morrer. O `buzz.py` chama `freeze_support()`,
   mas isso não garante que os *workers* herdem corretamente o ambiente congelado.
2. **Carga de bibliotecas nativas** — `whisper.dll`, `SDL2.dll`, DLLs do CUDA e
   `ffmpeg/ffprobe`. O `buzz.py` faz `os.add_dll_directory()` para o diretório
   do app e para `dll_backup`, mas os caminhos mudam entre `_internal\` (build)
   e o layout instalado. DLL que não carrega em processo filho = fechamento sem
   mensagem, porque é falha no nível do SO, não exceção Python.
3. **Download/carregamento do modelo Whisper** — na primeira transcrição o
   modelo é baixado ou lido do cache (`model_loader.py`). Diretórios de cache
   e permissões diferem quando o app está instalado em `Program Files`.
4. **Resolução do caminho de ffmpeg/ffprobe** — adicionar um arquivo de mídia é
   exatamente o momento em que `whisper_audio.py` chama o ffmpeg para decodificar
   o áudio. Os binários *estão* dentro do pacote (o `Buzz.spec` os embute), mas
   estar embutido e ser encontrado em runtime são coisas diferentes: em modo
   congelado o binário não está no PATH, está no diretório do bundle. Se a busca
   cair no PATH do sistema e a máquina do usuário não tiver ffmpeg instalado, a
   chamada falha. Vale confirmar antes de descartar — a coincidência entre o
   ponto do crash e o ponto em que o ffmpeg é chamado é forte demais para ser
   ignorada.

   **Confirmado na leitura do código** (`buzz/whisper_audio.py`, função
   `load_audio`): o ffmpeg é invocado por **nome puro**, via
   `subprocess.run(["ffmpeg", "-nostdin", ...])`, e o próprio comentário no
   código diz *"Requires the ffmpeg CLI in PATH"*. Não há resolução por caminho
   absoluto. A única coisa que faz isso funcionar em modo congelado é a linha
   `os.environ["PATH"] += os.pathsep + APP_BASE_DIR` em `buzz/buzz.py`, onde
   `APP_BASE_DIR` vale `sys._MEIPASS` quando congelado — ou seja, o
   `_internal\`. **A cadeia inteira depende dessa única linha.**

   Detalhe adicional que torna a função frágil: ela levanta `RuntimeError`
   sempre que o ffmpeg escreve **qualquer coisa** em `stderr`
   (`if len(result.stderr): raise ...`), mesmo com `-loglevel panic`.

   > **Discriminador útil:** tanto "ffmpeg não encontrado"
   > (`FileNotFoundError`) quanto "ffmpeg reclamou" (`RuntimeError`) são
   > **exceções Python** — deveriam aparecer no `logs.txt`. Se o processo morre
   > sem deixar nada no log, a hipótese 4 perde força e o peso volta para (1) e
   > (2), que falham no nível do SO.

> **Antes de investigar as três hipóteses acima, ver §6.4(a) e §6.5.** Há duas
> explicações mais prosaicas na frente delas: o instalador pode estar
> empacotando um build antigo residual em `dist\Buzz\`, e o ambiente que compila
> pode não ser o ambiente que foi testado. Em ambos os casos o crash não teria
> relação nenhuma com "empacotamento infiel".

**Por que o fechamento é silencioso — e por que isso não é característica do
bug.** No build de produção (`PYINSTALLER_DEBUG` vazio) o `Buzz.spec` gera o
executável com `console=False`. Um crash nativo — DLL que não carrega, processo
filho que morre — simplesmente **não tem para onde escrever**. O "fecha sem
mensagem" descrito acima é, em boa parte, artefato dessa configuração. Qualquer
tentativa séria de diagnóstico precisa passar por um build com
`PYINSTALLER_DEBUG=1` **instalado** (não apenas executado da `dist\`).

**Diagnóstico ainda não fechado.** O caminho para fechá-lo é o que já está
previsto no `Buzz.spec`: compilar com `PYINSTALLER_DEBUG=1` (console visível +
bootloader verboso) e ler `logs.txt` em
`%LocalAppData%\Buzz\Buzz\Logs` *(a conferir — ver nota)*. Um crash que
aparece no console mas não no log aponta para (1) ou (2); um traceback no log
aponta para (3).

> **Nota sobre o caminho do log.** O `CONTRIBUTING.md` do upstream instrui a
> colar `%USERPROFILE%\AppData\Local\Buzz\Buzz\Logs` no Explorer — com o nome
> **duplicado**, que é o layout que o `platformdirs` produz quando `appname` e
> `appauthor` coincidem. Se o caminho procurado estiver errado, a conclusão
> "não há log" é **falso negativo**. Conferir na máquina antes de fixar no
> documento.

### 6.2 Dificuldades já superadas (e o custo delas)

| Dificuldade | Como foi contornada |
|---|---|
| Toolchain de compilação C++ no Windows | Instalação de MSYS2 + GCC/GDB, Chocolatey, GNU make — cadeia longa e frágil, documentada passo a passo no tutorial |
| `make dist/Buzz` (método oficial) não funciona | Substituído por chamada direta `pyinstaller --noconfirm --console Buzz.spec` |
| DLLs nativas não chegavam ao pacote | Passo manual de cópia de `dll_backup\*` para `buzz\` antes de compilar, + inclusão explícita no `Buzz.spec` |
| Ambiente Poetry quebrando | Receita de reset completo: `poetry env remove`, `poetry cache clear . --all`, apagar `poetry.lock`, `poetry install` |
| Torch/CUDA com versão errada | Reinstalação manual de `torch==2.6.0+cu124`, `torchaudio==2.6.0+cu124` e do conjunto de pacotes `nvidia-*-cu12` a partir do índice do PyTorch |
| Falhas relacionadas à GPU | Variável de ambiente `BUZZ_FORCE_CPU=true` como escape |
| Erros de FFmpeg **na inicialização** | São ruído — o Buzz tenta carregar o ffmpeg por vários caminhos e alguns falham por desenho. ⚠ Isso vale para a inicialização; **não** serve de argumento para descartar o ffmpeg no momento da transcrição (§6.1, hipótese 4) |
| Ruído de "syntax errors" durante o build | Idem — inofensivos, segundo o próprio upstream |

### 6.3 Dificuldade estrutural

O Buzz é um **aplicativo desktop monolítico**, não uma biblioteca. Ele acopla
GUI (PyQt6), banco próprio (SQLite com migrations), fila de trabalho, download
de modelos e três motores de inferência. Empacotar isso com PyInstaller
significa arrastar PyTorch + CUDA + Qt + ffmpeg + DLLs nativas — pacote da ordem
de gigabytes, com uma superfície enorme de coisas que podem quebrar entre "roda
aqui" e "roda instalado". **Boa parte da dor deste projeto vem dessa escolha
arquitetural, não de um bug específico.**

### 6.4 Inconsistências entre `Buzz.spec`, `installer.iss` e o código

*(Sessão de 18/08/2026 — revisão do instalador.)* Divergências identificadas na
leitura dos arquivos. **Nenhuma foi confirmada em execução ainda**, mas as duas
primeiras são candidatas diretas a explicar o comportamento "funciona compilado,
quebra instalado".

#### (a) O instalador pode estar empacotando uma pasta obsoleta — **prioridade alta**

| Arquivo | Valor |
|---|---|
| `Buzz.spec` → `COLLECT(name=...)` | `Buzz PCRS` → gera `dist\Buzz PCRS\` |
| `installer.iss` → `AppSourcePath` | `dist\Buzz\*` |

O PyInstaller passou a gravar em `dist\Buzz PCRS\`, mas o `installer.iss`
continua lendo `dist\Buzz\`. Como `dist\Buzz\` **existe** no repositório (sobra
de builds anteriores — a listagem recursiva mostrou
`dist\Buzz\_internal\assets\buzz-icon-1024_pcrs.png`), o `iscc` compila sem erro
e produz um instalador aparentemente correto, só que **com o build antigo
dentro**.

Isso muda a leitura do problema central da §6.1: **pode não haver bug de
empacotamento nenhum** — pode ser simplesmente que a versão testada instalada
nunca foi a versão recém-compilada.

A divergência foi **verificada também na cópia canônica `D:\`** — não é um
descuido local da cópia descartada. Continua valendo como defeito a corrigir.

> **Mas o efeito é diferente em cada cópia.** Em `E:\` existia um `dist\Buzz\`
> residual, então o `iscc` compilava em silêncio empacotando o build velho — o
> cenário que explicaria o crash. Em `D:\` **não há `dist\` nenhum**, então o
> `iscc` simplesmente vai falhar na primeira tentativa. Como `E:\` foi
> descartada, esta hipótese **deixa de ser candidata a explicar o crash** e
> passa a ser apenas um bug de configuração que trava o próximo build.
- *Correção:* alinhar os dois nomes (ou o `COLLECT` volta a `Buzz`, ou o
  `AppSourcePath` passa a `dist\Buzz PCRS\*`). Preferir nome **sem espaço** —
  espaço em caminho é fonte recorrente de problema em script de build e em
  resolução de DLL.

#### (b) A chave de registro do instalador não é a chave que o app lê — **CONFIRMADO**

Verificado em `buzz/settings/settings.py` na cópia canônica:

```python
APP_NAME = "Buzz"
APP_DISPLAY_NAME = "Buzz PCRS"

class Settings:
    def __init__(self, application=""):
        self.settings = QSettings(APP_NAME, application)
```

`QSettings("Buzz", "")` no Windows resolve para **`HKCU\Software\Buzz`**. O
`installer.iss` grava em **`HKCU\Software\PCRS\Buzz`**. São chaves diferentes:
tudo o que o instalador escreve — `ui-locale`, `instituicao`,
`versao_instalacao`, `data_instalacao` — **é ignorado pelo app**.

*Impacto real: baixo.* O fork já alterou o padrão no código
(`buzz/locale.py`: `settings.value(settings.Key.UI_LOCALE, "pt_BR")`), então a
interface abre em português de qualquer jeito. As chaves do instalador são
**inertes, não nocivas**.

*Decisão a tomar:* ou alinhar o `installer.iss` a `HKCU\Software\Buzz`, ou
alterar `APP_NAME`/o construtor do `QSettings` para apontar à chave
institucional, ou assumir que as chaves são só um registro de inventário e
documentar isso. O que não convém é deixar a ambiguidade sem registro.

⚠ Se optar por mudar `APP_NAME`, atenção: ele também é usado como domínio do
`gettext` em `buzz/locale.py` (`APP_NAME.lower()` → `buzz.mo`) e como nome de
diretório pelo `platformdirs` (logs, cache, dados). Mudá-lo quebra tradução,
caminho de log e histórico de transcrições de instalações existentes.

#### (c) `[Files]` referencia arquivos inexistentes — **parcialmente resolvido**

```
Source: "README_PCRS.txt"; DestDir: "{app}"; Flags: ignoreversion; DestName: "LEIAME.txt"
```

O problema do **nome** era um artefato da cópia descartada: `E:\` tinha
`_leiame_buzz_pcrs.txt`, mas a cópia canônica `D:\` tem `README_PCRS.txt`, que
**bate** com o `installer.iss`. Sem problema aqui.

O que resta:

- `README_PCRS.txt` existe mas está **vazio (0 bytes)** — vai instalar um
  `LEIAME.txt` em branco.
- `manual_usuario_pcrs.pdf` **não existe**. A linha em `[Files]` tem
  `skipifsourcedoesntexist` e não quebra o build, mas o atalho
  `{group}\Manual do Usuário` em `[Icons]` é criado de qualquer forma e fica
  **apontando para o vazio**. Ou se escreve o manual, ou se remove o atalho.

#### (d) `SignTool=signtool` aborta o `iscc` — *já resolvido*

`Value of [Setup] section directive "SignTool" is invalid.` A diretiva exige um
sign tool previamente **registrado no IDE do Inno Setup**
(*Tools → Configure Sign Tools*); não basta ter `signtool.exe` no PATH. Enquanto
não houver certificado, a linha fica comentada.

### 6.5 O ambiente que empacota não é o ambiente declarado — **prioridade alta**

O `pyproject.toml`/`poetry.lock` descrevem um conjunto de versões; o build sai
de um ambiente **conda** (`C:\Users\fredlicks\.conda\envs\buzz`, Python 3.11.13).
A divergência já é visível no próprio PyInstaller: o `pyproject.toml` declara
`^6.12.0`, o conda tem **6.13.0**.

Numa investigação de "roda no dev, quebra no pacote", isso é suspeito de
primeira ordem — **o ambiente testado e o ambiente que empacota podem
simplesmente não ser o mesmo conjunto de versões.** Torch, ctranslate2 e
transformers são os que mais importam aqui: são exatamente os pacotes com
binários nativos e com versões fixadas por bug conhecido (`transformers 4.49.0`).

Eliminar essa divergência **antes** de qualquer outra hipótese. Ou o build passa
a rodar dentro do ambiente do Poetry, ou o ambiente conda vira a fonte declarada
e travada — mas não os dois.

---

## 7. Estado atual

| Item | Situação |
|---|---|
| Fork institucional criado | ✅ |
| Identidade visual PCRS | ✅ |
| Instalador Inno Setup em pt-BR | ✅ |
| Tutorial de compilação | ✅ |
| Build de desenvolvimento funcionando | ✅ |
| Build empacotado (PyInstaller) gerando executável | ✅ |
| **Versão instalada transcrevendo arquivo** | ❌ **fecha inesperadamente** |
| `README_PCRS.txt` | ⬜ existe, mas vazio (0 bytes) — §6.4c |
| `manual_usuario_pcrs.pdf` | ⬜ não existe (atalho do menu Iniciar fica quebrado) |
| Assinatura digital do executável | ⬜ não configurada (`SignTool` comentado — §6.4d) |
| Alinhamento `Buzz.spec` ↔ `installer.iss` | ❌ divergente (§6.4a) |
| Chave de registro do instalador ↔ `QSettings` | ❌ divergente, impacto baixo (§6.4b) |
| Cópia canônica do repositório | ✅ `D:\Github\fredlicks\buzz` (definido 18/08/2026) |
| Build a partir da cópia canônica | ⬜ **nunca foi feito** — próximo passo (§6.1) |
| Distribuição institucional | ⬜ bloqueada pelo item em vermelho |

---

## 8. Implicações para o módulo do Ancrim Tools

Se o objetivo é transformar isso num **módulo de transcrição** dentro do Ancrim
Tools, o aprendizado do Buzz PCRS aponta caminhos bem concretos:

**Reaproveitar**

- A lógica de `buzz/transcriber/` — a abstração "um transcritor, vários motores"
  é boa e testada.
- `whisper_audio.py` (decodificação via ffmpeg) e a estratégia de resolução de
  binários.
- O tratamento de idioma, segmentos com timestamp e exportação SRT/VTT.

**Descartar / substituir**

- Toda a camada `widgets/` (PyQt6) — a interface será do Ancrim Tools.
- O `db/` próprio do Buzz — usar a persistência do Ancrim Tools.
- O transcritor via API da OpenAI — inadequado para material sigiloso.
- Toda a cadeia `installer.iss` + imagens do wizard. Não há nada aqui
  reaproveitável num módulo — só o aprendizado registrado acima.

**Decidir cedo (foi aqui que o Buzz doeu)**

1. **Um motor só, ou vários?** Escolher `faster-whisper` como motor único
   elimina PyTorch, CUDA-toolkit em pacote e o submódulo whisper.cpp de uma vez
   — corta o problema de empacotamento pela raiz.
2. **Como o módulo é distribuído?** Se o Ancrim Tools já resolve empacotamento,
   herdar essa solução em vez de recriar a cadeia PyInstaller + Inno Setup.
3. **Onde vivem os modelos?** Definir um diretório de modelos fora de
   `Program Files` (ex.: `%LocalAppData%`), pré-populado na instalação, evita a
   classe inteira de erros de download/permissão em primeira execução.
4. **Processo separado ou thread?** Se a transcrição rodar em subprocesso,
   testar o comportamento congelado desde o primeiro dia — não no fim.
5. **Log desde o começo.** O crash do Buzz PCRS é difícil justamente porque é
   silencioso. Um log em arquivo, ativo por padrão, com o caminho visível ao
   usuário, teria economizado semanas.
6. **Binários externos (ffmpeg/ffprobe): dependência de build, não do usuário.**
   No Buzz o `Buzz.spec` resolve o caminho com `shutil.which("ffmpeg")` **no
   momento da compilação** e embute os executáveis no pacote — o usuário final
   não instala ffmpeg. Três consequências para o Ancrim Tools:

   - A **máquina de build** precisa ter ffmpeg no PATH. Se não tiver,
     `shutil.which()` devolve `None` e o build falha (ou, pior, gera pacote sem
     o binário).
   - O pacote fica **amarrado à versão de ffmpeg da máquina de quem compilou**.
     Convém versionar o ffmpeg junto do repositório — mesma estratégia já usada
     com as DLLs em `dll_backup/` — em vez de depender do que estiver instalado.
   - O **caminho em runtime muda** entre ambiente de desenvolvimento e
     executável congelado. O módulo precisa resolver isso explicitamente
     (diretório do bundle) em vez de confiar no PATH do sistema.

   Se o Ancrim Tools adotar `faster-whisper` como motor único (item 1 acima), o
   ffmpeg continua necessário para decodificar formatos de entrada — esta
   decisão **não desaparece** junto com o PyTorch.
7. **Uma única fonte de verdade para nome, versão e caminhos.** Os problemas
   (a), (b) e (c) da §6.4 são todos a mesma falha: o nome do produto está
   escrito à mão em três lugares (spec de empacotamento, script do instalador,
   código) e saiu de sincronia. No Ancrim Tools, derivar todos eles de um único
   arquivo de metadados do projeto.
8. **Limpar o diretório de saída antes de empacotar.** Build incremental sobre
   `dist/` residual produz artefato que compila, instala e engana — o pior tipo
   de falha, porque não gera erro. `rm -rf dist/` como primeiro passo
   obrigatório do pipeline.
9. **Branding não vale reconstrução de cadeia.** Uma sessão inteira foi gasta em
   imagem lateral do assistente e cor de fundo — resultado cosmético, custo
   alto. Se o Ancrim Tools já tem instalador, o módulo de transcrição deve
   herdá-lo e não trazer junto o par PyInstaller + Inno Setup.
10. **Um ambiente só, declarado.** Se o dev roda em conda e o build lê o mesmo
    conda, tudo bem — mas isso precisa estar escrito e travado. Ter
    `poetry.lock` descrevendo um ambiente e `conda` fornecendo outro (§6.5) é
    dívida garantida.

> Complemento ao item 5: **log em arquivo, ativo por padrão, independe de o
> executável ter console.** Foi exatamente a ausência dessa independência que
> tornou o crash do Buzz PCRS silencioso (§6.1).

---

## 9. Lacunas a confirmar

Pontos que não estão registrados nos arquivos do projeto e que valeria a pena
anotar antes de encerrar este documento:

- [ ] Já foi lido o `logs.txt` de uma execução instalada que travou? O que ele mostrou?
- [ ] O crash acontece com **qualquer** motor de transcrição, ou só com alguns?
- [ ] Acontece também com `BUZZ_FORCE_CPU=true`?
- [ ] Acontece rodando `dist\Buzz PCRS\Buzz.exe` direto (sem instalar), ou só
      depois de instalado em `Program Files`?
- [ ] O modelo Whisper chega a ser baixado antes do fechamento?
- [ ] Houve teste em máquina limpa (sem ambiente de desenvolvimento instalado)?
- [ ] **O `dist\` testado corresponde ao build atual, ou é resíduo?** (§6.4a —
      verificar antes de qualquer outra hipótese de crash)
- [ ] O app lê `HKCU\Software\PCRS\Buzz` ou `HKCU\Software\Buzz`? (§6.4b)
- [x] ~~Qual das duas cópias é a canônica?~~ → **`D:\Github\fredlicks\buzz`**
      (definido em 18/08/2026). `E:\` descartada.
- [x] ~~O app lê `HKCU\Software\PCRS\Buzz` ou `HKCU\Software\Buzz`?~~ →
      **`HKCU\Software\Buzz`**, confirmado em `settings.py` (§6.4b).
- [x] ~~O nome do arquivo LEIAME bate com o `installer.iss`?~~ → **sim** na cópia
      canônica; o desencontro era da cópia descartada (§6.4c).
- [ ] **Recompilar do zero a partir de `D:\` — o crash ainda se reproduz?**
      (pré-requisito de tudo, §6.1)
- [ ] O ambiente conda `buzz` e o `poetry.lock` declaram as mesmas versões de
      torch, ctranslate2 e transformers? (§6.5)
- [ ] Já houve algum build com `PYINSTALLER_DEBUG=1` **instalado** (não apenas
      executado da `dist\`)? É a única configuração em que o crash tem chance de
      deixar rastro visível.
- [ ] Onde `ffmpeg.exe` e `ffprobe.exe` aparecem na instalação? No PyInstaller
      6.x (o projeto fixa `pyinstaller = "^6.12.0"`) o destino `"."` de
      `binaries` cai em `_internal\`, não na raiz da pasta do app. Confirmar em
      `%ProgramFiles%\PCRS\Buzz PCRS\_internal\`.
- [ ] O crash acontece também em máquina que **tem** ffmpeg instalado no PATH?
      Se não acontecer, a hipótese 4 da §6.1 está confirmada.

### Como verificar a hipótese 4 (ffmpeg)

Contexto de execução: **Windows PowerShell**, sem privilégio de administrador,
em qualquer diretório.

```powershell
Get-ChildItem -Path "$env:ProgramFiles\PCRS\Buzz PCRS" -Recurse -Filter "ffmpeg.exe"
Get-ChildItem -Path "$env:ProgramFiles\PCRS\Buzz PCRS" -Recurse -Filter "ffprobe.exe"
```

- **Não retorna nada** → o binário não chegou ao pacote; provável que
  `shutil.which("ffmpeg")` tenha devolvido `None` na máquina de build.
- **Retorna em `_internal\`** → o binário está lá, e a questão passa a ser de
  resolução de caminho em runtime — o que deve aparecer no `logs.txt`.

Teste complementar: rodar o mesmo arquivo de mídia numa máquina limpa **com**
ffmpeg instalado via Chocolatey. Se funcionar ali e falhar na máquina sem
ffmpeg, a hipótese está fechada.

---

## 10. Referências

- Upstream: <https://github.com/chidiwilliams/buzz> (MIT)
- Fork PCRS: <https://github.com/fred-licks/buzz>
- Documentação Buzz: <https://chidiwilliams.github.io/buzz/>
- whisper.cpp: <https://github.com/ggerganov/whisper.cpp>
- Repositório local **canônico**: `D:\Github\fredlicks\buzz`
  (`E:\GitHub\third-party\buzz` descartada — ver §2)
