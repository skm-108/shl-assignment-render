from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.models.api import ChatRequest, ChatResponse
from app.services.conversation import ConversationService


def create_app() -> FastAPI:
    app = FastAPI(title="SHL Conversational Assessment Recommender")
    catalog_path = Path(__file__).resolve().parents[2] / "New folder" / "shl_product_catalog.json"
    service = ConversationService(catalog_path)

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        return service.respond(request)

    return app


app = create_app()
