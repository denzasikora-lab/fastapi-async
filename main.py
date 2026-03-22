from contextlib import asynccontextmanager

# Import FastAPI to create the web application
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Import the router for wallet endpoints
from app.api.v1.wallets import router as wallet_router
# Import the router for operations endpoints (income and expenses)
from app.api.v1.operations import router as operations_router
from app.api.v1.users import router as users_router
# Import DB helpers and settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


# Create the FastAPI application instance
app = FastAPI(lifespan=lifespan)

# Include the wallet router with the /api/v1 prefix
app.include_router(wallet_router, prefix="/api/v1", tags=["wallet"])
# Include the operations router with the /api/v1 prefix
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])
# Include the users router with the /api/v1 prefix
app.include_router(users_router, prefix="/api/v1", tags=["users"])

# Mount static files (HTML, CSS, JS) from app/static at /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")