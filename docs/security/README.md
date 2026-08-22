# Security Documentation — AI SOC Platform

## Documents

| Document | Description |
|----------|-------------|
| [Threat Model](threat-model.md) | STRIDE analysis, attack scenarios, controls matrix |
| [Architecture Security](../architecture/README.md#6-sécurité) | Security architecture overview |

## Security Principles

1. **Defense in Depth** — Multiple layers of security controls
2. **Least Privilege** — Minimum permissions required
3. **Zero Trust** — Verify every request, even internal
4. **Fail Secure** — Default deny, SOAR simulation by default
5. **Audit Everything** — Immutable audit trail for sensitive actions

## Compliance Targets

- OWASP Top 10 (2021)
- CIS Benchmarks (Docker, Kubernetes)
- NIST Cybersecurity Framework (Identify, Protect, Detect, Respond, Recover)

## Security Scanning (CI/CD — Phase 21)

| Tool | Type | Scope |
|------|------|-------|
| Semgrep | SAST | Python, TypeScript source code |
| Trivy | Container/Dependency | Docker images, OS packages |
| Gitleaks | Secret scanning | Git history, commits |
| OWASP ZAP | DAST | Running application |
| pip-audit | Dependency | Python packages |
| npm audit | Dependency | Node.js packages |

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly by contacting the project maintainers directly. Do not create public GitHub issues for security vulnerabilities.
