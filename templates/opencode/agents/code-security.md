---
description: Security review specialist for identifying vulnerabilities and ensuring secure coding practices. Invoke for security audits, vulnerability assessments, and OWASP compliance checks.
mode: subagent
model: {{model:deep_review}}#medium
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
  - action: subagent
    resource: "*"
    effect: deny
  - action: question
    resource: "*"
    effect: deny
---

{{prompt:code-security}}
