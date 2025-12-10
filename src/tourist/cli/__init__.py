import os
import subprocess

import typer
import uvicorn

app = typer.Typer()


@app.command()
def serve():

    if not os.path.exists("/tmp/.X99-lock"):
        print("starting X11")
        subprocess.Popen(
            f"Xvfb :99 -screen 0 1280x720x24",
            shell=True,
        )

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
