[Setup]
AppName=apocalyptic_translatorZ
OutputBaseFilename=apocalyptic_translatorZ_installer
AppVersion=v0.2.0-alpha
DefaultDirName={src}
UsePreviousAppDir=no
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\apocalyptic_translatorZ.exe
DisableDirPage=yes
SetupIconFile=.\apocalyptic_translatorZ.ico

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "apocalyptic_translatorZ.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Code]
var
  SourceDir: String;
  DeepL_available_language: String;
  GameLabel: TLabel;
  GameName: String;
  DST_Page: TInputOptionWizardPage;
  DST_LanguageCode: String;
  DST_LanguageMsg: String;
  TranslationServicePage: TInputOptionWizardPage;
  TranslationService: String;
  ResultCode: Integer;

function InitializeSetup(): Boolean;
var
  SourceDir: String;
begin
  SourceDir := ExpandConstant('{src}');

  // Vérifie si le chemin contient un des mots-clés (en ignorant la casse)
  if (Pos('PARADOX OF HOPE', UpperCase(SourceDir)) = 0) and
     (Pos('CONVRGENCE', UpperCase(SourceDir)) = 0) and
     (Pos('ZONA', UpperCase(SourceDir)) = 0) then
  begin
    MsgBox('Error: This installer must be placed in the root directory of one of the following games: "CONVRGENCE", "Paradox of Hope", "ZONA" ou "ZONAORIGIN".' + #13#10 +
           'Please move this installer to the appropriate Steam folder "steamapps/common/<GAME NAME>/" and restart the installer.', 
           mbError, MB_OK);
    Result := False; // Ferme l'installateur
    exit;
  end;

  Result := True; // Continue l'installation
end;

procedure TranslationServicePageOnActivate(Page: TWizardPage);
var
  SourceDir: String;
begin
  SourceDir := ExpandConstant('{src}');
  // Vérifie si le chemin contient un jeux supportés par le traductions DeepL (en ignorant la casse)
  if (Pos('CONVRGENCE', UpperCase(SourceDir)) > 0) or
     (Pos('ZONAORIGIN', UpperCase(SourceDir)) > 0) then
  begin
    //  Chinese Simplified      Czech                   Japanese                Korean                  Français            
    if (DST_Page.Values[0]) or (DST_Page.Values[1]) or (DST_Page.Values[8]) or (DST_Page.Values[9]) or (DST_Page.Values[6]) then
    begin
      // Réactiver DeepL si autre langue
      TranslationServicePage.CheckListBox.ItemEnabled[0] := True;
    end
    else
    begin
      // Désactiver DeepL (index 0 dans TranslationServicePage)
      TranslationServicePage.CheckListBox.ItemEnabled[0] := False;
      TranslationServicePage.Values[0] := False;  // le décocher si actif
      TranslationServicePage.Values[1] := True;   // forcer Google
    end
  end
  else
  begin
    // Désactiver DeepL (index 0 dans TranslationServicePage)
    TranslationServicePage.CheckListBox.ItemEnabled[0] := False;
    TranslationServicePage.Values[0] := False;  // le décocher si actif
    TranslationServicePage.Values[1] := True;   // forcer Google
  end;
end;

