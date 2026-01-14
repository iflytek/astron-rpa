; NSIS script for astronrpa protocol registration

!macro customInstall
    ; Register astronrpa protocol in HKEY_CURRENT_USER (does not require admin)
    WriteRegStr HKCU "Software\Classes\AstronRPA" "" "URL:astronrpa Protocol"
    WriteRegStr HKCU "Software\Classes\AstronRPA" "URL Protocol" ""
    WriteRegStr HKCU "Software\Classes\AstronRPA\shell\open\command" "" '"$INSTDIR\${APP_EXECUTABLE_FILENAME}" "%1"'
!macroend

!macro customUnInstall
    ; Unregister from HKEY_CURRENT_USER
    DeleteRegKey HKCU "Software\Classes\AstronRPA"
!macroend
