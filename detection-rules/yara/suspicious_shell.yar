rule Suspicious_Shell_Scripts
{
    meta:
        description = "Detects suspicious shell scripts commonly used in attacks"
        author = "AI SOC Platform"
        date = "2024-01-15"
        modified = "2024-06-01"
        severity = "high"
        mitre_attack = "T1059.004"
        tags = "malware, shell, linux"
        reference = "Internal detection rules for AI SOC Platform"

    strings:
        $shebang_bash = "#!/bin/bash" ascii
        $shebang_sh = "#!/bin/sh" ascii
        $shebang_zsh = "#!/bin/zsh" ascii

        $reverse_shell_1 = "bash -i >& /dev/tcp/" ascii
        $reverse_shell_2 = "nc -e /bin/" ascii
        $reverse_shell_3 = "ncat -e /bin/" ascii
        $reverse_shell_4 = "socat exec:" ascii
        $reverse_shell_5 = "python -c 'import socket" ascii
        $reverse_shell_6 = "perl -e 'use Socket" ascii
        $reverse_shell_7 = "ruby -rsocket -e" ascii
        $reverse_shell_8 = "php -fsockopen" ascii
        $reverse_shell_9 = "mkfifo /tmp/" ascii
        $reverse_shell_10 = "0<&" ascii
        $reverse_shell_11 = "1>&2" ascii
        $reverse_shell_12 = "2>&1" ascii

        $download_exec_1 = "wget " ascii
        $download_exec_2 = "curl " ascii
        $download_exec_3 = "curl -o" ascii
        $download_exec_4 = "wget -O" ascii
        $download_exec_5 = "axel " ascii

        $chmod_exec_1 = "chmod +x" ascii
        $chmod_exec_2 = "chmod 777" ascii
        $chmod_exec_3 = "chmod u+s" ascii
        $chmod_exec_4 = "chown root" ascii

        $privesc_1 = "/etc/passwd" ascii
        $privesc_2 = "/etc/shadow" ascii
        $privesc_3 = "sudo " ascii
        $privesc_4 = "su -c" ascii
        $privesc_5 = "sudoers" ascii
        $privesc_6 = "visudo" ascii

        $persistence_1 = "crontab" ascii
        $persistence_2 = "/etc/cron" ascii
        $persistence_3 = "systemctl" ascii
        $persistence_4 = "service " ascii
        $persistence_5 = ".bashrc" ascii
        $persistence_6 = ".profile" ascii

        $obfuscation_1 = "eval " ascii
        $obfuscation_2 = "base64 -d" ascii
        $obfuscation_3 = "base64 --decode" ascii
        $obfuscation_4 = "xxd -r" ascii
        $obfuscation_5 = "exec " ascii

        $network_1 = "iptables -F" ascii
        $network_2 = "ufw disable" ascii
        $network_3 = "firewall-cmd" ascii
        $network_4 = "netstat" ascii
        $network_5 = "ss -tlnp" ascii

        $cleanup_1 = "history -c" ascii
        $cleanup_2 = "rm -rf " ascii
        $cleanup_3 = "shred " ascii
        $cleanup_4 = "dd if=/dev/zero" ascii
        $cleanup_5 = "> /var/log" ascii

    condition:
        uint32(0) != 0x00000000 and
        filesize < 500KB and
        (
            (1 of ($shebang_*) and 2 of ($reverse_shell_*)) or
            (1 of ($shebang_*) and 2 of ($download_exec_*) and 1 of ($chmod_exec_*)) or
            (3 of ($reverse_shell_*)) or
            (2 of ($privesc_*) and 1 of ($persistence_*)) or
            (2 of ($obfuscation_*) and 1 of ($reverse_shell_*)) or
            (1 of ($network_*) and 1 of ($cleanup_*))
        )
}

rule Suspicious_Bash_Reverse_Shell
{
    meta:
        description = "Detects bash reverse shell patterns"
        author = "AI SOC Platform"
        date = "2024-01-15"
        severity = "critical"
        mitre_attack = "T1059.004"
        tags = "reverse_shell, critical"

    strings:
        $s1 = "bash -i" ascii nocase
        $s2 = "/dev/tcp/" ascii
        $s3 = ">&0" ascii
        $s4 = "1>&0" ascii
        $s5 = "2>&0" ascii
        $s6 = "0<&196" ascii
        $s7 = "exec 5<>/dev/tcp/" ascii
        $s8 = "/dev/udp/" ascii

    condition:
        filesize < 100KB and
        ($s1 and $s2) or
        $s7 or
        ($s1 and ($s3 or $s4 or $s5 or $s6)) or
        $s8
}
