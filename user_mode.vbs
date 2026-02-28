Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the script's directory
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Kill any existing Python processes first (hidden, wait for completion)
WshShell.Run "cmd /c taskkill /F /IM python.exe /T 2>nul", 0, True

' Wait for processes to fully terminate
WScript.Sleep 2000

' Start Flask using the hidden batch file
WshShell.Run "cmd /c cd /d """ & scriptDir & """ && """ & scriptDir & "\user_mode_hidden.bat""", 0, False

' Wait for server to start
WScript.Sleep 4000

' Open default browser
WshShell.Run "cmd /c start """" ""http://127.0.0.1:5000""", 0, False
