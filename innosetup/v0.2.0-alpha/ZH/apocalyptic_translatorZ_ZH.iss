[Setup]
AppName=apocalyptic_translatorZ
OutputBaseFilename=apocalyptic_translatorZ_installer_ZH
AppVersion=v0.1.9-alpha
DefaultDirName={src}
UsePreviousAppDir=no
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\apocalyptic_translatorZ.exe
DisableDirPage=yes
SetupIconFile=.\apocalyptic_translatorZ.ico

[Languages]
Name: "zh"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
Source: "apocalyptic_translatorZ.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Code]
var
  SourceDir: String;
  SRC_Page: TInputOptionWizardPage;
  SRC_LanguageCode: String;
  SRC_LanguageName: String;
  DST_Page: TInputOptionWizardPage;
  DST_LanguageCode: String;
  DST_LanguageMsg: String;
  ResultCode: Integer;
  TranslationServicePage: TInputOptionWizardPage;
  TranslationService: String;

function InitializeSetup(): Boolean;
var
  SourceDir: String;
begin
  SourceDir := ExpandConstant('{src}');

  // Check if the path contains CONVERGENCE (ignoring case)
  if (Pos('CONVRGENCE', UpperCase(SourceDir)) = 0) then
  begin
    MsgBox('错误：此安装程序必须放置在“CONVRGENCE”游戏的根目录下。' + #13#10 +
           '请将此安装程序移动至相应的Steam文件夹“steamapps/common/<游戏名称>/”，然后重新启动安装程序。', 
           mbError, MB_OK);
    Result := False; // Ferme l'installateur
    exit;
  end;

  Result := True; // Continue l'installation
end;

procedure InitializeWizard;
begin
  // Destination language (Texts and Subtitles)
  DST_LanguageCode := 'zh'

  // Translation Service Selection Page
  TranslationServicePage := CreateInputOptionPage(wpWelcome,'选择翻译服务', '请选择翻译工具', '选择要使用的翻译服务：', True, False);
  TranslationServicePage.Add('使用 DeepL 进行翻译');
  TranslationServicePage.Add('使用 Google 进行翻译');
  // Default to DeepL and Google as failback
  TranslationServicePage.Values[0] := True;

end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SRC_LanguageCode := 'auto';
    SRC_LanguageName := '俄罗斯';  // Russian

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
    // DST_LanguageMsg := '要享受法语文字和 ' + SRC_LanguageName + ' 语音：从 Steam 启动游戏，然后在游戏语言设置中选择 “' + SRC_LanguageName + '”。祝您在游戏区玩得开心！'
    DST_LanguageMsg := '要同时享受法语文本和 ' + SRC_LanguageName + ' 语音：请通过Steam启动《CONVRGENCE》，然后在游戏语言设置中选择 “' + SRC_LanguageName + '”。' + #10#13 + '祝您在游戏世界中尽情享受！'

    // Execute auto_ZONA_translator.exe with the selected language and capture the return code
    Exec(ExpandConstant('{app}\apocalyptic_translatorZ.exe'), '-ls ' + SRC_LanguageCode + ' -l ' + DST_LanguageCode + ' -t ' + TranslationService + ' -v --force', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);

    // Check if the return code is -1, initiate uninstallation if -1 or not equal 0
    // if ResultCode = -1 then
    if (ResultCode = -1) or (ResultCode <> 0) then
    begin
      MsgBox('安装程序遇到错误。翻译未正确安装。正在卸载。', mbError, MB_OK);
      Exec(ExpandConstant('{uninstallexe}'), '/VERYSILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end
    else
    begin
      MsgBox(DST_LanguageMsg, mbInformation, MB_OK);
    end;
  end;
end;
