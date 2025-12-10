#!/usr/bin/env python3

import argparse
import shlex
import subprocess
import sys
from textwrap import dedent
from typing import Literal


def run_command(cmd: str):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        shell=True,
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


def docker_tag():
    run_command("docker pull ghcr.io/pogzyb/tourist:latest")


def run_tofu(
    action: Literal["apply", "plan", "destroy"],
    x_api_key: str,
    bucket: str,
    prefix: str,
    region: str,
):
    cmd_init = f'tofu init -backend-config="region={region}" -backend-config="bucket={bucket}" -backend-config="key=tourist.tfstate"'
    run_command(cmd_init)
    cmd_action = f'tofu {action} -var-file="tourist.tfvars" -var="x_api_key={x_api_key}" -var="region={region}" -var="project_name={prefix}"'
    cmd_action = (
        cmd_action + " -input=false -auto-approve" if action != "plan" else cmd_action
    )
    run_command(cmd_action)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tourist setup script.")
    parser.add_argument(
        "action",
        help="The OpenTofu action to perform.",
        choices=["apply", "destroy", "plan"],
    )
    parser.add_argument(
        "-b",
        "--state-bucket",
        help="This AWS S3 bucket stores the statefile. This should be created in your AWS account as a prerequisite to deploying.",
        required=True,
    )
    parser.add_argument(
        "-g",
        "--region",
        help="The AWS region where to deploy the resources.",
        default="us-east-1",
    )
    parser.add_argument(
        "-n",
        "--name-prefix",
        help="A custom prefix you can add to the name of the infrastructure resources that are created.",
        default="tourist",
    )
    parser.add_argument(
        "-k",
        "--x-api-key",
        help="The value of the X-API-KEY header used to authorize use of the endpoint.",
        default=None,
    )
    args = parser.parse_args()

    if args.action == "apply":
        # Check for x-api-key
        if args.x_api_key is None:
            raise Exception(
                "The --x-api-key value is missing. This is required to secure your endpoint."
            )
        # Prepare the tourist docker image for the user's ECR repository
        docker_tag()

    # Run tofu
    run_tofu(
        args.action, args.x_api_key, args.state_bucket, args.name_prefix, args.region
    )
