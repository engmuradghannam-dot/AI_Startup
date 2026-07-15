"""External Integration API.

Provides webhooks, API keys, and integration endpoints
for third-party services to connect with AI Startup.
"""
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid


class IntegrationType(Enum):
    WEBHOOK = "webhook"
    API_KEY = "api_key"
    OAUTH = "oauth"
    PLUGIN = "plugin"


class IntegrationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"


class WebhookEndpoint:
    """A webhook endpoint configuration."""

    def __init__(self, url: str, events: List[str], secret: str,
                 integration_id: str, description: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.url = url
        self.events = events
        self.secret = secret
        self.integration_id = integration_id
        self.description = description
        self.status = IntegrationStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.last_triggered = None
        self.success_count = 0
        self.fail_count = 0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "url": self.url,
            "events": self.events,
            "integration_id": self.integration_id,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "success_count": self.success_count,
            "fail_count": self.fail_count,
        }


class APIKey:
    """An API key for external access."""

    def __init__(self, name: str, permissions: List[str], 
                 integration_id: str, expires_in_days: int = 365):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.key = self._generate_key()
        self.permissions = permissions
        self.integration_id = integration_id
        self.status = IntegrationStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        self.last_used = None
        self.use_count = 0

    def _generate_key(self) -> str:
        """Generate a secure API key."""
        return f"ask_{secrets.token_urlsafe(32)}"

    def to_dict(self, include_key: bool = False) -> Dict:
        result = {
            "id": self.id,
            "name": self.name,
            "permissions": self.permissions,
            "integration_id": self.integration_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "use_count": self.use_count,
        }
        if include_key:
            result["key"] = self.key
        return result

    def is_valid(self) -> bool:
        """Check if API key is valid."""
        return (self.status == IntegrationStatus.ACTIVE and 
                datetime.utcnow() < self.expires_at)


class ExternalIntegration:
    """External integration configuration."""

    def __init__(self, name: str, integration_type: IntegrationType,
                 description: str = "", config: Dict = None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.integration_type = integration_type
        self.description = description
        self.config = config or {}
        self.status = IntegrationStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.webhooks: List[WebhookEndpoint] = []
        self.api_keys: List[APIKey] = []

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.integration_type.value,
            "description": self.description,
            "config": self.config,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "webhook_count": len(self.webhooks),
            "api_key_count": len(self.api_keys),
        }


