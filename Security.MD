# SECURITY.MD - Security & Alignment Policy

## 0. OVERVIEW
ARK is a safety-critical framework. We take vulnerabilities seriously. This includes not only software bugs but also alignment bypasses, reward hacking exploits, and prompt injections.

## 1. REPORTING A VULNERABILITY
If you discover a vulnerability (e.g., a way to bypass the SafetyMonitor, jailbreak the Warden, or exploit a memory corruption flaw):
- DO NOT open a public issue.
- DO NOT post it on social media.
- Please email the core research team directly at: security@ark-research.org
- Include a detailed proof-of-concept (PoC) and the specific environment/seed used.

## 2. OUR COMMITMENT
- We will acknowledge receipt of your report within 48 hours.
- We will keep you updated on the remediation progress.
- We will publicly credit you in the CHANGELOG.md once the patch is released (unless you prefer to remain anonymous).

## 3. SCOPE
The following are considered critical vulnerabilities:
- Bypassing the ALLOW/BLOCK/REPLAN loop.
- Achieving high reward while violating the eligibility/ constraints.
- Resisting the request_shutdown command.
- Escaping the sandbox via the hallucinator/ module.
