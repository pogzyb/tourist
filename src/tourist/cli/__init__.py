import os

import typer
import uvicorn
from xvfbwrapper import Xvfb

app = typer.Typer()


@app.command()
def serve():
    with Xvfb(width=1280, height=720, display=99):
        uvicorn.run(
            "tourist.app:create_app",
            host="0.0.0.0",
            port=int(os.getenv("TOURIST__PORT", 8000)),
            log_level="debug",
            factory=True,
            workers=1,
        )


def main() -> None:
    app()
