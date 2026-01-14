; NSIS script for astronrpa protocol registration

!macro customInstall
    ; Register astronrpa protocol in HKEY_CURRENT_USER (does not require admin)
    WriteRegStr HKCU "Software\Classes\astronrpa" "" "URL:astronrpa Protocol"
    WriteRegStr HKCU "Software\Classes\astronrpa" "URL Protocol" ""
    WriteRegStr HKCU "Software\Classes\astronrpa\shell\open\command" "" '"$INSTDIR\${APP_EXECUTABLE_FILENAME}" "%1"'
!macroend

!macro customUnInstall
    ; Unregister from HKEY_CURRENT_USER
    DeleteRegKey HKCU "Software\Classes\astronrpa"
!macroend
