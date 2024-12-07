# apocalyptic_translatorZ

Mod for translating all Ukrainian or Russian texts of the following Steam games:
- '**CONVRGENCE**' by NikZ
- '**Paradox of Hope**' by NikZ
- '**Z.O.N.A Origin**' by AGaming+
- '**Z.O.N.A Project X**' by AGaming+

And enjoy Ukrainian or Russian voices while having all the texts in your native language!

This mod is an evolution of my previous mod [auto_ZONA_translator](https://github.com/peurKe/auto_ZONA_translator)

<!-- TOC -->
- [Discord](#Discord)
- [Prerequisites](#Prerequisites)
- [Currently supported languages](#Currently-supported-languages)
- [Usage from executable installer](#Usage-from-executable-installer)
- [Release notes](#Release-notes)
<!-- /TOC -->

# Discord

- CONVRGENCE: [16 additional subtitle languages to play with Russian voices](https://discord.com/channels/869881583635664946/1309965989462544395)
- ZONA Origin: [Welcome to #zona-translate-deepl!](https://discord.com/channels/1113935727202410691/1302585407308955690)

# Prerequisites

- Your '**CONVRGENCE**', '**Z.O.N.A Origin**' or '**Z.O.N.A Project X**' games must be up to date

  (As '**Paradox of Hope**' is no longer hosted by Steam, you need to make sure you have an updated version yourself.)

- Your PC must have an Internet connection for API requests from online translators when the new game texts are not yet present and translated inside the mod.

# Currently supported languages

- 中国語（簡体字） (Chinese Simplified)
- 日本語（ひらがな） (Japanese Hiragana)
- 한국어 (Korean)
- Čeština (Czech)
- Dansk (Danish)
- English (English)
- Español (Spanish)
- Français (French)
- German (German)
- Italiano (Italian)
- Magyar (Hungarian)
- Nederlands (Dutch)
- Polski (Polish)
- Português (Portuguese)
- Română (Romanian)
- Suomi (Finnish)
- Svenska (Swedish)

# Usage from executable installer

## Go to the Latest release:

- [Latest release](https://github.com/peurKe/apocalyptic_translatorZ/releases)

## Download the EXE installer '**apocalyptic_translatorZ_installer.exe**' from the release assets

The '**apocalyptic_translatorZ_installer.exe**' installer can be used for **CONVRGENCE**, **Paradox of Hope**, **Z.O.N.A Origin**, **Z.O.N.A Project X** games.

Choose the default installer for all latin languages:
- **apocalyptic_translatorZ_installer.exe** embedding texts and subtitles for **all supported languages**

## Copy the downloaded EXE installer into game folder

- Copy it to your **CONVRGENCE** or **Paradox of Hope** or **Z.O.N.A Project X** or **Z.O.N.A Origin** game folder in your Steam library.
  By default in :
    - **CONVRGENCE** :arrow_right: C:\Program Files (x86)\Steam\steamapps\common\CONVRGENCE\
    - **Paradox of Hope** :arrow_right: C:\Program Files (x86)\Steam\steamapps\common\Paradox of Hope\ (You will first need to add the game as a non-Steam game)
    - **Z.O.N.A Project X** :arrow_right: C:\Program Files (x86)\Steam\steamapps\common\ZONA\
    - **Z.O.N.A Origin** :arrow_right: C:\Program Files (x86)\Steam\steamapps\common\ZONAORIGIN\

   NB: If your Z.O.N.A game is installed on a drive other than the C: system drive, your game folder could be in the following location:
    - **CONVRGENCE** :arrow_right: E:\Steam\Library\steamapps\common\CONVRGENCE\
    - **Paradox of Hope** :arrow_right: E:\Steam\Library\steamapps\common\Paradox of Hope\
    - **Z.O.N.A Project X** :arrow_right: E:\SteamLibrary\steamapps\common\ZONA\
    - **Z.O.N.A Origin** :arrow_right: E:\Steam\Library\steamapps\common\ZONAORIGIN\

   If you want to retrieve your game folder, go to your library in Steam and:
    - Right-click on your game in your list of games in the left-hand panel.
    - Click on 'Properties...'
    - Click on 'Browse...'
   An explorer window will appear showing the folder for your game.
 
## Go to your game directory.

## Double-clic on EXE installer

- Tick the box corresponding to the language of the TEXT and SUBTITLES you wish to read in the game: *(Only for non specific language installer)*
```
  Choose your preferred language for TEXTS and SUBTITLES:
    ( ) 中国語（簡体字）
    ( ) 日本語（ひらがな）
    ( ) 한국어
    ( ) Čeština
    ( ) Dansk
    ( ) English
    ( ) Español
    (X) Français
    ( ) German
    ( ) Italiano
    ( ) Magyar
    ( ) Nederlands
    ( ) Polski
    ( ) Português
    ( ) Română
    ( ) Suomi
    ( ) Svenska
```
- Clic on "Next" button *(Only for non specific language installer)*

- Tick the box corresponding to the VOICE language you wish to hear in the game: *(Only for non specific language installer)*
```
  Choose your preferred language for VOICES:
    (X)  Ukrainian
    ( )  Russian
```
- Clic on "Next" button

## Installer show the destination location

- If the destination location corresponds to the installation of your Z.O.N.A. game, click on the "Next" button.
  Alternatively, click the 'Browse' button to define the correct destination location, then click the 'Next' button.

## The installer indicates that the destination location already exists

- That's normal, this is because the installer is installing in an existing game. Confirm by clicking on the 'Yes' button.

## The installer displays the main information about the installation process that will be carried out.

- Clic on 'Install' button.

## The installation python script then starts automatically

## Wait for the translation ending

- If installation succeed then this message will appears.
```
    To play with this translation:
        1. Just launch your game from Steam as usual.
        2. Be sure to select 'Ukrainian/Russian' language in your game's settings.

    /!\ Over the next few days:
        If your translated game no longer launches correctly or if a new update has been made by AGaming+ or NikZ
        You will need to run this script again to update the translation.

    Press Enter to exit...
```
- Press Enter to exit

## Enjoy Ukrainian or Russian voices while having all the texts in your native language!

- Just launch your game from Steam as usual.
- Make sure you select the '**Ukrainian**' or '**Russian**' language in your your game settings according to your choice of VOICES in the installation executable.

## Restoring original subtitles

- There are two methods available:
  - Either select '**English**' in your game settings,
  - Or run the shortcut '**apocalyptic_translatorZ (restore)**' created by the executable in your game directory, and confirm that you want to restore the original translation by typing '**y**'.
```
 Confirm you want to restore all backup binary files (y/n): 
```

# Release notes

- v0.1.0-alpha
  - Initial update
