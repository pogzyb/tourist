import os
import sys

import typer
import uvicorn

app = typer.Typer()


# TODO/contribution: Add flags for customizations like port.
@app.command()
def serve():

    # make sure chrome exists
    ok = True
    chrome_binary = os.getenv("TOURIST__CHROME_BIN", "/tourist/browser/chrome")
    if not os.path.isfile(chrome_binary):
        ok = False
        print("Exiting because chrome wasn't found!")
        print("Set it with the environment variable: TOURIST__CHROME_BIN")
        print(
            "Download available: https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chrome-linux64.zip"
        )

    chrome_driver = os.getenv("TOURIST__CHROME_DRIVER", "/tourist/browser/chromedriver")
    if not os.path.isfile(chrome_driver):
        ok = False
        print("Exiting because chromedriver wasn't found!")
        print("Set it with the environment variable: TOURIST__CHROME_DRIVER")
        print(
            "Download available: https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip"
        )

    if ok:
        uvicorn.run(
            "tourist.app:create_app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            factory=True,
        )
    else:
        sys.exit(1)


def main() -> None:
    app()