procedure InitializeWizard;
begin
  // Initialiser SourceDir
  SourceDir := ExpandConstant('{src}');
  DeepL_available_language := '   CONVRGENCE in French, Czech, Chinese Simplified, japanese and Korean.' + #13#10 + '   ZONAORIN in French, Czech.'


  if Pos('PARADOX OF HOPE', UpperCase(SourceDir)) > 0 then
    GameName := 'Paradox of Hope'
  else if Pos('CONVRGENCE', UpperCase(SourceDir)) > 0 then
    GameName := 'CONVRGENCE'
  else if Pos('ZONAORIGIN', UpperCase(SourceDir)) > 0 then
    GameName := 'ZONAORIGIN'
  else if Pos('ZONA', UpperCase(SourceDir)) > 0 then
    GameName := 'ZONA'
  else
    GameName := 'Unknown Game';

  // Destination language (Texts and Subtitles)
  DST_Page := CreateInputOptionPage(wpWelcome, 'TEXTS and SUBTITLES selection', '', 'Choose your TEXTS and SUBTITLES preferred language for detected game: ' + GameName, True, True);

  GameLabel := TLabel.Create(DST_Page);
  GameLabel.Parent := DST_Page.Surface;
  GameLabel.Caption := 'Detected game: ' + GameName;
  GameLabel.Top := 0;
  GameLabel.Left := 0;

  DST_Page.Add('中国語（簡体字）(Chinese Simplified) only for CONVRGENCE');  //  0 (DeepL/Google) (Only for CONVRGENCE)
  DST_Page.Add('Čeština (Czech)');                                         //  1 (DeepL/Google)
  DST_Page.Add('Dansk (Danish)');                                          //  2 (Google)
  DST_Page.Add('Deutch (German)');                                         //  3 (Google)
  DST_Page.Add('English (English)');                                       //  4 (Google)
  DST_Page.Add('Español (Spanish)');                                       //  5 (Google)
  DST_Page.Add('Français (French)');                                       //  6 (DeepL/Google)
  DST_Page.Add('Italiano (Italian)');                                      //  7 (Google)
  DST_Page.Add('日本語 ひらがな (Japanese Hiragana) only for CONVRGENCE');  //  8 (DeepL/Google) (Only for CONVRGENCE)
  DST_Page.Add('한국어 (Korean) only for CONVRGENCE');                     //  9 (DeepL/Google) (Only for CONVRGENCE)
  DST_Page.Add('Magyar (Hungarian)');                                      // 10 (Google)
  DST_Page.Add('Nederlands (Dutch)');                                      // 11 (Google)
  DST_Page.Add('Polski (Polish)');                                         // 12 (Google)
  DST_Page.Add('Português (Portuguese)');                                  // 13 (Google)
  DST_Page.Add('Română (Romanian)');                                       // 14 (Google)
  DST_Page.Add('Suomi (Finnish)');                                         // 15 (Google)
  DST_Page.Add('Svenska (Swedish)');                                       // 16 (Google)
  DST_Page.Values[4] := True; // Default is 'English (English)'

  // Désactiver Chinese Simplified, Japanese and Korean si SourceDir contient "Paradox of Hope" ou "ZONA"
  if (Pos('PARADOX OF HOPE', UpperCase(SourceDir)) > 0) or (Pos('ZONA', UpperCase(SourceDir)) > 0) then
  begin
    DST_Page.CheckListBox.ItemEnabled[0] := False;  // Griser l'option Chinese Simplified
    DST_Page.Values[0] := False;                    // Décocher Chinese Simplified si actif
    DST_Page.CheckListBox.ItemEnabled[8] := False;  // Griser l'option Japanese
    DST_Page.Values[8] := False;                    // Décocher Japanese si actif
    DST_Page.CheckListBox.ItemEnabled[9] := False;  // Griser l'option Korean
    DST_Page.Values[9] := False;                    // Décocher Korean si actif
  end;

  // Translation Service Selection Page (AFTER language page)
  TranslationServicePage := CreateInputOptionPage(DST_Page.ID,
    'Translation service selection',
    'Please select the offline translation service',
    'Select the offline translation service you wish to use.'
          + #13#10#13#10
          + '✔ The translation files for all subtitle languages are already stored in this installer.'
          + #13#10#13#10
          + '✔ In case of missing translations then Google translate online service will be used to update missing translations.'
          + #13#10#13#10
          + '✔ IMPORTANT:'
          + #13#10
          + '   "Translate with DeepL" option is currently available only for:' + #13#10 + DeepL_available_language
          + #13#10#13#10,
    True, False);
  TranslationServicePage.Add('Translate with DeepL');
  TranslationServicePage.Add('Translate with Google');
  TranslationServicePage.Values[0] := True; // par défaut DeepL

  // Attacher l’événement OnActivate
  TranslationServicePage.OnActivate := @TranslationServicePageOnActivate;
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
    DST_LanguageMsg := '✔ REMEMBER: ' + #13#10 + 'Launch your game and select Russian or Ukrainian in the ' + gameName + ' settings! Subtitles in your native language should appear!';

    // 中国語（簡体字）(Chinese Simplified)  //  0 (DeepL/Google) (Only for CONVRGENCE)
    // Čeština (Czech)                     //  1 (DeepL/Google)
    // Dansk (Danish)                      //  2 (Google)
    // Deutch (German)                     //  3 (Google)
    // English (English)                   //  4 (Google)
    // Español (Spanish)                   //  5 (Google)
    // Français (French)                   //  6 (DeepL/Google)
    // Italiano (Italian)                  //  7 (Google)
    // 日本語 ひらがな (Japanese Hiragana)   //  8 (DeepL/Google) (Only for CONVRGENCE)
    // 한국어 (Korean)                      //  9 (DeepL/Google) (Only for CONVRGENCE)
    // Magyar (Hungarian)                  // 10 (Google)
    // Nederlands (Dutch)                  // 11 (Google)
    // Polski (Polish)                     // 12 (Google)
    // Português (Portuguese)              // 13 (Google)
    // Română (Romanian)                   // 14 (Google)
    // Suomi (Finnish)                     // 15 (Google)
    // Svenska (Swedish)                   // 16 (Google)

    if DST_Page.Values[0] then
    begin
      DST_LanguageCode := 'zh';
      DST_LanguageMsg := '✔ 请记住： ' + #13#10#13#10 + '启动您的游戏' + GameName + '，并在游戏设置中选择俄语或乌克兰语！' + #13#10#13#10 + '您母语的字幕应该会显示出来！';
    end
    else if DST_Page.Values[1] then
    begin
      DST_LanguageCode := 'cs';
      DST_LanguageMsg := '✔ PAMATUJTE: ' + #13#10 + 'Spusťte hru ' + GameName + ' a v nastavení hry vyberte jazyk ruština nebo ukrajinština! ' + #13#10#13#10 + 'Titulky ve vašem rodném jazyce by se měly zobrazit!';
    end
    else if DST_Page.Values[2] then
    begin
      DST_LanguageCode := 'da';
      DST_LanguageMsg := '✔ HUSK: ' + #13#10 + 'Start dit spil ' + GameName + ' og vælg sprogene russisk eller ukrainsk i spilindstillingerne! ' + #13#10#13#10 + 'Undertekster på dit modersmål bør nu vises!';
    end
    else if DST_Page.Values[3] then
    begin
      DST_LanguageCode := 'de';
      DST_LanguageMsg := '✔ DENKEN SIE DARAN: ' + #13#10 + 'Starten Sie Ihr Spiel ' + GameName + ' und wählen Sie in den Spieleinstellungen die Sprache Russisch oder Ukrainisch aus! ' + #13#10#13#10 + 'Die Untertitel in Ihrer Muttersprache sollten nun angezeigt werden!';
    end
    else if DST_Page.Values[4] then
    begin
      DST_LanguageCode := 'en';
      DST_LanguageMsg := '✔ REMEMBER: ' + #13#10 + 'Launch your game ' + GameName + ' and select Russian or Ukrainian in the game settings! ' + #13#10#13#10 + 'Subtitles in your native language should appear!';
    end
    else if DST_Page.Values[5] then
    begin
      DST_LanguageCode := 'es';
      DST_LanguageMsg := '✔ RECUERDA: ' + #13#10 + '¡Inicia tu juego ' + GameName + ' y selecciona el idioma ruso o ucraniano en la configuración del juego! ' + #13#10#13#10 + '¡Los subtítulos en tu idioma nativo deberían aparecer!';
    end
    else if DST_Page.Values[6] then
    begin
      DST_LanguageCode := 'fr';
      DST_LanguageMsg := '✔ RAPPELEZ-VOUS: ' + #13#10 + 'Lancez votre jeu ' + GameName + ' et sélectionnez le langage Russe ou Ukrainien dans les paramètres du jeu! ' + #13#10#13#10 + 'Les sous-titres dans votre langue maternelle devraient apparaître!';
    end
    else if DST_Page.Values[7] then
    begin
      DST_LanguageCode := 'it';
      DST_LanguageMsg := '✔ RICORDA: ' + #13#10 + 'avvia il gioco ' + GameName + ' e seleziona la lingua russa o ucraina nelle impostazioni di gioco! ' + #13#10#13#10 + 'Dovrebbero apparire i sottotitoli nella tua lingua madre!';
    end
    else if DST_Page.Values[8] then
    begin
      DST_LanguageCode := 'ja';
      DST_LanguageMsg := '✔ 覚えておいてください: ' + #13#10 + 'ゲーム ' + GameName + ' を起動し、ゲーム設定でロシア語またはウクライナ語を選択してください！' + #13#10#13#10 + '母国語の字幕が表示されるはずです！';
    end
    else if DST_Page.Values[9] then
    begin
      DST_LanguageCode := 'ko';
      DST_LanguageMsg := '✔ 기억하세요: ' + #13#10 + '게임 ' + GameName + '을 실행하고 게임 설정에서 러시아어 또는 우크라이나어를 선택하세요! ' + #13#10#13#10 + '그러면 모국어 자막이 표시될 것입니다!';
    end
    else if DST_Page.Values[10] then
    begin
      DST_LanguageCode := 'hu';
      DST_LanguageMsg := '✔ NE FELEDJE: ' + #13#10 + 'Indítsa el a ' + GameName + ' játékot, és válassza ki az orosz vagy ukrán nyelvet a játék beállításaiban! ' + #13#10#13#10 + 'A feliratok az Ön anyanyelvén jelennek meg!';
    end
    else if DST_Page.Values[11] then
    begin
      DST_LanguageCode := 'nl';
      DST_LanguageMsg := '✔ LET OP: ' + #13#10 + 'Start uw spel ' + GameName + ' en selecteer Russisch of Oekraïens in de spelinstellingen! ' + #13#10#13#10 + 'De ondertitels in uw moedertaal zouden nu moeten verschijnen!';
    end
    else if DST_Page.Values[12] then
    begin
      DST_LanguageCode := 'pl';
      DST_LanguageMsg := '✔ PAMIĘTAJ: ' + #13#10 + 'Uruchom grę ' + GameName + ' i wybierz język rosyjski lub ukraiński w ustawieniach gry! ' + #13#10#13#10 + 'Napisy w Twoim języku ojczystym powinny się pojawić!';
    end
    else if DST_Page.Values[13] then
    begin
      DST_LanguageCode := 'pt';
      DST_LanguageMsg := '✔ LEMBRE-SE: Inicie o seu jogo ' + GameName + ' e selecione o idioma russo ou ucraniano nas configurações do jogo! ' + #13#10#13#10 + 'As legendas no seu idioma nativo devem aparecer!';
    end
    else if DST_Page.Values[14] then
    begin
      DST_LanguageCode := 'ro';
      DST_LanguageMsg := '✔ REȚINEȚI: ' + #13#10 + 'Lansați jocul ' + GameName + ' și selectați limba rusă sau ucraineană în setările jocului! ' + #13#10#13#10 + 'Subtitrările în limba maternă ar trebui să apară!';
    end
    else if DST_Page.Values[15] then
    begin
      DST_LanguageCode := 'fi';
      DST_LanguageMsg := '✔ MUISTA: ' + #13#10 + 'Käynnistä peli ' + GameName + ' ja valitse pelin asetuksista kieli venäjä tai ukraina! ' + #13#10#13#10 + 'Omakieliset tekstitykset pitäisi näkyä!';
    end
    else
    begin
      DST_LanguageCode := 'sv';
      DST_LanguageMsg := '✔ KOM IHÅG: ' + #13#10 + 'Starta spelet ' + GameName + ' och välj ryska eller ukrainska som språk i spelinställningarna! ' + #13#10#13#10 + 'Undertexter på ditt modersmål bör då visas!';
    end;
      
    // Execute auto_ZONA_translator.exe with the selected language and capture the return code
    Exec(ExpandConstant('{app}\apocalyptic_translatorZ.exe'), '-ls auto -l ' + DST_LanguageCode  + ' -t ' + TranslationService + ' -v --force', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);

    // Check if the return code is -1, initiate uninstallation if it is
    // if ResultCode = -1 then
    if (ResultCode = -1) or (ResultCode <> 0) then
    begin
      MsgBox('The application encountered an error and will now uninstall.', mbError, MB_OK);
      Exec(ExpandConstant('{uninstallexe}'), '/VERYSILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end
    else
    begin
      MsgBox(DST_LanguageMsg, mbInformation, MB_OK);
    end;
  end;
end;
