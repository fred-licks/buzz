# Setup completo para compilação no Windows

Write-Host "=== Configuração de Ambiente de Compilação Windows ===" -ForegroundColor Green

# 1. Verificar se já tem as ferramentas
Write-Host "Verificando ferramentas existentes..." -ForegroundColor Yellow

$hasGit = Get-Command git -ErrorAction SilentlyContinue
$hasGcc = Get-Command gcc -ErrorAction SilentlyContinue
$hasMake = Get-Command make -ErrorAction SilentlyContinue
$hasCmake = Get-Command cmake -ErrorAction SilentlyContinue

Write-Host "Git: $(if($hasGit){'✓'}else{'✗'})"
Write-Host "GCC: $(if($hasGcc){'✓'}else{'✗'})"
Write-Host "Make: $(if($hasMake){'✓'}else{'✗'})"
Write-Host "CMake: $(if($hasCmake){'✓'}else{'✗'})"

# 2. Instalar ferramentas faltantes via Chocolatey
if (-not $hasGcc -or -not $hasMake -or -not $hasCmake) {
    Write-Host "Instalando ferramentas via Chocolatey..." -ForegroundColor Yellow
    
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        if (-not $hasMake) { choco install make -y }
        if (-not $hasCmake) { choco install cmake -y }
        if (-not $hasGcc) { choco install mingw -y }
    } else {
        Write-Host "Chocolatey não encontrado. Instale manualmente:" -ForegroundColor Red
        Write-Host "  - MinGW: https://www.mingw-w64.org/"
        Write-Host "  - CMake: https://cmake.org/download/"
        Write-Host "  - Make: via chocolatey ou MSYS2"
    }
}

# 3. Configurar variáveis de ambiente
Write-Host "Configurando variáveis de ambiente..." -ForegroundColor Yellow
$env:CC = "gcc"
$env:CXX = "g++"

# 4. Verificar Visual C++ Build Tools
$vcppPath = "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools"
if (-not (Test-Path $vcppPath)) {
    $vcppPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
}

if (Test-Path $vcppPath) {
    Write-Host "✓ Visual C++ Build Tools encontrado" -ForegroundColor Green
} else {
    Write-Host "⚠ Visual C++ Build Tools não encontrado" -ForegroundColor Yellow
    Write-Host "  Baixe de: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
}

# 5. Testar compilação
Write-Host "Testando ambiente de compilação..." -ForegroundColor Yellow
try {
    # Teste simples de gcc
    if ($hasGcc) {
        $testResult = & gcc --version 2>&1
        Write-Host "✓ GCC funcionando" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Problema com GCC" -ForegroundColor Red
}

Write-Host "`n=== Configuração concluída ===" -ForegroundColor Green
Write-Host "Agora tente novamente: poetry install" -ForegroundColor Cyan