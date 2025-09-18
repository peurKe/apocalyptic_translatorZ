[Setup]
AppName=apocalyptic_translatorZ
OutputBaseFilename=apocalyptic_translatorZ_installer_ZH
AppVersion=v0.1.4-alpha
DefaultDirName={src}
UsePreviousAppDir=no
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\apocalyptic_translatorZ.exe
DisableDirPage=no
SetupIconFile=.\apocalyptic_translatorZ.ico

[Languages]
Name: "ro"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
Source: "apocalyptic_translatorZ.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Code]
var
  // BEGIN CONVRGENCE + Paradox of Hope are only Russian Voices / Z.O.N.A project X is only Ukrainian Voices
  SourceDir: String;
  Only_OneLang: Boolean;
  Only_OneLang_1: String;
  Only_OneLang_2: String;
  Only_OneLang_3: String;
  // END CONVRGENCE + Paradox of Hope are only Russian Voices / Z.O.N.A project X is only Ukrainian Voices
  SRC_Page: TInputOptionWizardPage;
  SRC_LanguageCode: String;
  SRC_LanguageName: String;
  DST_Page: TInputOptionWizardPage;
  DST_LanguageCode: String;
  DST_LanguageMsg: String;
  ResultCode: Integer;
  TranslationServicePage: TInputOptionWizardPage;
  TranslationService: String;

procedure InitializeWizard;
begin

  // BEGIN CONVRGENCE + Paradox of Hope are only Russian Voices / Z.O.N.A project X is only Ukrainian Voices
  SourceDir := ExpandConstant('{src}');
  Only_OneLang_1 := 'CONVRGENCE';
  Only_OneLang_2 := 'Paradox of Hope';
  Only_OneLang_3 := 'ZONA';

  Only_OneLang := False;
  if (Pos(Only_OneLang_1, SourceDir) > 0) or (Pos(Only_OneLang_2, SourceDir) > 0) then
  begin
    Only_OneLang := True;
    SRC_LanguageCode := 'ru';
    SRC_LanguageName := '俄语'
  end;
  if (Pos(Only_OneLang_3, SourceDir) > 0) then
  begin
    Only_OneLang := True;
    SRC_LanguageCode := 'uk';
    SRC_LanguageName := '乌克兰语';
  end;

  if not Only_OneLang then
  begin
    // Source language (Voices)
    SRC_Page := CreateInputOptionPage(wpWelcome, '选择游戏语音', '', '为游戏中的语音选择您喜欢的语言：', True, False);
    SRC_Page.Add('乌克兰语（普里皮亚季的母语，最大限度的沉浸！）.');
    SRC_Page.Add('俄语');
    SRC_Page.Values[0] := True;
  end;
  // END CONVRGENCE + Paradox of Hope are only Russian Voices / Z.O.N.A project X is only Ukrainian Voices

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
    // BEGIN CONVRGENCE + Paradox of Hope are only Russian Voices / Z.O.N.A project X is only Ukrainian Voices
    if not Only_OneLang then
    begin
      // Source language (Voices)
      if SRC_Page.Values[0] then
      begin
        SRC_LanguageCode := 'uk';
        SRC_LanguageName := '乌克兰语';
      end
      else
      begin
        SRC_LanguageCode := 'ru';
        SRC_LanguageName := '俄罗斯';
      end;
    end;
    // END CONVRGENCE + Paradox of Hope are only Russian Voices / Z.O.N.A project X is only Ukrainian Voices

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
    DST_LanguageMsg := '要享受法语文字和 ' + SRC_LanguageName + ' 语音：从 Steam 启动游戏，然后在游戏语言设置中选择 “' + SRC_LanguageName + '”。祝您在游戏区玩得开心！'

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
