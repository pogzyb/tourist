import os
import sys

import typer
import uvicorn

app = typer.Typer()


# TODO/contribution: Add flags for customizations like port.
@app.command()
def serve():

    ok = True
    chrome_binary = os.getenv("TOURIST__CHROME_BIN", "/tourist/browser/chrome")

    if ok:
        uvicorn.run(
            "tourist.app:create_app",
            host="0.0.0.0",
            port=int(os.getenv("TOURIST__PORT", 8000)),
            log_level="info",
            factory=True,
        )
    else:
        sys.exit(1)


def main() -> None:
    app()
