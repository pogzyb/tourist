#!/usr/bin/env python3

import os
import shlex
import subprocess
import sys
from textwrap import dedent
from typing import Annotated, Literal, Any

import typer

app = typer.Typer()

aws_app = typer.Typer()
azure_app = typer.Typer()

app.add_typer(aws_app, name="aws", help="Deploy tourist to AWS Lambda.")
app.add_typer(azure_app, name="azure", help="Deploy tourist to Azure Container Apps.")


def run_command(cmd: str, extra_env: dict[str, Any] | None = None):
    env = os.environ
    if extra_env:
        env.update(env)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        shell=True,
        env=env,
    )
    for line in process.stdout:
        print(f">>> {line.strip()}")
        sys.stdout.flush()
        if process.stderr:
            for line in process.stderr:
                print(f"STDERR: {line.strip()}")
                sys.stderr.flush()
    return_code = process.wait()
    if return_code != 0:
        raise Exception(f"Command '{cmd}' failed with exit code {return_code}")


def docker_pull(provider: str, mode: str):
    if provider == "aws" and mode == "mcp":
        raise Exception("MCP mode is not supported for AWS deployment.")
    run_command(f"docker pull ghcr.io/pogzyb/tourist-{provider}-{mode}:latest")


@aws_app.command("deploy")
def aws_deploy(
    state_bucket: Annotated[str, typer.Option()],
    region: Annotated[str, typer.Option()],
    x_api_key: Annotated[str, typer.Option()],
    mode: Annotated[str, typer.Option()],
    name_prefix: Annotated[str, typer.Option()] = "tourist",
    count: Annotated[int, typer.Option()] = 1,
    plan: Annotated[bool, typer.Option()] = False,
):
    docker_pull("aws", mode)
    cmd_init = f"""\
tofu -chdir=aws init \
    -backend-config="region={region}" \
    -backend-config="bucket={state_bucket}" \
    -backend-config="key=tourist.tfstate"
"""
    run_command(cmd_init)
    action = "plan" if plan else "apply"
    cmd_action = f"""\
tofu -chdir=aws {action} \
    -var-file="tourist.tfvars" \
    -var="x_api_key={x_api_key}" \
    -var="region={region}" \
    -var="project_name={name_prefix}" \
    -var="num_functions={count}" \
    -var="mode={mode}" \
    -auto-approve -input=false
"""
    run_command(cmd_action)


@aws_app.command("destroy")
def aws_destroy(
    state_bucket: Annotated[str, typer.Option()],
):
    cmd_init = f"""\
tofu -chdir=aws init \
    -backend-config="region={region}" \
    -backend-config="bucket={state_bucket}" \
    -backend-config="key=tourist.tfstate"
"""
    run_command(cmd_init)
    cmd_action = f"""\
tofu -chdir=aws destroy \
    -var-file="tourist.tfvars" \
    -auto-approve -input=false
"""
    run_command(cmd_action)


@azure_app.command("deploy")
def azure_deploy(
    tofu_resource_group: Annotated[str, typer.Option()],
    tofu_storage_account_name: Annotated[str, typer.Option()],
    tofu_container_name: Annotated[str, typer.Option()],
    x_api_key: Annotated[str, typer.Option()],
    mode: Annotated[str, typer.Option()],
    name_prefix: Annotated[str, typer.Option()] = "tourist",
    plan: Annotated[bool, typer.Option()] = False,
):
    docker_pull("azure", mode)
    run_command("tofu -chdir=azure fmt")
    cmd_init = f"""\
tofu -chdir=azure init \
    -backend-config="resource_group_name={tofu_resource_group}" \
    -backend-config="storage_account_name={tofu_storage_account_name}" \
    -backend-config="container_name={tofu_container_name}" \
    -backend-config="key=tourist.tfstate"
    """
    run_command(cmd_init)

    action = "plan" if plan else "apply"
    env = {
        "TF_VAR_ARM_CLIENT_ID": os.getenv("ARM_CLIENT_ID"),
        "TF_VAR_ARM_CLIENT_SECRET": os.getenv("ARM_CLIENT_SECRET"),
        "TF_VAR_ARM_TENANT_ID": os.getenv("ARM_TENANT_ID"),
    }
    cmd_action = f"""\
tofu -chdir=azure {action} \
    -var-file="tourist.tfvars" \
    -var="x_api_key={x_api_key}" \
    -var="project_name={name_prefix}" \
    -var="mode={mode}" \
    -auto-approve -input=false
    """
    run_command(cmd_action, env)


@azure_app.command("destroy")
def azure_destroy(
    tofu_resource_group: Annotated[str, typer.Option()],
    tofu_storage_account_name: Annotated[str, typer.Option()],
    tofu_container_name: Annotated[str, typer.Option()],
):
    cmd_init = f"""\
tofu -chdir=azure init \
    -backend-config="resource_group_name={tofu_resource_group}" \
    -backend-config="storage_account_name={tofu_storage_account_name}" \
    -backend-config="container_name={tofu_container_name}" \
    -backend-config="key=tourist.tfstate"
    """
    run_command(cmd_init)
    cmd_action = f"""\
tofu -chdir=azure destroy \
    -var-file="tourist.tfvars" \
    -var="x_api_key=na" \
    -var="project_name=na" \
    -var="mode=na" \
    -input=false -auto-approve
    """
    run_command(cmd_action)


if __name__ == "__main__":
    app()
