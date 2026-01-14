!macro customInstall
    ; 尝试写入 HKCR (需要管理员权限，对所有用户生效)
    ClearErrors
    WriteRegStr HKCR "astronrpa" "" "URL:astronrpa Protocol"
    WriteRegStr HKCR "astronrpa" "URL Protocol" ""
    WriteRegStr HKCR "astronrpa" "FriendlyTypeName" "星辰RPA"
    WriteRegStr HKCR "astronrpa\Application" "ApplicationName" "星辰RPA"
    WriteRegStr HKCR "astronrpa\shell\open\command" "" '"$INSTDIR\${APP_EXECUTABLE_FILENAME}" -- "%1"'
    
    ; 如果 HKCR 写入失败（非管理员），则写入 HKCU (仅对当前用户生效)
    ${If} ${Errors}
        ClearErrors
        WriteRegStr HKCU "Software\Classes\astronrpa" "" "URL:astronrpa Protocol"
        WriteRegStr HKCU "Software\Classes\astronrpa" "URL Protocol" ""
        WriteRegStr HKCU "Software\Classes\astronrpa" "FriendlyTypeName" "星辰RPA"
        WriteRegStr HKCU "Software\Classes\astronrpa\Application" "ApplicationName" "星辰RPA"
        WriteRegStr HKCU "Software\Classes\astronrpa\shell\open\command" "" '"$INSTDIR\${APP_EXECUTABLE_FILENAME}" -- "%1"'
    ${EndIf}
!macroend

!macro customUnInstall
    ; 尝试从 HKCR 删除
    ClearErrors
    DeleteRegKey HKCR "astronrpa"
    
    ; 同时从 HKCU 删除（如果存在）
    ClearErrors
    DeleteRegKey HKCU "Software\Classes\astronrpa"
!macroend
