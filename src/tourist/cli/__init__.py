import os
import subprocess

import typer
import uvicorn

app = typer.Typer()


@app.command()
def serve():
    print(f"TOURIST🤳 [v{os.getenv('TOURIST_VERSION')}]")
    uvicorn_run = "uvicorn tourist.app:create_app --host 0.0.0.0 --port 8000 --workers 1 --log-level debug --factory"
    xvfb_run = f"xvfb-run -n 99 --server-args='-screen 0 1024x768x24' {uvicorn_run}"
    with subprocess.Popen(xvfb_run, shell=True) as process:
        process.wait()


def main() -> None:
    app()
