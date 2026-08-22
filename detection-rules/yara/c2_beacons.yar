rule C2_Beacons_Metasploit
{
    meta:
        description = "Detects Metasploit meterpreter and stager shellcode patterns"
        author = "AI SOC Platform"
        date = "2024-01-15"
        modified = "2024-06-01"
        severity = "critical"
        mitre_attack = "T1105"
        tags = "c2, metasploit, shellcode, meterpreter"
        reference = "Common meterpreter and stager byte patterns"

    strings:
        $metas_1 = { FC E8 89 00 00 00 60 89 E5 31 D2 64 8B 52 30 }
        $metas_2 = { FC E8 82 00 00 00 60 89 E5 31 C0 64 8B 50 30 }
        $metas_3 = { 60 31 D2 64 8B 52 30 8B 52 0C 8B 52 14 }
        $metas_4 = { 60 31 DB 64 8B 43 30 8B 40 0C 8B 70 14 }
        $metas_5 = { 48 89 C4 48 83 EC 20 48 31 C9 48 89 CA }
        $meterpreter_rev_tcp = { 6A 10 56 57 68 99 A5 74 61 FF D5 }
        $meterpreter_rev_http = { 68 F0 B5 A2 56 FF D5 }

    condition:
        any of them
}

rule C2_Beacons_CobaltStrike
{
    meta:
        description = "Detects Cobalt Strike beacon patterns"
        author = "AI SOC Platform"
        date = "2024-01-15"
        modified = "2024-06-01"
        severity = "critical"
        mitre_attack = "T1105"
        tags = "c2, cobalt_strike, beacon"
        reference = "Cobalt Strike signature patterns"

    strings:
        $cs_beacon_1 = { 48 89 5C 24 08 48 89 6C 24 10 48 89 74 24 18 57 }
        $cs_beacon_2 = { 4C 8B 53 08 45 8B 0A 45 8B 5A 04 4D 8D 52 08 }
        $cs_beacon_3 = { 89 44 24 3C 8B 44 24 3C 8B 44 24 38 }
        $cs_config = { 00 01 00 01 00 02 ?? ?? 00 02 00 01 00 02 ?? ?? }
        $cs_pipe = { 5C 00 70 00 69 00 70 00 65 00 5C 00 }

        $cs_keyword_1 = "beacon.dll" ascii nocase
        $cs_keyword_2 = "beacon.exe" ascii nocase
        $cs_keyword_3 = "cobaltstrike" ascii nocase

    condition:
        any of ($cs_beacon_*) or
        ($cs_config and $cs_pipe) or
        any of ($cs_keyword_*)
}

rule C2_Beacons_Generic_HTTP
{
    meta:
        description = "Detects generic HTTP C2 beaconing patterns"
        author = "AI SOC Platform"
        date = "2024-01-15"
        severity = "high"
        mitre_attack = "T1071.001"
        tags = "c2, http, beacon"

    strings:
        $http_post_ua = "POST" ascii
        $ua_chrome_old = "User-Agent: Mozilla/4.0 (compatible; MSIE " ascii
        $ua_chrome_old2 = "User-Agent: Mozilla/5.0 (compatible; MSIE " ascii
        $ua_chrome_old3 = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" ascii

        $beacon_uri_1 = "/gate.php" ascii
        $beacon_uri_2 = "/check.php" ascii
        $beacon_uri_3 = "/submit.php" ascii
        $beacon_uri_4 = "/login.php" ascii
        $beacon_uri_5 = "/admin.php" ascii
        $beacon_uri_6 = "/cmd.php" ascii
        $beacon_uri_7 = "/shell.php" ascii
        $beacon_uri_8 = "/backdoor.php" ascii
        $beacon_uri_9 = "/upload.php" ascii
        $beacon_uri_10 = "/api/connect" ascii

        $c2_headers_1 = "X-C2:" ascii
        $c2_headers_2 = "X-Session:" ascii
        $c2_headers_3 = "X-ID:" ascii
        $c2_headers_4 = "Cookie: session=" ascii

    condition:
        $http_post_ua and
        (
            ($ua_chrome_old and 2 of ($beacon_uri_*)) or
            ($ua_chrome_old2 and 2 of ($beacon_uri_*)) or
            any of ($c2_headers_*)
        )
}

rule C2_Beacons_DNS
{
    meta:
        description = "Detects DNS-based C2 communication patterns"
        author = "AI SOC Platform"
        date = "2024-01-15"
        severity = "high"
        mitre_attack = "T1071.004"
        tags = "c2, dns, tunnel"

    strings:
        $dns_txt_1 = "dns_txt_query" ascii
        $dns_txt_2 = "TXT" ascii
        $dns_txt_3 = "nslookup -type=TXT" ascii

        $dns_tunnel_1 = "dnscat" ascii nocase
        $dns_tunnel_2 = "iodine" ascii nocase
        $dns_tunnel_3 = "dns2tcp" ascii nocase

        $base32_encoded = /[A-Z2-7]{16,64}=*/ ascii
        $hex_encoded = /[0-9a-f]{16,64}/ ascii

    condition:
        any of ($dns_tunnel_*) or
        (2 of ($dns_txt_*) and any of ($base32_encoded, $hex_encoded))
}

rule C2_Beacons_Malleable_C2
{
    meta:
        description = "Detects Cobalt Strike Malleable C2 profile artifacts"
        author = "AI SOC Platform"
        date = "2024-01-15"
        severity = "high"
        mitre_attack = "T1071.001"
        tags = "c2, cobalt_strike, malleable"

    strings:
        $malleable_1 = "Accept: */*" ascii
        $malleable_2 = "Content-Type: application/x-www-form-urlencoded" ascii
        $malleable_3 = "Connection: Keep-Alive" ascii
        $malleable_4 = "Cache-Control: no-cache" ascii

        $cs_stager_1 = "__VIEWSTATE" ascii
        $cs_stager_2 = "__VIEWSTATEGENERATOR" ascii
        $cs_stager_3 = "__EVENTVALIDATION" ascii
        $cs_stager_4 = "Referer: http://" ascii

        $java_payload = { 50 4B 03 04 }
        $jndi_lookup = "jndi:ldap://" ascii

    condition:
        3 of ($malleable_*) and any of ($cs_stager_*) or
        ($java_payload at 0 and $jndi_lookup)
}