class IntegrationManager:
    """Manages all external integrations."""

    def __init__(self):
        self.integrations: Dict[str, ExternalIntegration] = {}
        self.api_key_index: Dict[str, APIKey] = {}  # Fast lookup by key
        self.webhook_index: Dict[str, WebhookEndpoint] = {}  # Fast lookup by ID

    # ========== Integration Management ==========

    async def create_integration(self, name: str, integration_type: str,
                                description: str = "", config: Dict = None) -> ExternalIntegration:
        """Create a new external integration."""
        integration = ExternalIntegration(
            name=name,
            integration_type=IntegrationType(integration_type),
            description=description,
            config=config or {}
        )
        self.integrations[integration.id] = integration
        return integration

    async def get_integration(self, integration_id: str) -> Optional[ExternalIntegration]:
        """Get an integration by ID."""
        return self.integrations.get(integration_id)

    async def list_integrations(self, integration_type: Optional[str] = None,
                                status: Optional[str] = None) -> List[Dict]:
        """List all integrations with filtering."""
        result = list(self.integrations.values())

        if integration_type:
            result = [i for i in result if i.integration_type.value == integration_type]

        if status:
            result = [i for i in result if i.status.value == status]

        return [i.to_dict() for i in result]

    async def update_integration(self, integration_id: str, 
                                updates: Dict) -> Optional[ExternalIntegration]:
        """Update an integration."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return None

        if "name" in updates:
            integration.name = updates["name"]
        if "description" in updates:
            integration.description = updates["description"]
        if "config" in updates:
            integration.config.update(updates["config"])
        if "status" in updates:
            integration.status = IntegrationStatus(updates["status"])

        return integration

    async def delete_integration(self, integration_id: str) -> bool:
        """Delete an integration."""
        if integration_id in self.integrations:
            integration = self.integrations[integration_id]
            # Clean up associated resources
            for webhook in integration.webhooks:
                if webhook.id in self.webhook_index:
                    del self.webhook_index[webhook.id]
            for api_key in integration.api_keys:
                if api_key.key in self.api_key_index:
                    del self.api_key_index[api_key.key]
            del self.integrations[integration_id]
            return True
        return False

    # ========== API Keys ==========

    async def create_api_key(self, integration_id: str, name: str,
                            permissions: List[str], expires_in_days: int = 365) -> Optional[APIKey]:
        """Create a new API key."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return None

        api_key = APIKey(
            name=name,
            permissions=permissions,
            integration_id=integration_id,
            expires_in_days=expires_in_days
        )

        integration.api_keys.append(api_key)
        self.api_key_index[api_key.key] = api_key

        return api_key

    async def validate_api_key(self, key: str) -> Optional[APIKey]:
        """Validate an API key."""
        api_key = self.api_key_index.get(key)
        if api_key and api_key.is_valid():
            api_key.last_used = datetime.utcnow()
            api_key.use_count += 1
            return api_key
        return None

    async def revoke_api_key(self, integration_id: str, key_id: str) -> bool:
        """Revoke an API key."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return False

        for api_key in integration.api_keys:
            if api_key.id == key_id:
                api_key.status = IntegrationStatus.REVOKED
                if api_key.key in self.api_key_index:
                    del self.api_key_index[api_key.key]
                return True
        return False

    async def list_api_keys(self, integration_id: str) -> List[Dict]:
        """List API keys for an integration."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return []
        return [k.to_dict() for k in integration.api_keys]

    # ========== Webhooks ==========

    async def create_webhook(self, integration_id: str, url: str,
                            events: List[str], description: str = "") -> Optional[WebhookEndpoint]:
        """Create a new webhook endpoint."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return None

        secret = secrets.token_urlsafe(32)
        webhook = WebhookEndpoint(
            url=url,
            events=events,
            secret=secret,
            integration_id=integration_id,
            description=description
        )

        integration.webhooks.append(webhook)
        self.webhook_index[webhook.id] = webhook

        return webhook

    async def trigger_webhook(self, event: str, payload: Dict) -> List[Dict]:
        """Trigger webhooks for an event."""
        import httpx

        results = []
        for webhook in self.webhook_index.values():
            if event in webhook.events and webhook.status == IntegrationStatus.ACTIVE:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            webhook.url,
                            json={
                                "event": event,
                                "timestamp": datetime.utcnow().isoformat(),
                                "payload": payload,
                            },
                            headers={
                                "X-Webhook-Secret": webhook.secret,
                                "X-Event-Type": event,
                            },
                            timeout=10.0
                        )
                        webhook.last_triggered = datetime.utcnow()
                        webhook.success_count += 1
                        results.append({
                            "webhook_id": webhook.id,
                            "status": "success",
                            "status_code": response.status_code,
                        })
                except Exception as e:
                    webhook.fail_count += 1
                    results.append({
                        "webhook_id": webhook.id,
                        "status": "failed",
                        "error": str(e),
                    })

        return results

    async def delete_webhook(self, integration_id: str, webhook_id: str) -> bool:
        """Delete a webhook endpoint."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return False

        for i, webhook in enumerate(integration.webhooks):
            if webhook.id == webhook_id:
                integration.webhooks.pop(i)
                if webhook_id in self.webhook_index:
                    del self.webhook_index[webhook_id]
                return True
        return False

    async def list_webhooks(self, integration_id: str) -> List[Dict]:
        """List webhooks for an integration."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return []
        return [w.to_dict() for w in integration.webhooks]

    # ========== Event Types ==========

    async def get_available_events(self) -> List[Dict]:
        """Get list of available webhook events."""
        return [
            {"event": "agent.created", "description": "New agent created"},
            {"event": "agent.updated", "description": "Agent updated"},
            {"event": "agent.deleted", "description": "Agent deleted"},
            {"event": "task.completed", "description": "Task completed"},
            {"event": "task.failed", "description": "Task failed"},
            {"event": "chat.message", "description": "New chat message"},
            {"event": "learning.updated", "description": "Learning pattern updated"},
            {"event": "system.alert", "description": "System alert triggered"},
            {"event": "skill.executed", "description": "Skill executed"},
            {"event": "training.completed", "description": "Training completed"},
        ]


# Singleton instance
_integration_manager: Optional[IntegrationManager] = None


async def get_integration_manager() -> IntegrationManager:
    """Get or create the integration manager singleton."""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = IntegrationManager()
    return _integration_manager
