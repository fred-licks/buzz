; Script para instalação do Buzz PCRS
; Polícia Civil do Estado do Rio Grande do Sul – PCRS
; Dinov/DTIP - Divisão de Inovação do Departamento de Tecnologia da Informação Policial

#define AppName "Buzz PCRS"
#define AppExeName "Buzz.exe"
#define AppPublisher "Polícia Civil do Estado do Rio Grande do Sul – PCRS"
#define AppURL "https://www.pc.rs.gov.br"
#define AppIconPath "assets\buzz_pcrs.ico"
#define AppSourcePath "dist\Buzz\*"
#define OutputDir "dist"
#define AppRegKey "Software\PCRS\Buzz"
#define AppVersion "1.0.0"
#define AppCopyright "Copyright © 2025 PCRS"

[Setup]
; NOTE: O valor AppId identifica unicamente esta aplicação. Não use o mesmo AppId para outras aplicações.
; (Para gerar um novo GUID, clique em Tools | Generate GUID no IDE.)
AppId={{C9C45D2A-029B-4E91-818E-03431D508869}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppCopyright={#AppCopyright}
;AppVerName={#AppName} {#AppVersion}
DefaultDirName={autopf}\PCRS\{#AppName}
DefaultGroupName=PCRS
DisableProgramGroupPage=no
; Remover comentário da linha abaixo para executar em modo de instalação não-administrativa (instalar apenas para o usuário atual)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir={#OutputDir}
OutputBaseFilename=Buzz-PCRS-{#AppVersion}-windows-x64
SetupIconFile={#AppIconPath}
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} - Transcrição de Áudio
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Configurações de segurança e assinatura
; SignTool=signtool
; Configurações visuais
WizardImageFile=assets\wizard-image.bmp
WizardSmallImageFile=assets\wizard-small-image.bmp

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
; Linha original comentada
;Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Criar ícone na &Barra de Tarefas"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: {#AppSourcePath}; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Arquivo de readme/documentação
Source: "README_PCRS.txt"; DestDir: "{app}"; Flags: ignoreversion; DestName: "LEIAME.txt"
; Manual do usuário (se existir)
Source: "manual_usuario_pcrs.pdf"; DestDir: "{app}"; Flags: ignoreversion external skipifsourcedoesntexist
; NOTE: Não use "Flags: ignoreversion" em arquivos compartilhados do sistema

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Comment: "Transcrição de áudio - PCRS"
Name: "{group}\Manual do Usuário"; Filename: "{app}\manual_usuario_pcrs.pdf"; Comment: "Manual de utilização do Buzz PCRS"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autoprograms}\PCRS\{#AppName}"; Filename: "{app}\{#AppExeName}"; Comment: "Transcrição de áudio - PCRS"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon; Comment: "Transcrição de áudio - PCRS"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Configuração de idioma padrão
Root: HKCU; Subkey: "{#AppRegKey}"; ValueType: string; ValueName: "ui-locale"; ValueData: "pt_BR"
; Configurações institucionais
Root: HKCU; Subkey: "{#AppRegKey}"; ValueType: string; ValueName: "instituicao"; ValueData: "PCRS"
Root: HKCU; Subkey: "{#AppRegKey}"; ValueType: string; ValueName: "versao_instalacao"; ValueData: "{#AppVersion}"
Root: HKCU; Subkey: "{#AppRegKey}"; ValueType: string; ValueName: "data_instalacao"; ValueData: "{code:GetCurrentDateTime}"

[Code]
function GetCurrentDateTime(Param: String): String;
begin
  Result := GetDateTimeString('dd/mm/yyyy hh:nn:ss', #0, #0);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if RegKeyExists(HKEY_CURRENT_USER, '{#AppRegKey}') then
      if MsgBox('Deseja excluir as configurações do Buzz PCRS?' + #13#10 + 
                'Isso removerá todas as configurações personalizadas.', 
                mbConfirmation, MB_YESNO) = IDYES
      then
        RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, '{#AppRegKey}');
  end;
end;

procedure DeleteFileOrFolder(FilePath: string);
begin
  if FileExists(FilePath) then
  begin
    DeleteFile(FilePath);
  end
  else if DirExists(FilePath) then
  begin
    DelTree(FilePath, True, True, True);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // Limpar instalação anterior se existir
    DeleteFileOrFolder(ExpandConstant('{app}\Buzz.exe'));
    DeleteFileOrFolder(ExpandConstant('{app}\_internal'));
    // Criar diretório de logs se não existir
    ForceDirectories(ExpandConstant('{localappdata}\PCRS\Buzz\Logs'));
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Verificar se já existe uma instalação
  if RegKeyExists(HKEY_CURRENT_USER, '{#AppRegKey}') then
  begin
    if MsgBox('Uma versão do Buzz PCRS já está instalada.' + #13#10 + 
              'Deseja continuar com a instalação?' + #13#10 + 
              'A versão anterior será atualizada.', 
              mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;