"""
Staff-Echo Application Entry Point

Usage:
    python main.py                    # Development mode (in-memory everything)
    STAFF_ECHO_GEMINI_API_KEY=... python main.py  # With Gemini API
"""

import uvicorn

from staff_echo.infrastructure.config.settings import Settings
from staff_echo.infrastructure.config.dependency_injection import Container
from staff_echo.presentation.api.app import create_app


def main():
    settings = Settings()
    container = Container(settings)
    app = create_app(container)
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
