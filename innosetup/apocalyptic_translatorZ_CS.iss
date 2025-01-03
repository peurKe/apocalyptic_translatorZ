[Setup]
AppName=apocalyptic_translatorZ
OutputBaseFilename=apocalyptic_translatorZ_installer_CS
AppVersion=v0.1.9-alpha
DefaultDirName={src}
UsePreviousAppDir=no
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\apocalyptic_translatorZ.exe
DisableDirPage=no
SetupIconFile=.\apocalyptic_translatorZ.ico

[Languages]
Name: "ro"; MessagesFile: "compiler:Languages\Czech.isl"

[Files]
Source: "apocalyptic_translatorZ.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Code]
var
  DST_LanguageCode: String;
  DST_LanguageMsg: String;
  ResultCode: Integer;
  TranslationServicePage: TInputOptionWizardPage;
  TranslationService: String;

procedure InitializeWizard;
begin
  // Destination language (Texts and Subtitles)
  DST_LanguageCode := 'cs'

  // Translation Service Selection Page
  TranslationServicePage := CreateInputOptionPage(wpWelcome,'Výběr překladatelské služby', 'Vyberte překladatelskou službu', 'Vyberte překladatelskou službu, kterou chcete použít:', True, False);
  TranslationServicePage.Add('Přeložit pomocí DeepL');
  TranslationServicePage.Add('Přeložit pomocí Google');
  // Default to DeepL and Google as failback
  TranslationServicePage.Values[0] := True;

end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Determine selected translation service
    if TranslationServicePage.Values[0] then
    begin
      // Default to Deepl Translate and Google as failback
      TranslationService := 'deepl,google';
    end
    else
    begin
      // Default to Google Translate and DeepL as failback
      TranslationService := 'google,deepl';
    end;

    // Destination language (Texts and Subtitles)
    DST_LanguageMsg := 'Chcete-li si vychutnat TEXTY v ČEŠTINĚ s originálními hlasy: Spusťte hru ve službě Steam a v nastavení jazyka hry vyberte originální jazyk. BAVTE SE V ZÓNĚ!'

    // Execute auto_ZONA_translator.exe with the selected language and capture the return code
    Exec(ExpandConstant('{app}\apocalyptic_translatorZ.exe'), '-ls auto -l ' + DST_LanguageCode + ' -t ' + TranslationService + ' -v --force', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);

    // Check if the return code is -1, initiate uninstallation if -1 or not equal 0
    // if ResultCode = -1 then
    if (ResultCode = -1) or (ResultCode <> 0) then
    begin
      MsgBox('Instalační program narazil na chybu. Překlady nebyly správně nainstalovány. Probíhá odinstalace.', mbError, MB_OK);
      Exec(ExpandConstant('{uninstallexe}'), '/VERYSILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end
    else
    begin
      MsgBox(DST_LanguageMsg, mbInformation, MB_OK);
    end;
  end;
end;
