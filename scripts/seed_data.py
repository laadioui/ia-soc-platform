#!/usr/bin/env python3
"""
Seed the AI SOC Platform database with demo data.

Usage:
    python scripts/seed_data.py              # uses SQLite in-memory for quick test
    python scripts/seed_data.py --postgres   # uses DATABASE_URL from env
"""
from __future__ import annotations

import argparse
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "collector-service"))

from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User
from app.models.event import SecurityEvent
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.detection_rule import DetectionRule
from app.models.ioc import IOC
from app.models.mitre import MITRETechnique
from app.models.threat_intelligence import ThreatIntelligence

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://soc_admin:soc_secret_password_2026@localhost:5432/ai_soc_platform",
)


# ---------------------------------------------------------------------------
# Data definitions
# ---------------------------------------------------------------------------

USERS = [
    {"email": "admin@soc.local", "username": "admin", "full_name": "SOC Admin", "password": "Admin@2026!"},
    {"email": "manager@soc.local", "username": "manager", "full_name": "SOC Manager", "password": "Manager@2026!"},
    {"email": "analyst@soc.local", "username": "analyst", "full_name": "SOC Analyst", "password": "Analyst@2026!"},
    {"email": "viewer@soc.local", "username": "viewer", "full_name": "SOC Viewer", "password": "Viewer@2026!"},
]

DETECTION_RULES = [
    {
        "rule_id": "BRUTE-FORCE-001",
        "name": "Brute Force Login Attempt",
        "description": "Detects more than 10 failed login attempts from a single IP within 5 minutes.",
        "rule_type": "threshold",
        "severity": "high",
        "category": "authentication",
        "condition": {"field": "action", "operator": "equals", "value": "login_failed"},
        "mitre_technique": "T1110",
        "mitre_tactic": "Credential Access",
        "threshold": 10,
        "time_window_seconds": 300,
    },
    {
        "rule_id": "PORT-SCAN-001",
        "name": "Port Scanning Activity",
        "description": "Detects access to more than 20 distinct ports from a single IP within 60 seconds.",
        "rule_type": "threshold",
        "severity": "high",
        "category": "discovery",
        "condition": {"field": "destination_port", "operator": "countDistinct", "threshold": 20},
        "mitre_technique": "T1046",
        "mitre_tactic": "Discovery",
        "threshold": 20,
        "time_window_seconds": 60,
    },
    {
        "rule_id": "PRIV-ESC-001",
        "name": "Privilege Escalation Attempt",
        "description": "Detects sudo, role assignment, or group modification events indicating privilege escalation.",
        "rule_type": "pattern",
        "severity": "critical",
        "category": "privilege_escalation",
        "condition": {"field": "action", "operator": "in", "value": ["sudo", "role_added", "privilege_escalation"]},
        "mitre_technique": "T1548",
        "mitre_tactic": "Privilege Escalation",
    },
    {
        "rule_id": "LAT-MOVE-001",
        "name": "Lateral Movement Detected",
        "description": "Detects SMB/RDP/SSH connections to multiple internal hosts from a single source.",
        "rule_type": "correlation",
        "severity": "critical",
        "category": "lateral_movement",
        "condition": {"field": "action", "operator": "in", "value": ["smb_connection", "rdp_connection", "ssh_connection"]},
        "mitre_technique": "T1021",
        "mitre_tactic": "Lateral Movement",
    },
    {
        "rule_id": "C2-BEACON-001",
        "name": "Command and Control Beacon",
        "description": "Detects periodic outbound connections characteristic of C2 beaconing.",
        "rule_type": "anomaly",
        "severity": "critical",
        "category": "command_and_control",
        "condition": {"field": "outbound_connections", "operator": "periodicPattern", "interval_seconds": 60},
        "mitre_technique": "T1071",
        "mitre_tactic": "Command and Control",
    },
]

