Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Build the command
pythonPath = scriptDir & "\env\Scripts\python.exe"
scriptPath = scriptDir & "\src\gui_main.py"

' Run without showing window (0 = hidden, True = wait for completion set to False)
objShell.Run """" & pythonPath & """ """ & scriptPath & """", 0, False
