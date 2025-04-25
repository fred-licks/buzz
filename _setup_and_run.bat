@echo off
echo === Configurando e iniciando o Buzz ===

echo 1. Instalando dependências...
call poetry install

echo 2. Atualizando backup de DLLs...
if exist buzz\dll_backup (
    echo Removendo backup anterior...
    rd /s /q buzz\dll_backup
)

echo Copiando novo backup...
xcopy /E /I /Y dll_backup buzz\dll_backup

echo 3. Construindo o projeto...
call poetry build

echo 4. Gerando distribuição...
call make dist/Buzz

echo 5. Compilando o instalador...


echo === Concluído ===