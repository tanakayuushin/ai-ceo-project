' Soundcore -> Notion silent launcher
Dim WShell
Set WShell = CreateObject(
"
WScript.Shell
"
)
WShell.Run "python ""C:\Users\tsube\OneDrive\??????\ai-ceo-project\tools\notion-sync\soundcore_to_notion.py""", 0, False
