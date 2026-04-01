import os
import tempfile

import typer
import uvicorn
from xvfbwrapper import Xvfb

app = typer.Typer()


@app.command()
def serve():
    print(f"TOURIST🤳 [v{os.getenv('TOURIST_VERSION')}]")
    with tempfile.TemporaryDirectory(prefix="xvfb-") as tempdir:
        with Xvfb(display=99, height=1280, tempdir=tempdir, timeout=60):
            uvicorn.run(
                "tourist.app:create_app",
                host="0.0.0.0",
                port=int(os.getenv("TOURIST_PORT", 8000)),
                log_level="debug",
                factory=True,
                workers=1,
            )


def main() -> None:
    app()
