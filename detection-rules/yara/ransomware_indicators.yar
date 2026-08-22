rule Ransomware_Indicators
{
    meta:
        description = "Detects indicators of ransomware activity"
        author = "AI SOC Platform"
        date = "2024-01-15"
        modified = "2024-06-01"
        severity = "critical"
        mitre_attack = "T1486"
        tags = "ransomware, destructive, critical"
        reference = "Detection patterns for common ransomware families"

    strings:
        $ransom_note_1 = "YOUR FILES HAVE BEEN ENCRYPTED" ascii nocase
        $ransom_note_2 = "All your files are encrypted" ascii nocase
        $ransom_note_3 = "Your personal ID" ascii nocase
        $ransom_note_4 = "To decrypt your files" ascii nocase
        $ransom_note_5 = "Bitcoin wallet" ascii nocase
        $ransom_note_6 = "Tor Browser" ascii nocase
        $ransom_note_7 = "Ransomware" ascii nocase
        $ransom_note_8 = "DECRYPT" ascii
        $ransom_note_9 = ".onion" ascii
        $ransom_note_10 = "pay ransom" ascii nocase
        $ransom_note_11 = "RECOVER-YOUR-FILES" ascii nocase
        $ransom_note_12 = "how_to_decrypt" ascii nocase

        $encryption_1 = "AES-256" ascii
        $encryption_2 = "RSA-2048" ascii
        $encryption_3 = "RSA-4096" ascii
        $encryption_4 = "ChaCha20" ascii
        $encryption_5 = "Salsa20" ascii
        $encryption_6 = "XOR" ascii

        $extension_1 = ".locked" ascii
        $extension_2 = ".encrypted" ascii
        $extension_3 = ".crypto" ascii
        $extension_4 = ".cerber" ascii
        $extension_5 = ".zepto" ascii
        $extension_6 = ".cerber3" ascii
        $extension_7 = ".locky" ascii
        $extension_8 = ".wncry" ascii
        $extension_9 = ".wcry" ascii
        $extension_10 = ".crypt" ascii
        $extension_11 = ".locked" ascii
        $extension_12 = ".aesir" ascii
        $extension_13 = ".zzzzz" ascii
        $extension_14 = ".micro" ascii
        $extension_15 = ".xxx" ascii
        $extension_16 = ".ttt" ascii
        $extension_17 = ".ecc" ascii
        $extension_18 = ".ezz" ascii

        $vss_delete_1 = "vssadmin delete shadows" ascii nocase
        $vss_delete_2 = "wmic shadowcopy delete" ascii nocase
        $vss_delete_3 = "bcdedit /set {default} recoveryenabled no" ascii nocase
        $vss_delete_4 = "bcdedit /set {default} bootstatuspolicy ignoreallfailures" ascii nocase
        $vss_delete_5 = "wbadmin delete catalog" ascii nocase
        $vss_delete_6 = "wbadmin delete systemstatebackup" ascii nocase

        $crypto_wipe_1 = "cipher /w:" ascii nocase
        $crypto_wipe_2 = "format /y" ascii nocase

    condition:
        filesize < 5MB and
        (
            (3 of ($ransom_note_*)) or
            (2 of ($ransom_note_*) and 2 of ($extension_*)) or
            (2 of ($vss_delete_*)) or
            (1 of ($vss_delete_*) and 1 of ($ransom_note_*)) or
            (2 of ($extension_*) and 1 of ($encryption_*))
        )
}

rule Ransomware_Note_Creation
{
    meta:
        description = "Detects creation of common ransomware note files"
        author = "AI SOC Platform"
        date = "2024-01-15"
        severity = "critical"
        mitre_attack = "T1486"
        tags = "ransomware, file_creation"

    strings:
        $note1 = "README_LOCKED.txt" ascii nocase
        $note2 = "DECRYPT_INSTRUCTIONS.html" ascii nocase
        $note3 = "HOW_TO_DECRYPT.txt" ascii nocase
        $note4 = "RECOVER-YOUR-FILES.txt" ascii nocase
        $note5 = "RESTORE_FILES.txt" ascii nocase
        $note6 = "DECRYPT.txt" ascii nocase
        $note7 = "HELP_DECRYPT.txt" ascii nocase
        $note8 = "RECOVER_FILES.html" ascii nocase
        $note9 = "HOW_TO_RECOVER.txt" ascii nocase
        $note10 = "DECRYPT-FILES.txt" ascii nocase

    condition:
        filesize < 500KB and
        any of them
}
