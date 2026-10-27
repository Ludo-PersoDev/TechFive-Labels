[Setup]
AppName=TechFive Labels
AppVersion=1.0.1
DefaultDirName={autopf}\TechFiveLabels
DefaultGroupName=TechFive Labels
OutputDir=installer_output
OutputBaseFilename=TechFiveLabels_Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=data\favicon.ico
UninstallDisplayIcon={app}\TechFiveLabels.exe

[Files]
; On prend tout le dossier généré par PyInstaller et on l'inclut
Source: "dist\TechFiveLabels\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\TechFive Labels"; Filename: "{app}\TechFiveLabels.exe"
Name: "{autodesktop}\TechFive Labels"; Filename: "{app}\TechFiveLabels.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked