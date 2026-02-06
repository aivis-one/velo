# =============================================================================
# VELO Backend — Application Entry Point
# =============================================================================
#
# This is the main FastAPI application instance.
#
# Phase 0.1: Just the app skeleton with version endpoint.
# Phase 0.3: Will add health checks (DB + Redis), CORS, structlog.
#
# HOW TO RUN:
#   uvicorn app.main:app --reload
#
# HOW IT WORKS:
#   FastAPI() creates a web application instance.
#   @app.get("/") registers a function to handle GET requests to /.
#   Uvicorn binds this app to a port and starts listening for HTTP requests.
# =============================================================================

from fastapi import FastAPI

app = FastAPI(
    title="VELO API",
    description="Platform for wellness practice facilitators",
    version="0.1.0",
    # docs_url="/docs" is the default — Swagger UI auto-generated from your endpoints.
    # Try it: http://localhost:8000/docs after starting the server.
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint — returns API name and version.

    This is useful for quick "is the server running?" checks
    and for identifying which version is deployed.
    """
    return {"name": "VELO API", "version": "0.1.0"}
