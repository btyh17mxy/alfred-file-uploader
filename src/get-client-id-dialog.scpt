set theResponse to display dialog "imgur client id" default answer "" buttons {"Cancel", "Continue"} default button "Continue"
if ((button returned of theResponse) is equal to "Cancel") then
	return ""
else
	return text returned of theResponse
end if