MITRE_TECHNIQUES = [
    {"technique_id": "T1110", "name": "Brute Force", "tactic": "Credential Access", "description": "Adversaries may use brute force techniques to gain access to accounts.", "platforms": ["Linux", "Windows", "macOS"]},
    {"technique_id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery", "description": "Adversaries may attempt to get a listing of services running on remote hosts.", "platforms": ["Linux", "Windows", "macOS"]},
    {"technique_id": "T1548", "name": "Abuse Elevation Control Mechanism", "tactic": "Privilege Escalation", "description": "Adversaries may circumvent mechanisms designed to control elevated privileges.", "platforms": ["Linux", "Windows", "macOS"]},
    {"technique_id": "T1021", "name": "Remote Services", "tactic": "Lateral Movement", "description": "Adversaries may use valid accounts to log into a service for remote access.", "platforms": ["Linux", "Windows"]},
    {"technique_id": "T1071", "name": "Application Layer Protocol", "tactic": "Command and Control", "description": "Adversaries may communicate using application layer protocols to avoid detection.", "platforms": ["Linux", "Windows", "macOS"]},
    {"technique_id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution", "description": "Adversaries may abuse command and script interpreters to execute commands.", "platforms": ["Linux", "Windows", "macOS"]},
    {"technique_id": "T1053", "name": "Scheduled Task/Job", "tactic": "Execution", "description": "Adversaries may abuse task scheduling functionality to facilitate execution.", "platforms": ["Linux", "Windows"]},
    {"technique_id": "T1082", "name": "System Information Discovery", "tactic": "Discovery", "description": "An adversary may attempt to get detailed information about the operating system.", "platforms": ["Linux", "Windows", "macOS"]},
    {"technique_id": "T1005", "name": "Data from Local System", "tactic": "Collection", "description": "Adversaries may search local system sources to find files of interest.", "platforms": ["Linux", "Windows", "macOS"]},
    {"technique_id": "T1567", "name": "Exfiltration Over Web Service", "tactic": "Exfiltration", "description": "Adversaries may use an existing, legitimate external Web service to exfiltrate data.", "platforms": ["Linux", "Windows", "macOS"]},
]

IOCS = [
    {"ioc_type": "ip", "ioc_value": "192.168.1.100", "severity": "high", "confidence": 0.85, "description": "Known brute force source IP", "source": "internal-siem", "threat_type": "brute_force"},
    {"ioc_type": "domain", "ioc_value": "evil-c2.example.com", "severity": "critical", "confidence": 0.95, "description": "C2 domain observed in multiple incidents", "source": "threat-feed", "threat_type": "c2"},
    {"ioc_type": "hash", "ioc_value": "d41d8cd98f00b204e9800998ecf8427e", "severity": "critical", "confidence": 0.90, "description": "SHA256 of known malware sample", "source": "virustotal", "threat_type": "malware"},
    {"ioc_type": "url", "ioc_value": "https://phishing.example.com/login", "severity": "high", "confidence": 0.80, "description": "Phishing URL targeting credential theft", "source": "phish-tank", "threat_type": "phishing"},
    {"ioc_type": "email", "ioc_value": "attacker@protonmail.com", "severity": "medium", "confidence": 0.70, "description": "Suspicious email used in social engineering", "source": "abuse-report", "threat_type": "social_engineering"},
]

THREAT_INTEL = [
    {
        "indicator_type": "ip",
        "indicator_value": "192.168.1.100",
        "threat_type": "botnet",
        "confidence": 0.88,
        "severity": "high",
        "description": "Associated with Mirai botnet variant",
        "source": "AlienVault OTX",
        "tags": ["botnet", "iot", "mirai"],
        "related_mitre": ["T1110", "T1046"],
        "tlp": "amber",
    },
    {
        "indicator_type": "domain",
        "indicator_value": "evil-c2.example.com",
        "threat_type": "apt",
        "confidence": 0.92,
        "severity": "critical",
        "description": "C2 infrastructure linked to APT29",
        "source": "MISP Galaxy",
        "tags": ["apt29", "cozy-bear", "c2"],
        "related_mitre": ["T1071", "T1021"],
        "tlp": "red",
    },
    {
        "indicator_type": "hash",
        "indicator_value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "threat_type": "ransomware",
        "confidence": 0.95,
        "severity": "critical",
        "description": "LockBit 3.0 ransomware sample hash",
        "source": "CISA Advisory",
        "tags": ["ransomware", "lockbit", "extortion"],
        "related_mitre": ["T1059", "T1005", "T1567"],
        "tlp": "white",
    },
]

# ---------------------------------------------------------------------------
# Sample events
# ---------------------------------------------------------------------------

EVENT_SOURCES = [
    ("linux-syslog", "linux", "authentication"),
    ("windows-eventlog", "windows", "process"),
    ("nginx", "nginx", "web"),
    ("docker", "container", "runtime"),
    ("aws-cloudtrail", "aws-cloudtrail", "cloud"),
    ("kubernetes", "kubernetes", "orchestrator"),
    ("firewall", "firewall", "network"),
    ("ids-suricata", "ids", "intrusion"),
]

