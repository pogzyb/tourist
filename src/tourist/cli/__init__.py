import subprocess
import time
import os
import tempfile
import shlex

import typer
import uvicorn

app = typer.Typer()


@app.command()
def serve():
    print(f"TOURIST🤳 [v{os.getenv('TOURIST_VERSION')}]")
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
