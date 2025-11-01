import uvicorn
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from controllers.voice_controller import router as voice_router
from controllers.health_check import router as health_check_router

load_dotenv()


def create_app():
    app = FastAPI()
    app.state.settings = get_settings()

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(voice_router)
    app.include_router(health_check_router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST"), port=int(os.getenv("PORT")))
