"""External Integrations API routes."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel

from app.services.integration_manager import (
    get_integration_manager, IntegrationType, IntegrationStatus
)

router = APIRouter(prefix="/integrations", tags=["Integrations"])


# ========== Pydantic Models ==========

class CreateIntegrationRequest(BaseModel):
    name: str
    integration_type: str  # webhook, api_key, oauth, plugin
    description: str = ""
    config: dict = {}


class CreateAPIKeyRequest(BaseModel):
    name: str
    permissions: List[str]
    expires_in_days: int = 365


class CreateWebhookRequest(BaseModel):
    url: str
    events: List[str]
    description: str = ""


class UpdateIntegrationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    status: Optional[str] = None


# ========== Integration Routes ==========

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_integration(request: CreateIntegrationRequest):
    """Create a new external integration."""
    manager = await get_integration_manager()
    integration = await manager.create_integration(
        name=request.name,
        integration_type=request.integration_type,
        description=request.description,
        config=request.config
    )
    return integration.to_dict()


@router.get("/")
async def list_integrations(
    integration_type: Optional[str] = None,
    status: Optional[str] = None,
):
    """List all integrations."""
    manager = await get_integration_manager()
    return await manager.list_integrations(integration_type, status)


@router.get("/{integration_id}")
async def get_integration(integration_id: str):
    """Get integration details."""
    manager = await get_integration_manager()
    integration = await manager.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration.to_dict()


@router.patch("/{integration_id}")
async def update_integration(integration_id: str, request: UpdateIntegrationRequest):
    """Update an integration."""
    manager = await get_integration_manager()
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    integration = await manager.update_integration(integration_id, updates)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration.to_dict()


@router.delete("/{integration_id}")
async def delete_integration(integration_id: str):
    """Delete an integration."""
    manager = await get_integration_manager()
    success = await manager.delete_integration(integration_id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")
    return {"message": "Integration deleted"}


# ========== API Key Routes ==========

@router.post("/{integration_id}/api-keys", status_code=status.HTTP_201_CREATED)
async def create_api_key(integration_id: str, request: CreateAPIKeyRequest):
    """Create a new API key."""
    manager = await get_integration_manager()
    api_key = await manager.create_api_key(
        integration_id=integration_id,
        name=request.name,
        permissions=request.permissions,
        expires_in_days=request.expires_in_days
    )
    if not api_key:
        raise HTTPException(status_code=404, detail="Integration not found")
    return api_key.to_dict(include_key=True)


@router.get("/{integration_id}/api-keys")
async def list_api_keys(integration_id: str):
    """List API keys for an integration."""
    manager = await get_integration_manager()
    return await manager.list_api_keys(integration_id)


@router.delete("/{integration_id}/api-keys/{key_id}")
async def revoke_api_key(integration_id: str, key_id: str):
    """Revoke an API key."""
    manager = await get_integration_manager()
    success = await manager.revoke_api_key(integration_id, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key revoked"}


# ========== Webhook Routes ==========

@router.post("/{integration_id}/webhooks", status_code=status.HTTP_201_CREATED)
async def create_webhook(integration_id: str, request: CreateWebhookRequest):
    """Create a new webhook endpoint."""
    manager = await get_integration_manager()
    webhook = await manager.create_webhook(
        integration_id=integration_id,
        url=request.url,
        events=request.events,
        description=request.description
    )
    if not webhook:
        raise HTTPException(status_code=404, detail="Integration not found")
    return webhook.to_dict()


@router.get("/{integration_id}/webhooks")
async def list_webhooks(integration_id: str):
    """List webhooks for an integration."""
    manager = await get_integration_manager()
    return await manager.list_webhooks(integration_id)


@router.delete("/{integration_id}/webhooks/{webhook_id}")
async def delete_webhook(integration_id: str, webhook_id: str):
    """Delete a webhook endpoint."""
    manager = await get_integration_manager()
    success = await manager.delete_webhook(integration_id, webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"message": "Webhook deleted"}


# ========== Event Types ==========

@router.get("/events/available")
async def get_available_events():
    """Get list of available webhook events."""
    manager = await get_integration_manager()
    return await manager.get_available_events()


# ========== API Key Validation ==========

@router.post("/validate-key")
async def validate_api_key(x_api_key: str = Header(...)):
    """Validate an API key."""
    manager = await get_integration_manager()
    api_key = await manager.validate_api_key(x_api_key)
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "valid": True,
        "key_id": api_key.id,
        "name": api_key.name,
        "permissions": api_key.permissions,
        "expires_at": api_key.expires_at.isoformat(),
    }