ACTIONS = [
    "login", "login_failed", "logout",
    "file_access", "file_create", "file_delete",
    "process_created", "process_terminated",
    "sudo", "sudo_command",
    "connection_attempt", "connection_established",
    "dns_query", "http_request",
    "service_start", "service_stop",
    "policy_change", "audit_log_cleared",
]

SEVERITIES = ["info", "low", "medium", "high", "critical"]

IPS = [f"192.168.1.{i}" for i in range(1, 21)] + [f"10.0.0.{i}" for i in range(1, 21)]
HOSTNAMES = [f"server-{i:02d}" for i in range(1, 11)] + [f"endpoint-{i:02d}" for i in range(1, 6)]
USERS_LIST = ["admin", "root", "analyst1", "analyst2", "viewer1", "svc-account", "backup-user"]


def _random_event(seed: int) -> dict:
    """Deterministic pseudo-random event from seed."""
    s = seed
    def _pick(lst):
        nonlocal s
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        return lst[s % len(lst)]

    src, src_type, category = _pick(EVENT_SOURCES)
    now = datetime.now(timezone.utc) - timedelta(minutes=seed % 60)

    return {
        "event_id": f"evt-demo-{seed:04d}",
        "timestamp": now,
        "source": src,
        "source_type": src_type,
        "category": category,
        "action": _pick(ACTIONS),
        "severity": _pick(SEVERITIES),
        "source_ip": _pick(IPS),
        "destination_ip": _pick(IPS),
        "destination_port": (seed * 7) % 65535 + 1,
        "hostname": _pick(HOSTNAMES),
        "user_name": _pick(USERS_LIST),
        "application": _pick(["sshd", "nginx", "sudo", "bash", "powershell", "docker"]),
        "is_alert": seed % 10 == 0,
        "processed": True,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def seed(url: str):
    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        # ── Users ────────────────────────────────────────────────────────
        print("[*] Seeding users...")
        for u in USERS:
            user = User(
                id=uuid.uuid4(),
                email=u["email"],
                username=u["username"],
                full_name=u["full_name"],
                hashed_password=hash_password(u["password"]),
                is_active=True,
                is_verified=True,
            )
            session.add(user)
        await session.commit()
        print(f"    Created {len(USERS)} users")

        # ── Detection Rules ──────────────────────────────────────────────
        print("[*] Seeding detection rules...")
        for r in DETECTION_RULES:
            rule = DetectionRule(
                id=uuid.uuid4(),
                **r,
                is_active=True,
                version=1,
                author="SOC Team",
            )
            session.add(rule)
        await session.commit()
        print(f"    Created {len(DETECTION_RULES)} detection rules")

        # ── MITRE Techniques ────────────────────────────────────────────
        print("[*] Seeding MITRE techniques...")
        for t in MITRE_TECHNIQUES:
            technique = MITRETechnique(
                id=uuid.uuid4(),
                **t,
            )
            session.add(technique)
        await session.commit()
        print(f"    Created {len(MITRE_TECHNIQUES)} MITRE techniques")

        # ── IOCs ────────────────────────────────────────────────────────
        print("[*] Seeding IOCs...")
        for i in IOCS:
            ioc = IOC(
                id=uuid.uuid4(),
                **i,
                is_active=True,
            )
            session.add(ioc)
        await session.commit()
        print(f"    Created {len(IOCS)} IOCs")

        # ── Threat Intelligence ─────────────────────────────────────────
        print("[*] Seeding threat intelligence...")
        for ti in THREAT_INTEL:
            record = ThreatIntelligence(
                id=uuid.uuid4(),
                **ti,
            )
            session.add(record)
        await session.commit()
        print(f"    Created {len(THREAT_INTEL)} threat intelligence records")

        # ── Security Events ─────────────────────────────────────────────
        print("[*] Seeding 50 sample security events...")
        for i in range(1, 51):
            data = _random_event(i)
            event = SecurityEvent(id=uuid.uuid4(), **data)
            session.add(event)
        await session.commit()
        print("    Created 50 security events")

    await engine.dispose()
    print("[✓] Seed completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Seed AI SOC Platform database")
    parser.add_argument("--postgres", action="store_true", help="Use PostgreSQL (DATABASE_URL)")
    parser.add_argument("--url", type=str, default=None, help="Override DATABASE_URL")
    args = parser.parse_args()

    if args.url:
        url = args.url
    elif args.postgres:
        url = DATABASE_URL
    else:
        url = "sqlite+aiosqlite:///./soc_seed.db"
        print(f"[*] Using local SQLite: {url}")

    asyncio.run(seed(url))


if __name__ == "__main__":
    main()
