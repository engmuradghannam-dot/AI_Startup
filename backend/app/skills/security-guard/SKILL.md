---
skill_name: security-guard
version: "1.0.0"
category: security
trigger: auto
execution_mode: sync
---

# Security Guard

## Intent
Protect sensitive data and prevent security vulnerabilities in agent operations.

## Protection Layers

### Input Sanitization
- Remove PII (emails, phone numbers, SSN)
- Strip API keys and secrets
- Block SQL injection patterns
- Prevent XSS attacks
- Validate file uploads

### Output Filtering
- Redact sensitive data
- Validate generated code for vulnerabilities
- Check for secret leakage
- Ensure compliance with policies

### Access Control
- Verify agent permissions
- Enforce role-based access
- Audit all actions
- Block unauthorized operations

### Threat Detection
- Monitor for suspicious patterns
- Detect data exfiltration attempts
- Identify privilege escalation
- Alert on anomalous behavior

## Rules
1. Never log sensitive data
2. Always validate inputs
3. Principle of least privilege
4. Encrypt data at rest and in transit
5. Audit all security events
6. Fail secure (deny by default)

## Alert Levels
- INFO: Normal security events
- WARNING: Unusual patterns
- CRITICAL: Active threats
- EMERGENCY: Data breach detected

## Example
```python
# Sanitize user input
sanitized = await security_guard.sanitize_input(
    content=user_message,
    agent_id=agent.id
)
# Returns: {"safe": true, "sanitized": "...", "issues": []}

# Check permissions
allowed = await security_guard.check_permissions(
    agent=agent,
    action="write",
    resource="/api/users"
)
```
