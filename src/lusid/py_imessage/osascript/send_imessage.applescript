on run {targetBuddyPhone, targetMessage, createContact}
    -- Handle contact creation (only if createContact is true)
    if createContact is "true" then
        tell application "Contacts"
            set contactName to "lusid-" & targetBuddyPhone
            
            -- Check if contact already exists
            set existingContacts to every person whose name is contactName
            
            -- Only create contact if it doesn't exist
            if (count of existingContacts) is 0 then
                set newPerson to make new person with properties {first name:contactName}
                make new phone at newPerson with properties {label:"iMessage", value:targetBuddyPhone}
                save
            end if
        end tell
    end if
    
    -- Send iMessage
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy targetBuddyPhone of targetService
        send targetMessage to targetBuddy
    end tell
end run
