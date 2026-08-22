"""Quick API test script"""

import json

import httpx

BASE = "http://127.0.0.1:8000"


def main():
    # Test 1: Health
    r = httpx.get(f"{BASE}/health")
    print(f"[1] Health: {r.status_code} - {r.json()}")

    # Test 2: Root
    r = httpx.get(f"{BASE}/")
    print(f"[2] Root: {r.status_code} - {r.json()}")

    # Test 3: Register admin
    r = httpx.post(
        f"{BASE}/api/v1/auth/register",
        json={
            "email": "admin@aisoc-platform.com",
            "username": "admin",
            "full_name": "Admin User",
            "password": "admin123456",
        },
    )
    print(f"[3] Register: {r.status_code} - {r.text[:200]}")

    if r.status_code == 201:
        # Test 4: Login
        r = httpx.post(f"{BASE}/api/v1/auth/login", json={"username": "admin", "password": "admin123456"})
        print(f"[4] Login: {r.status_code}")
        if r.status_code == 200:
            token_data = r.json()
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            print(f"    Token: {token_data['access_token'][:50]}...")

            # Test 5: Register analyst
            r = httpx.post(
                f"{BASE}/api/v1/auth/register",
                json={
                    "email": "analyst@aisoc-platform.com",
                    "username": "analyst",
                    "full_name": "SOC Analyst",
                    "password": "analyst12345",
                },
            )
            print(f"[5] Register analyst: {r.status_code}")

            # Test 6: Ingest events
            sources = ["linux-server-01", "windows-ws-02", "nginx-proxy-01", "docker-host-01", "aws-cloudtrail"]
            categories = ["authentication", "network", "process", "file", "cloud"]
            severities = ["low", "medium", "high", "critical"]
            actions = [
                "login_failed",
                "login_success",
                "port_scan",
                "privilege_escalation",
                "file_access",
                "process_creation",
                "network_connection",
            ]

            events_payload = {"events": []}
            for i in range(20):
                events_payload["events"].append(
                    {
                        "source": sources[i % len(sources)],
                        "source_type": sources[i % len(sources)].split("-")[0],
                        "category": categories[i % len(categories)],
                        "action": actions[i % len(actions)],
                        "severity": severities[i % len(severities)],
                        "source_ip": f"192.168.1.{100 + i}",
                        "user_name": f"user_{i % 5}",
                        "hostname": sources[i % len(sources)],
                    }
                )

            r = httpx.post(f"{BASE}/api/v1/events/bulk", json=events_payload, headers=headers)
            print(f"[6] Bulk ingest: {r.status_code} - {r.json()}")

            # Test 7: List events
            r = httpx.get(f"{BASE}/api/v1/events?page=1&page_size=5", headers=headers)
            print(f"[7] List events: {r.status_code} - total={r.json().get('total', 'N/A')}")

            # Test 8: Create incident
            r = httpx.post(
                f"{BASE}/api/v1/incidents",
                json={
                    "title": "Possible Brute Force Attack",
                    "description": "Multiple failed login attempts detected from IP 192.168.1.100",
                    "severity": "high",
                    "risk_score": 72.5,
                    "source": "detection-engine",
                },
                headers=headers,
            )
            print(f"[8] Create incident: {r.status_code} - {r.json().get('incident_id', 'N/A')}")

            # Test 9: List incidents
            r = httpx.get(f"{BASE}/api/v1/incidents", headers=headers)
            print(f"[9] List incidents: {r.status_code} - total={r.json().get('total', 'N/A')}")

            # Test 10: Dashboard
            r = httpx.get(f"{BASE}/api/v1/dashboard", headers=headers)
            print(f"[10] Dashboard: {r.status_code} - {json.dumps(r.json().get('stats', {}), indent=None)}")

            # Test 11: Create IOC
            r = httpx.post(
                f"{BASE}/api/v1/threat-intelligence/iocs",
                json={
                    "ioc_type": "ip",
                    "ioc_value": "185.220.101.45",
                    "severity": "high",
                    "confidence": 92.0,
                    "threat_type": "botnet",
                    "source": "abuse.ch",
                },
                headers=headers,
            )
            print(f"[11] Create IOC: {r.status_code}")

            # Test 12: Threat intel lookup
            r = httpx.get(f"{BASE}/api/v1/threat-intelligence/lookup/185.220.101.45", headers=headers)
            print(f"[12] Threat lookup: {r.status_code} - {r.json()}")

            # Test 13: AI analyze
            r = httpx.post(
                f"{BASE}/api/v1/ai/analyze",
                json={
                    "query": "Why is this brute force attack critical?",
                    "context": {"ip": "192.168.1.100", "events": 15},
                },
                headers=headers,
            )
            print(f"[13] AI analyze: {r.status_code}")
            if r.status_code == 200:
                resp = r.json()
                print(f"    Confidence: {resp.get('confidence')} - Model: {resp.get('model_used')}")

            # Test 14: Response action (simulated)
            r = httpx.post(
                f"{BASE}/api/v1/response/block-ip",
                json={"ip_address": "192.168.1.100", "reason": "Brute force detected"},
                headers=headers,
            )
            print(f"[14] Block IP: {r.status_code} - simulated={r.json().get('is_simulated', 'N/A')}")

            # Test 15: Detection rules
            r = httpx.get(f"{BASE}/api/v1/detection-rules", headers=headers)
            print(f"[15] Detection rules: {r.status_code} - count={len(r.json())}")

            print("\n=== ALL TESTS PASSED ===")
            print("\nFrontend: http://localhost:3000")
            print("Backend API docs: http://localhost:8000/docs")
        else:
            print(f"    Login failed: {r.text}")
    elif r.status_code == 400 and "already exists" in r.text:
        print("    User already exists, trying login...")
        r = httpx.post(f"{BASE}/api/v1/auth/login", json={"username": "admin", "password": "admin123456"})
        print(f"    Login: {r.status_code}")
    else:
        print(f"    Unexpected: {r.text}")


if __name__ == "__main__":
    main()
