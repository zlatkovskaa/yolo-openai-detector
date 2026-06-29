"""Model discovery endpoint."""

from fastapi import APIRouter, Depends, Request

from ..auth import require_api_key
from ..openai_compat.schemas import ModelListResponse, ModelObject

router = APIRouter()


@router.get("/v1/models", response_model=ModelListResponse)
async def list_models(
    request: Request,
    _: None = Depends(require_api_key),
) -> ModelListResponse:
    settings = request.app.state.settings
    return ModelListResponse(
        data=[
            ModelObject(
                id=settings.model_id,
                created=request.app.state.started_at,
                owned_by="local",
            )
        ]
    )
