#!/usr/bin/env python3
"""
Simulate a multi-phase attack against the AI SOC Platform.

Generates timestamped security events that flow through the detection
pipeline so that brute-force, privilege escalation, lateral movement,
and data-access alerts are raised.

Usage:
    python scripts/simulate_attack.py              # SQLite
    python scripts/simulate_attack.py --postgres    # PostgreSQL
    python scripts/simulate_attack.py --dry-run     # print events only
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "collector-service"))

from app.core.database import Base
from app.models.event import SecurityEvent

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://soc_admin:soc_secret_password_2026@localhost:5432/ai_soc_platform",
)

ATTACKER_IP = "192.168.1.100"
VICTIM_HOST = "webserver-01"
VICTIM_IP = "10.0.0.5"
COMPROMISED_USER = "admin"
OTHER_HOSTS = ["fileserver-01", "dbserver-01", "appserver-01"]
BASE_TIME = datetime.now(UTC)


def _event_id() -> str:
    return f"evt-atk-{uuid.uuid4().hex[:10]}"


def _make_event(phase: int, minute_offset: int, **kwargs) -> dict:
    ts = BASE_TIME + timedelta(minutes=minute_offset)
    defaults = {
        "event_id": _event_id(),
        "timestamp": ts,
        "source": "linux-syslog",
        "source_type": "server",
        "category": "authentication",
        "action": "login",
        "severity": "info",
        "source_ip": ATTACKER_IP,
        "destination_ip": VICTIM_IP,
        "hostname": VICTIM_HOST,
        "user_name": COMPROMISED_USER,
    }
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# Phase definitions
# ---------------------------------------------------------------------------


def phase1_brute_force() -> list[dict]:
    """Phase 1: 15 failed login attempts from the attacker IP."""
    events = []
    for i in range(15):
        events.append(
            _make_event(
                phase=1,
                minute_offset=i,
                action="login_failed",
                severity="medium",
                user_name="admin" if i < 10 else "root",
                raw_event={"attempt": i + 1, "method": "password"},
            )
        )
    return events


def phase2_successful_login() -> list[dict]:
    """Phase 2: Successful login after brute force."""
    return [
        _make_event(
            phase=2,
            minute_offset=16,
            action="login",
            severity="low",
            user_name=COMPROMISED_USER,
            raw_event={"method": "password", "session_id": "sess-abcdef123"},
        )
    ]


def phase3_privilege_escalation() -> list[dict]:
    """Phase 3: User escalates to root."""
    return [
        _make_event(
            phase=3,
            minute_offset=20,
            action="sudo",
            severity="critical",
            category="privilege_escalation",
            user_name=COMPROMISED_USER,
            raw_event={"command": "sudo bash", "terminal": "pts/0"},
        )
    ]


def phase4_sensitive_file_access() -> list[dict]:
    """Phase 4: Access sensitive files."""
    files = ["/etc/shadow", "/etc/passwd", "/root/.ssh/id_rsa", "/var/log/auth.log"]
    events = []
    for i, filepath in enumerate(files):
        events.append(
            _make_event(
                phase=4,
                minute_offset=25 + i,
                action="file_access",
                severity="high",
                category="file_access",
                user_name="root",
                raw_event={"file_path": filepath, "operation": "read"},
            )
        )
    return events


def phase5_lateral_movement() -> list[dict]:
    """Phase 5: Move to other hosts."""
    events = []
    for i, host in enumerate(OTHER_HOSTS):
        events.append(
            _make_event(
                phase=5,
                minute_offset=30 + i,
                action="ssh_connection",
                severity="critical",
                category="lateral_movement",
                source_ip=ATTACKER_IP,
                destination_ip=f"10.0.0.{10 + i}",
                hostname=host,
                user_name="root",
                raw_event={"method": "ssh", "key_used": "stolen_rsa"},
            )
        )
    events.append(
        _make_event(
            phase=5,
            minute_offset=34,
            action="smb_connection",
            severity="high",
            category="lateral_movement",
            destination_port=445,
            hostname="fileserver-01",
            user_name="admin",
            raw_event={"share": "\\\\fileserver-01\\C$", "access_level": "full"},
        )
    )
    return events


# ---------------------------------------------------------------------------
# All phases combined
# ---------------------------------------------------------------------------


def generate_attack_events() -> list[dict]:
    events = []
    events.extend(phase1_brute_force())
    events.extend(phase2_successful_login())
    events.extend(phase3_privilege_escalation())
    events.extend(phase4_sensitive_file_access())
    events.extend(phase5_lateral_movement())
    return events


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


async def run_attack(url: str, dry_run: bool = False):
    events = generate_attack_events()

    if dry_run:
        print(f"\n{'=' * 70}")
        print(f"  ATTACK SIMULATION — {len(events)} events across 5 phases")
        print(f"{'=' * 70}\n")
        for evt in events:
            ts = evt["timestamp"].strftime("%H:%M:%S")
            print(
                f"  [{ts}] phase={evt.get('_phase', '?'):>1} "
                f"action={evt['action']:<20} "
                f"src={evt['source_ip']:<16} "
                f"dst={evt.get('destination_ip', 'N/A'):<16} "
                f"user={evt['user_name']:<15} "
                f"sev={evt['severity']}"
            )
        print("\n  Summary:")
        print(f"    Phase 1 — Brute force:            15 failed logins from {ATTACKER_IP}")
        print(f"    Phase 2 — Compromised login:       1 successful login as {COMPROMISED_USER}")
        print("    Phase 3 — Privilege escalation:    sudo → root")
        print("    Phase 4 — Sensitive file access:   /etc/shadow, /root/.ssh/id_rsa, …")
        print(f"    Phase 5 — Lateral movement:        SSH/SMB to {', '.join(OTHER_HOSTS)}")
        return

    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        phases = {
            1: ("Brute Force", phase1_brute_force),
            2: ("Successful Login", phase2_successful_login),
            3: ("Privilege Escalation", phase3_privilege_escalation),
            4: ("Sensitive File Access", phase4_sensitive_file_access),
            5: ("Lateral Movement", phase5_lateral_movement),
        }

        total = 0
        for phase_num, (name, fn) in phases.items():
            phase_events = fn()
            print(f"\n[*] Phase {phase_num}: {name} ({len(phase_events)} events)")
            for evt in phase_events:
                db_evt = SecurityEvent(
                    id=uuid.uuid4(),
                    **{k: v for k, v in evt.items() if k in SecurityEvent.__table__.columns},
                )
                session.add(db_evt)
                total += 1
                ts = evt["timestamp"].strftime("%H:%M:%S")
                print(f"    [{ts}] {evt['action']:<20} from {evt['source_ip']} → {evt.get('destination_ip', 'N/A')}")

            await session.commit()
            print(f"    ✓ Ingested {len(phase_events)} events")

        print(f"\n[✓] Attack simulation complete — {total} events ingested")
        print("    Detection engine will now process events and generate alerts.")
        print("    Check /api/v1/alerts/ and /api/v1/incidents/ for results.")

    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Simulate a multi-phase attack scenario")
    parser.add_argument("--postgres", action="store_true", help="Use PostgreSQL (DATABASE_URL)")
    parser.add_argument("--url", type=str, default=None, help="Override DATABASE_URL")
    parser.add_argument("--dry-run", action="store_true", help="Print events without writing to DB")
    args = parser.parse_args()

    if args.url:
        url = args.url
    elif args.postgres:
        url = DATABASE_URL
    else:
        url = "sqlite+aiosqlite:///./soc_attack.db"

    asyncio.run(run_attack(url, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
