# Configuração usando DLLs pré-compiladas (v1.6.2 compatível)

Write-Host "=== Usando DLLs Pré-compiladas do Whisper.cpp v1.6.2 ===" -ForegroundColor Green

# 1. Copiar DLLs do backup
Write-Host "Copiando DLLs pré-compiladas..." -ForegroundColor Yellow
if (Test-Path "dll_backup") {
    Copy-Item -Recurse -Force "dll_backup\*" "buzz\"
    
    # Verificar se copiou
    if (Test-Path "buzz\whisper.dll") {
        Write-Host "✓ whisper.dll copiada" -ForegroundColor Green
    }
    if (Test-Path "buzz\SDL2.dll") {
        Write-Host "✓ SDL2.dll copiada" -ForegroundColor Green
    }
}
else {
    Write-Host "✗ Pasta dll_backup não encontrada!" -ForegroundColor Red
    exit 1
}

# 2. Criar whisper_cpp.py compatível com v1.6.2
Write-Host "Criando whisper_cpp.py compatível..." -ForegroundColor Yellow

$whisperCppContent = @"
# whisper_cpp.py - Gerado para compatibilidade com whisper.dll v1.6.2
# Baseado em https://github.com/ggerganov/whisper.cpp/commit/c7b6988678779901d02ceba1a8212d2c9908956e

import ctypes
import os
import sys
from ctypes import c_char_p, c_int, c_float, c_void_p, POINTER, c_bool, c_uint32, Structure

# Localizar whisper.dll
def find_whisper_dll():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dll_path = os.path.join(current_dir, "whisper.dll")
    
    if os.path.exists(dll_path):
        return dll_path
    
    # Procurar em outros locais
    possible_paths = [
        "./whisper.dll",
        "../whisper.dll",
        "whisper.dll"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

# Carregar biblioteca whisper
dll_path = find_whisper_dll()
if dll_path:
    try:
        libwhisper = ctypes.CDLL(dll_path)
        print(f"✓ whisper.dll carregada de: {dll_path}")
    except Exception as e:
        print(f"✗ Erro ao carregar whisper.dll: {e}")
        libwhisper = None
else:
    print("✗ whisper.dll não encontrada")
    libwhisper = None

# Estruturas básicas (compatíveis com v1.6.2)
class WhisperContext(Structure):
    pass

# Definições de tipos
whisper_context_p = POINTER(WhisperContext)

# Configurar funções principais se biblioteca carregada
if libwhisper:
    try:
        # whisper_init_from_file
        if hasattr(libwhisper, 'whisper_init_from_file'):
            libwhisper.whisper_init_from_file.argtypes = [c_char_p]
            libwhisper.whisper_init_from_file.restype = whisper_context_p
        
        # whisper_free
        if hasattr(libwhisper, 'whisper_free'):
            libwhisper.whisper_free.argtypes = [whisper_context_p]
            libwhisper.whisper_free.restype = None
            
        # whisper_full
        if hasattr(libwhisper, 'whisper_full'):
            libwhisper.whisper_full.argtypes = [whisper_context_p, c_void_p, POINTER(c_float), c_int]
            libwhisper.whisper_full.restype = c_int
        
        print("✓ Funções do whisper configuradas")
        WHISPER_AVAILABLE = True
        
    except Exception as e:
        print(f"⚠ Biblioteca carregada mas configuração falhou: {e}")
        WHISPER_AVAILABLE = False
else:
    WHISPER_AVAILABLE = False

# Constantes
WHISPER_SAMPLE_RATE = 16000

# Funções dummy para compatibilidade
def whisper_init_from_file(fname):
    if libwhisper and hasattr(libwhisper, 'whisper_init_from_file'):
        return libwhisper.whisper_init_from_file(fname.encode('utf-8'))
    return None

def whisper_free(ctx):
    if libwhisper and hasattr(libwhisper, 'whisper_free') and ctx:
        libwhisper.whisper_free(ctx)

# Exportações
__all__ = ['libwhisper', 'WHISPER_AVAILABLE', 'whisper_init_from_file', 'whisper_free', 'WHISPER_SAMPLE_RATE']
"@

# Salvar arquivo
$whisperCppContent | Out-File -FilePath "buzz\whisper_cpp.py" -Encoding UTF8

Write-Host "✓ whisper_cpp.py criado" -ForegroundColor Green

# 3. Compilar traduções
Write-Host "Compilando traduções..." -ForegroundColor Yellow
if (Test-Path "msgfmt.py") {
    try {
        python msgfmt.py -o buzz/locale/pt_BR/LC_MESSAGES/buzz.mo buzz/locale/pt_BR/LC_MESSAGES/buzz.po
        Write-Host "✓ Traduções compiladas" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠ Erro ao compilar traduções (opcional)" -ForegroundColor Yellow
    }
}

# 4. Verificar arquivos essenciais
Write-Host "`nVerificando arquivos essenciais..." -ForegroundColor Yellow
$essentialFiles = @(
    "buzz\whisper.dll",
    "buzz\SDL2.dll", 
    "buzz\whisper_cpp.py",
    "main.py"
)

foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "✗ $file FALTANDO" -ForegroundColor Red
    }
}

Write-Host "`n=== Configuração concluída! ===" -ForegroundColor Green
Write-Host "Agora execute: python -m buzz" -ForegroundColor Cyan
Write-Host "Se der erro, use: `$env:BUZZ_FORCE_CPU = 'true'; python -m buzz" -ForegroundColor Cyan