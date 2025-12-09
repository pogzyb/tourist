import os
import subprocess

import typer
import uvicorn

app = typer.Typer()


@app.command()
def serve():
    x11_proc = subprocess.Popen(
        f"Xvfb {os.getenv('DISPLAY')} -screen 0 1366x768x24",
        shell=True,
    )
    uvicorn.run(
        "tourist.app:create_app",
        host="0.0.0.0",
        port=int(os.getenv("TOURIST__PORT", 8000)),
        log_level="debug",
        factory=True,
    )


def main() -> None:
    app()
