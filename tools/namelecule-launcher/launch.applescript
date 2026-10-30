on run
    try
        set resourcesPath to (POSIX path of (path to me)) & "Contents/Resources/"
        do shell script "/usr/bin/python3 -B " & quoted form of (resourcesPath & "launcher.py") & " --config " & quoted form of (resourcesPath & "project.json")
    on error errorMessage
        display dialog "Το Namelecule δεν άνοιξε." & return & return & errorMessage with title "Namelecule" buttons {"Εντάξει"} default button 1 with icon caution
    end try
end run
