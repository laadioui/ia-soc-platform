"""Automatic demo data seeding for public deployments.

Activated by SEED_DEMO_DATA=true (see render.yaml). Because free hosting tiers
have ephemeral disks, the database is re-seeded at startup whenever the events
table is empty, so the public demo always shows a populated SOC.

All data is deterministic (seeded LCG) so screenshots and tests are stable.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.alert import Alert
from app.models.detection_rule import DetectionRule
from app.models.event import SecurityEvent
from app.models.incident import Incident, IncidentEvent, IncidentIOC
from app.models.ioc import IOC
from app.models.mitre import MITRETechnique
from app.models.threat_intelligence import ThreatIntelligence
from app.models.user import User

logger = structlog.get_logger()

USERS = [
    {"email": "socadmin@soc.local", "username": "socadmin", "full_name": "SOC Administrator", "password": "AdminPass123!"},
    {"email": "admin@soc.local", "username": "admin", "full_name": "SOC Admin", "password": "Admin@2026!"},
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
        "condition": {
            "field": "action",
            "operator": "in",
            "value": ["smb_connection", "rdp_connection", "ssh_connection"],
        },
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
    {"ioc_type": "ip", "ioc_value": "185.220.101.34", "severity": "high", "confidence": 0.85, "description": "Known brute force source IP (Tor exit node)", "source": "internal-siem", "threat_type": "brute_force"},
    {"ioc_type": "domain", "ioc_value": "evil-c2.example.com", "severity": "critical", "confidence": 0.95, "description": "C2 domain observed in multiple incidents", "source": "threat-feed", "threat_type": "c2"},
    {"ioc_type": "hash", "ioc_value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "severity": "critical", "confidence": 0.90, "description": "SHA256 of known ransomware sample", "source": "virustotal", "threat_type": "malware"},
    {"ioc_type": "url", "ioc_value": "https://phishing.example.com/login", "severity": "high", "confidence": 0.80, "description": "Phishing URL targeting credential theft", "source": "phish-tank", "threat_type": "phishing"},
    {"ioc_type": "email", "ioc_value": "attacker@protonmail.com", "severity": "medium", "confidence": 0.70, "description": "Suspicious email used in social engineering", "source": "abuse-report", "threat_type": "social_engineering"},
]

THREAT_INTEL = [
    {"indicator_type": "ip", "indicator_value": "185.220.101.34", "threat_type": "botnet", "confidence": 0.88, "severity": "high", "description": "Associated with Mirai botnet variant", "source": "AlienVault OTX", "tags": ["botnet", "iot", "mirai"], "related_mitre": ["T1110", "T1046"], "tlp": "amber"},
    {"indicator_type": "domain", "indicator_value": "evil-c2.example.com", "threat_type": "apt", "confidence": 0.92, "severity": "critical", "description": "C2 infrastructure linked to APT29", "source": "MISP Galaxy", "tags": ["apt29", "cozy-bear", "c2"], "related_mitre": ["T1071", "T1021"], "tlp": "red"},
    {"indicator_type": "hash", "indicator_value": "44d88612fea8a8f36de82e1278abb02f", "threat_type": "ransomware", "confidence": 0.95, "severity": "critical", "description": "LockBit 3.0 ransomware sample hash", "source": "CISA Advisory", "tags": ["ransomware", "lockbit", "extortion"], "related_mitre": ["T1059", "T1005", "T1567"], "tlp": "white"},
    {"indicator_type": "ip", "indicator_value": "45.155.205.233", "threat_type": "scanner", "confidence": 0.75, "severity": "medium", "description": "Mass scanner targeting RDP and SSH endpoints", "source": "AbuseIPDB", "tags": ["scanner", "rdp", "ssh"], "related_mitre": ["T1046"], "tlp": "green"},
    {"indicator_type": "domain", "indicator_value": "cdn-metrics-tracker.net", "threat_type": "c2", "confidence": 0.81, "severity": "high", "description": "Fake CDN domain used for beaconing", "source": "Recorded Future", "tags": ["c2", "beacon", "cdn"], "related_mitre": ["T1071", "T1567"], "tlp": "amber"},
]

EVENT_SOURCES = [
    ("linux-syslog", "server", "authentication"),
    ("windows-eventlog", "server", "process"),
    ("nginx", "application", "web"),
    ("docker", "container", "runtime"),
    ("aws-cloudtrail", "cloud", "cloud"),
    ("kubernetes", "orchestrator", "orchestrator"),
    ("firewall", "network", "network"),
    ("ids-suricata", "intrusion", "intrusion"),
]

ACTIONS = [
    "login", "login_failed", "logout", "file_access", "file_create", "file_delete",
    "process_created", "process_terminated", "sudo", "sudo_command",
    "connection_attempt", "connection_established", "dns_query", "http_request",
    "service_start", "service_stop", "policy_change", "audit_log_cleared",
]

SEVERITIES = ["info", "low", "medium", "high", "critical"]

IPS = [f"192.168.1.{i}" for i in range(1, 21)] + [f"10.0.0.{i}" for i in range(1, 21)] + ["185.220.101.34", "45.155.205.233"]
HOSTNAMES = [f"server-{i:02d}" for i in range(1, 11)] + [f"endpoint-{i:02d}" for i in range(1, 6)]
USERS_LIST = ["admin", "root", "analyst1", "analyst2", "viewer1", "svc-account", "backup-user"]


class _LCG:
    """Deterministic pseudo-random generator (stable across restarts)."""

    def __init__(self, seed: int = 42):
        self._s = seed

    def pick(self, lst):
        self._s = (self._s * 1103515245 + 12345) & 0x7FFFFFFF
        return lst[self._s % len(lst)]

    def below(self, n: int) -> int:
        self._s = (self._s * 1103515245 + 12345) & 0x7FFFFFFF
        return self._s % n


def _event_data(rng: _LCG, index: int) -> dict:
    src, src_type, category = rng.pick(EVENT_SOURCES)
    now = datetime.now(UTC) - timedelta(minutes=index % 240)
    return {
        "event_id": f"evt-demo-{index:04d}",
        "timestamp": now,
        "source": src,
        "source_type": src_type,
        "category": category,
        "action": rng.pick(ACTIONS),
        "severity": rng.pick(SEVERITIES),
        "source_ip": rng.pick(IPS),
        "destination_ip": rng.pick(IPS),
        "destination_port": rng.below(65534) + 1,
        "hostname": rng.pick(HOSTNAMES),
        "user_name": rng.pick(USERS_LIST),
        "application": rng.pick(["sshd", "nginx", "sudo", "bash", "powershell", "docker"]),
        "is_alert": index % 10 == 0,
        "processed": True,
    }


def _alert_defs(now: datetime) -> list[dict]:
    m = lambda minutes: now - timedelta(minutes=minutes)  # noqa: E731
    return [
        {
            "alert_id": "ALT-1001", "title": "Brute Force Login Attempt", "severity": "critical", "status": "new",
            "source": "linux-syslog", "rule_id": "BRUTE-FORCE-001", "rule_name": "Brute Force Login Attempt",
            "event_count": 28, "first_seen": m(18), "last_seen": m(3), "risk_score": 0.92,
            "description": "28 failed SSH login attempts from 185.220.101.34 targeting user 'admin' within 5 minutes.",
        },
        {
            "alert_id": "ALT-1002", "title": "Port Scanning Activity", "severity": "high", "status": "new",
            "source": "ids-suricata", "rule_id": "PORT-SCAN-001", "rule_name": "Port Scanning Activity",
            "event_count": 143, "first_seen": m(55), "last_seen": m(41), "risk_score": 0.78,
            "description": "Sequential scan of 143 ports on subnet 10.0.0.0/24 from 45.155.205.233.",
        },
        {
            "alert_id": "ALT-1003", "title": "Privilege Escalation via Sudo", "severity": "critical", "status": "investigating",
            "source": "linux-syslog", "rule_id": "PRIV-ESC-001", "rule_name": "Privilege Escalation Attempt",
            "event_count": 4, "first_seen": m(120), "last_seen": m(115), "risk_score": 0.87,
            "description": "User 'svc-account' executed sudo su - on server-03 (10.0.0.3) outside maintenance window.",
        },
        {
            "alert_id": "ALT-1004", "title": "C2 Beacon Detected", "severity": "critical", "status": "investigating",
            "source": "firewall", "rule_id": "C2-BEACON-001", "rule_name": "Command and Control Beacon",
            "event_count": 62, "first_seen": m(360), "last_seen": m(6), "risk_score": 0.95,
            "description": "Periodic HTTPS beacons every 60s from endpoint-02 to evil-c2.example.com (185.220.101.34).",
        },
        {
            "alert_id": "ALT-1005", "title": "Lateral Movement via SSH", "severity": "high", "status": "acknowledged",
            "source": "linux-syslog", "rule_id": "LAT-MOVE-001", "rule_name": "Lateral Movement Detected",
            "event_count": 9, "first_seen": m(200), "last_seen": m(180), "risk_score": 0.74,
            "description": "Compromised account 'backup-user' opened SSH sessions to 4 distinct internal hosts.",
        },
        {
            "alert_id": "ALT-1006", "title": "Impossible Travel Login", "severity": "medium", "status": "acknowledged",
            "source": "aws-cloudtrail", "rule_id": "GEO-001", "rule_name": "Impossible Travel",
            "event_count": 2, "first_seen": m(400), "last_seen": m(398), "risk_score": 0.55,
            "description": "Console login for 'analyst2' from Paris then Singapore within 22 minutes.",
        },
        {
            "alert_id": "ALT-1007", "title": "Ransomware Hash Match", "severity": "critical", "status": "new",
            "source": "windows-eventlog", "rule_id": "MAL-001", "rule_name": "Known Malware Hash",
            "event_count": 1, "first_seen": m(75), "last_seen": m(75), "risk_score": 0.98,
            "description": "Process invoice_scan.exe with LockBit hash e3b0c442...b855 executed on endpoint-01.",
        },
        {
            "alert_id": "ALT-1008", "title": "Audit Log Cleared", "severity": "high", "status": "resolved",
            "source": "windows-eventlog", "rule_id": "LOG-001", "rule_name": "Log Tampering",
            "event_count": 1, "first_seen": m(500), "last_seen": m(500), "risk_score": 0.70,
            "description": "Security event log cleared on server-07 by account 'svc-backup'.",
        },
        {
            "alert_id": "ALT-1009", "title": "Suspicious DNS Queries", "severity": "medium", "status": "new",
            "source": "nginx", "rule_id": "DNS-001", "rule_name": "DGA Domain Pattern",
            "event_count": 37, "first_seen": m(90), "last_seen": m(12), "risk_score": 0.61,
            "description": "37 DGA-like domains resolved from endpoint-04 (10.0.0.19).",
        },
        {
            "alert_id": "ALT-1010", "title": "Data Exfiltration Suspicion", "severity": "critical", "status": "new",
            "source": "firewall", "rule_id": "EXFIL-001", "rule_name": "Large Outbound Transfer",
            "event_count": 3, "first_seen": m(45), "last_seen": m(20), "risk_score": 0.90,
            "description": "3 outbound HTTPS transfers of 1.2 GB from server-02 to cdn-metrics-tracker.net.",
        },
        {
            "alert_id": "ALT-1011", "title": "Kubernetes Privileged Pod", "severity": "high", "status": "acknowledged",
            "source": "kubernetes", "rule_id": "K8S-001", "rule_name": "Privileged Container",
            "event_count": 1, "first_seen": m(300), "last_seen": m(300), "risk_score": 0.72,
            "description": "Pod 'debug-tools' started with privileged=true and hostNetwork on node worker-02.",
        },
        {
            "alert_id": "ALT-1012", "title": "Phishing Link Clicked", "severity": "medium", "status": "resolved",
            "source": "nginx", "rule_id": "PHISH-001", "rule_name": "Phishing URL Access",
            "event_count": 5, "first_seen": m(700), "last_seen": m(690), "risk_score": 0.58,
            "description": "5 users accessed https://phishing.example.com/login from the corporate proxy.",
        },
    ]


async def seed_demo_data(session: AsyncSession) -> dict[str, int]:
    """Populate an empty database with a realistic demo dataset."""
    counts: dict[str, int] = {}

    for u in USERS:
        session.add(
            User(
                id=uuid.uuid4(),
                email=u["email"],
                username=u["username"],
                full_name=u["full_name"],
                hashed_password=hash_password(u["password"]),
                is_active=True,
                is_verified=True,
            )
        )
    await session.commit()
    counts["users"] = len(USERS)

    for r in DETECTION_RULES:
        session.add(DetectionRule(id=uuid.uuid4(), is_active=True, version=1, author="SOC Team", **r))
    for t in MITRE_TECHNIQUES:
        session.add(MITRETechnique(id=uuid.uuid4(), **t))
    for i in IOCS:
        session.add(IOC(id=uuid.uuid4(), is_active=True, **i))
    for ti in THREAT_INTEL:
        session.add(ThreatIntelligence(id=uuid.uuid4(), **ti))
    await session.commit()
    counts.update({"rules": len(DETECTION_RULES), "mitre": len(MITRE_TECHNIQUES), "iocs": len(IOCS), "threat_intel": len(THREAT_INTEL)})

    rng = _LCG(seed=42)
    events: list[SecurityEvent] = []
    for i in range(1, 81):
        event = SecurityEvent(id=uuid.uuid4(), **_event_data(rng, i))
        events.append(event)
        session.add(event)
    await session.commit()
    counts["events"] = len(events)

    now = datetime.now(UTC)
    for a in _alert_defs(now):
        session.add(Alert(id=uuid.uuid4(), **a))
    await session.commit()
    counts["alerts"] = len(_alert_defs(now))

    analyst = (await session.execute(select(User).where(User.username == "analyst"))).scalar_one_or_none()

    incident_defs = [
        {
            "incident_id": "INC-2001",
            "title": "Coordinated intrusion: brute force followed by lateral movement",
            "description": "Attacker at 185.220.101.34 brute-forced SSH, escalated via sudo and moved laterally to 4 hosts.",
            "severity": "critical",
            "status": "open",
            "source": "correlation-engine",
            "risk_score": 0.94,
            "tags": ["brute-force", "lateral-movement", "apt"],
            "alert_refs": ["ALT-1001", "ALT-1003", "ALT-1005"],
        },
        {
            "incident_id": "INC-2002",
            "title": "Ransomware execution attempt on finance endpoint",
            "description": "LockBit sample detected on endpoint-01; containment actions initiated, forensics ongoing.",
            "severity": "critical",
            "status": "investigating",
            "source": "detection-engine",
            "risk_score": 0.97,
            "tags": ["ransomware", "lockbit", "containment"],
            "alert_refs": ["ALT-1007", "ALT-1010"],
        },
        {
            "incident_id": "INC-2003",
            "title": "C2 beaconing from compromised developer workstation",
            "description": "endpoint-02 beacons to evil-c2.example.com every 60 seconds for 6 hours.",
            "severity": "high",
            "status": "contained",
            "source": "detection-engine",
            "risk_score": 0.85,
            "tags": ["c2", "beacon", "apt29"],
            "alert_refs": ["ALT-1004", "ALT-1009"],
        },
    ]

    for d in incident_defs:
        incident = Incident(
            id=uuid.uuid4(),
            incident_id=d["incident_id"],
            title=d["title"],
            description=d["description"],
            severity=d["severity"],
            status=d["status"],
            source=d["source"],
            risk_score=d["risk_score"],
            tags=d["tags"],
            assigned_to=analyst.id if analyst else None,
        )
        for ev in events[:6]:
            incident.events.append(
                IncidentEvent(event_id=ev.id, event_id_str=ev.event_id, added_by="seed", notes="Linked by demo seed")
            )
        incident.iocs.append(
            IncidentIOC(ioc_type="ip", ioc_value="185.220.101.34", confidence=0.88, source="AlienVault OTX")
        )
        incident.iocs.append(
            IncidentIOC(ioc_type="domain", ioc_value="evil-c2.example.com", confidence=0.92, source="MISP Galaxy")
        )
        session.add(incident)
    await session.commit()
    counts["incidents"] = len(incident_defs)

    logger.info("Demo data seeded", **counts)
    return counts


async def seed_if_empty(session: AsyncSession) -> dict[str, int] | None:
    """Run the demo seed only when the events table is empty."""
    events_count = (await session.execute(select(func.count(SecurityEvent.id)))).scalar() or 0
    if events_count > 0:
        logger.info("Database already populated, skipping demo seed", events=events_count)
        return None
    return await seed_demo_data(session)
