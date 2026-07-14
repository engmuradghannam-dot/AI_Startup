---
skill_name: deployment-manager
version: "1.0.0"
category: deployment
trigger: manual
execution_mode: async
---

# Deployment Manager

## Intent
Automate deployment of agents and services with safety checks and rollback capability.

## Deployment Pipeline

### Build
- Compile/bundle code
- Run tests
- Build Docker image
- Scan for vulnerabilities

### Staging
- Deploy to staging environment
- Run integration tests
- Performance testing
- Security scanning

### Production
- Blue-green deployment
- Canary release
- Health checks
- Traffic shifting

### Monitoring
- Error tracking
- Performance metrics
- User feedback
- Automatic rollback triggers

## Safety Features

### Pre-Deployment
- All tests must pass
- Security scan clean
- Code review approved
- Change log updated

### During Deployment
- Health checks every 30s
- Error rate monitoring
- Latency tracking
- Automatic pause on issues

### Post-Deployment
- 1-hour monitoring window
- Rollback on error threshold
- Performance comparison
- User feedback collection

## Rollback
- One-click rollback
- Automatic rollback on failure
- Preserve data integrity
- Notify stakeholders

## Rules
1. Never deploy without tests
2. Always have rollback plan
3. Monitor for 1 hour minimum
4. Document all changes
5. Communicate with team

## Example
```python
# Deploy agent
result = await deployment_manager.deploy(
    agent_id=agent.id,
    environment="production",
    version="2.1.0",
    strategy="canary"
)
# Returns: {"deployment_id": "...", "status": "completed", "health": "passing"}

# Rollback if needed
await deployment_manager.rollback(deployment_id, target_version="2.0.0")
```
