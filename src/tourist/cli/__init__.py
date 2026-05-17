import os
import subprocess

import typer
import tourist


cli = typer.Typer(name="tourist")


# TODO: don't hardcode things like DISPLAY, host, and port here.
@cli.command()
def app():
    try:
        print(f"TOURIST🤳 [mode:APP v{tourist.__version__}]")
        cmd = "python -m uvicorn tourist.app:create_app --host 0.0.0.0 --port 8000 --workers 1 --log-level debug --factory"
        xvfb_run = f"xvfb-run -n 99 --server-args='-screen 0 1024x768x24' {cmd}"
        with subprocess.Popen(xvfb_run, shell=True) as process:
            process.wait()
    except:
        print("Running in APP mode. If seeing `ModuleNotFoundError`, try `pip install tourist[app]`")
        raise


@cli.command()
def mcp():
    try:
        print(f"TOURIST🤳 [mode:MCP v{tourist.__version__}]")
        cmd = "python -m uvicorn tourist.mcp:create_mcp --host 0.0.0.0 --port 8000 --workers 1 --log-level debug --factory"
        xvfb_run = f"xvfb-run -n 99 --server-args='-screen 0 1024x768x24' {cmd}"
        with subprocess.Popen(xvfb_run, shell=True) as process:
            process.wait()
    except:
        print("Running in MCP mode. If seeing `ModuleNotFoundError`, try `pip install tourist[mcp]`")
        raise


if __name__ == "__main__":
    cli()
