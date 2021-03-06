property fileTypes : {¬
	{«class PNGf», "png"}, ¬
	{«class HTML», "html"}, ¬
	{JPEG picture, "jpg"}, ¬
	{«class furl», "file"}}
on getType()
	repeat with aType in fileTypes
		if (first item of first item of (clipboard info)) is equal to (first item of aType) then return aType
	end repeat
        -- log first item of first item of (clipboard info)
	return missing value
end getType
set theType to getType()
theType & ", " & "type"
if theType is not missing value then
	if ((second item of theType) is equal to "file") then
		set filePath to (POSIX path of (the clipboard as «class furl»))
		return filePath
	else
		tell application "Finder"
			set currentPath to container of (path to me) as alias
			set currentPath to POSIX path of currentPath
			set filePath to currentPath & "tmp/"
		end tell
		set fileName to do shell script "date \"+%Y%m%d%H%M%S\" | md5"
		if fileName does not end with (second item of theType) then set fileName to (fileName & "." & (second item of theType as text))
		set filePath to filePath & fileName
		
		try
			set imageFile to (open for access filePath with write permission)
			set eof imageFile to 0
			write (the clipboard as (first item of theType)) to imageFile
			close access imageFile
		on error
			try
				close access imageFile
			end try
			return ""
			
		end try
		return filePath
	end if
else
	return ""
end if
