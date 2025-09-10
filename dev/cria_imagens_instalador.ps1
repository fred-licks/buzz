# Script corrigido com fundo PRETO para as imagens do instalador PCRS
# Contexto: PowerShell no diretório E:\GitHub\third-party\buzz

Write-Host "=== CORRIGINDO IMAGENS COM FUNDO PRETO ===" -ForegroundColor Cyan

# Caminho do logo da PCRS
$LogoPath = "buzz\assets\buzz-icon-1024_pcrs.png"

if (Test-Path $LogoPath) {
    Write-Host "✓ Logo encontrado: $LogoPath" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Logo não encontrado - usando design básico" -ForegroundColor Yellow
    $LogoPath = $null
}

Add-Type -AssemblyName System.Drawing

function New-PCRSImage {
    param(
        [int]$Width,
        [int]$Height,
        [string]$OutputPath,
        [string]$LogoPath = $null
    )
    
    Write-Host "Criando: $OutputPath ($Width x $Height) - FUNDO PRETO" -ForegroundColor Gray
    
    # Cores institucionais PCRS - PRETO E BRANCO
    $preto = [System.Drawing.Color]::Black
    $branco = [System.Drawing.Color]::White
    $cinzaEscuro = [System.Drawing.Color]::FromArgb(40, 40, 40)  # Para gradiente sutil
    
    # Criar bitmap
    $bitmap = New-Object System.Drawing.Bitmap($Width, $Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAlias
    
    if ($Width -eq 164) {
        # === IMAGEM LATERAL (164x314) - FUNDO PRETO ===
        
        # FUNDO COMPLETAMENTE PRETO (sem gradiente para garantir)
        $brushPreto = New-Object System.Drawing.SolidBrush($preto)
        $graphics.FillRectangle($brushPreto, 0, 0, $Width, $Height)
        $brushPreto.Dispose()
        
        $logoOffset = 60
        
        # Carregar logo da PCRS
        if ($LogoPath -and (Test-Path $LogoPath)) {
            try {
                $logo = [System.Drawing.Image]::FromFile((Resolve-Path $LogoPath).Path)
                
                # Logo centralizado no topo
                $logoSize = 80
                $logoX = ($Width - $logoSize) / 2
                $logoY = 40
                
                $graphics.DrawImage($logo, $logoX, $logoY, $logoSize, $logoSize)
                $logo.Dispose()
                
                $logoOffset = 140
                Write-Host "  ✓ Logo PCRS inserido (fundo preto)" -ForegroundColor Green
            }
            catch {
                Write-Host "  ⚠️  Erro com logo: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
        
        # Texto em branco sobre fundo preto
        $fontTitulo = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)
        $fontSubtitulo = New-Object System.Drawing.Font("Segoe UI", 11)
        $fontRodape = New-Object System.Drawing.Font("Segoe UI", 8)
        $brushBranco = New-Object System.Drawing.SolidBrush($branco)
        
        # Formato centralizado
        $formato = New-Object System.Drawing.StringFormat
        $formato.Alignment = [System.Drawing.StringAlignment]::Center
        
        # Título - BUZZ PCRS
        $rectTitulo = New-Object System.Drawing.RectangleF(10, $logoOffset, ($Width - 20), 50)
        $graphics.DrawString("BUZZ PCRS", $fontTitulo, $brushBranco, $rectTitulo, $formato)
        
        # Subtítulo
        $rectSubtitulo = New-Object System.Drawing.RectangleF(10, ($logoOffset + 60), ($Width - 20), 80)
        $graphics.DrawString("Sistema de Transcrição`ne Tradução de Áudio", $fontSubtitulo, $brushBranco, $rectSubtitulo, $formato)
        
        # Rodapé institucional
        $rectRodape = New-Object System.Drawing.RectangleF(10, ($Height - 60), ($Width - 20), 50)
        $graphics.DrawString("Polícia Civil`nRio Grande do Sul", $fontRodape, $brushBranco, $rectRodape, $formato)
        
        # Cleanup
        $fontTitulo.Dispose()
        $fontSubtitulo.Dispose()
        $fontRodape.Dispose()
        $brushBranco.Dispose()
        $formato.Dispose()
    }
    else {
        # === ÍCONE PEQUENO (55x55) - SEM FUNDO BRANCO ===
        
        # Usar fundo transparente ou preto para manter consistência
        # Como BMP não suporta transparência, usar fundo preto como a imagem lateral
        $graphics.FillRectangle([System.Drawing.Brushes]::Black, 0, 0, $Width, $Height)
        
        if ($LogoPath -and (Test-Path $LogoPath)) {
            try {
                $logo = [System.Drawing.Image]::FromFile((Resolve-Path $LogoPath).Path)
                
                # Logo centralizado ocupando todo o espaço disponível
                $logoSize = 50  # Maior para ocupar mais espaço
                $logoX = ($Width - $logoSize) / 2
                $logoY = ($Height - $logoSize) / 2
                
                $graphics.DrawImage($logo, $logoX, $logoY, $logoSize, $logoSize)
                $logo.Dispose()
                Write-Host "  ✓ Logo inserido no ícone (sem fundo branco)" -ForegroundColor Green
            }
            catch {
                # Fallback: apenas o logo PCRS simples sem círculo
                $font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
                $brushBranco = New-Object System.Drawing.SolidBrush($branco)
                $formato = New-Object System.Drawing.StringFormat
                $formato.Alignment = [System.Drawing.StringAlignment]::Center
                $formato.LineAlignment = [System.Drawing.StringAlignment]::Center
                
                $rect = New-Object System.Drawing.RectangleF(0, 0, $Width, $Height)
                $graphics.DrawString("PCRS", $font, $brushBranco, $rect, $formato)
                
                $font.Dispose()
                $brushBranco.Dispose()
                $formato.Dispose()
            }
        }
        else {
            # Design padrão: apenas texto PCRS centralizado sem círculo
            $font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
            $brushBranco = New-Object System.Drawing.SolidBrush($branco)
            $formato = New-Object System.Drawing.StringFormat
            $formato.Alignment = [System.Drawing.StringAlignment]::Center
            $formato.LineAlignment = [System.Drawing.StringAlignment]::Center
            
            $rect = New-Object System.Drawing.RectangleF(0, 0, $Width, $Height)
            $graphics.DrawString("PCRS", $font, $brushBranco, $rect, $formato)
            
            $font.Dispose()
            $brushBranco.Dispose()
            $formato.Dispose()
        }
    }
    
    # Salvar como BMP
    $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Bmp)
    
    # Cleanup
    $graphics.Dispose()
    $bitmap.Dispose()
    
    Write-Host "✓ Salvo: $OutputPath" -ForegroundColor Green
}

try {
    Write-Host "`n=== RECRIANDO COM FUNDO PRETO ===" -ForegroundColor Cyan
    
    # Remover imagens antigas se existirem
    if (Test-Path "assets\wizard-image.bmp") {
        Remove-Item "assets\wizard-image.bmp"
        Write-Host "Removida imagem anterior (vermelha)" -ForegroundColor Yellow
    }
    if (Test-Path "assets\wizard-small-image.bmp") {
        Remove-Item "assets\wizard-small-image.bmp"
        Write-Host "Removida imagem anterior (vermelha)" -ForegroundColor Yellow
    }
    
    # Criar novas imagens com fundo PRETO
    New-PCRSImage -Width 164 -Height 314 -OutputPath "assets\wizard-image.bmp" -LogoPath $LogoPath
    New-PCRSImage -Width 55 -Height 55 -OutputPath "assets\wizard-small-image.bmp" -LogoPath $LogoPath
    
    Write-Host "`n✅ IMAGENS CORRIGIDAS - FUNDO PRETO!" -ForegroundColor Green
    
    # Verificar resultado
    Get-ChildItem "assets\wizard*.bmp" | ForEach-Object {
        $sizeKB = [math]::Round($_.Length / 1024, 1)
        Write-Host "  ✓ $($_.Name) - $sizeKB KB - FUNDO PRETO" -ForegroundColor White
    }
    
    Write-Host "`n=== PRÓXIMO PASSO ===" -ForegroundColor Yellow
    Write-Host "Compile o instalador: iscc installer.iss" -ForegroundColor White
}
catch {
    Write-Host "❌ Erro: $($_.Exception.Message)" -ForegroundColor Red
}