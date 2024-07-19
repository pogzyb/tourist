import typer
import uvicorn

app = typer.Typer()


@app.command()
def serve():
    uvicorn.run(
        "tourist.app:create_app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        factory=True,
    )


def main() -> None:
    app()
