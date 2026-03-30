import subprocess
import time
import os
import tempfile
import shlex

import typer
import uvicorn
from xvfbwrapper import Xvfb

app = typer.Typer()


@app.command()
def serve():
    with tempfile.TemporaryDirectory(prefix="x11-") as tempdir:
        with Xvfb(
            width=1280,
            height=720,
            display=99,
            tempdir=tempdir,
            set_xdg_session_type=True,
        ):
            while True:
                check_xvfb = subprocess.run(
                    shlex.split("xdpyinfo -display :99"),
                    capture_output=True,
                    text=True,
                )
                if check_xvfb.returncode != 0:
                    print("Xvfb is not ready, waiting...")
                    time.sleep(1)
                    continue
                else:
                    break
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
