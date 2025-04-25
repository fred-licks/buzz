#!/bin/bash
echo "=== Configurando e iniciando o Buzz ==="

echo "1. Ativando ambiente virtual..."
poetry shell

echo "2. Instalando dependências..."
poetry install

echo "3. Copiando DLLs necessárias..."
if [ ! -f "buzz/libwhisper.so" ] && [ ! -f "buzz/libwhisper.dylib" ]; then
    echo "Copiando arquivos necessários..."
    cp -r ./dll_backup/* ./buzz/
else
    echo "Os arquivos necessários já existem, pulando cópia..."
fi

echo "4. Construindo o projeto..."
poetry build

echo "5. Iniciando o Buzz..."
python -m buzz

echo "=== Concluído ==="