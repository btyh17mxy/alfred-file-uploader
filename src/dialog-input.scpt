on run argv
    set theResponse to display dialog item 1 of argv default answer "" buttons {"Cancel", "Continue"} default button "Continue"
    if ((button returned of theResponse) is equal to "Cancel") then
        return ""
    else
        return text returned of theResponse
    end if
end run
