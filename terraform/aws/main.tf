# https://github.com/aws-samples/aws-sam-terraform-examples/tree/main/ga


data "aws_caller_identity" "current" {}

data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
    address  = "${data.aws_caller_identity.current.account_id}.dkr.ecr.us-east-1.amazonaws.com"
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project = "Tourist"
      Env     = var.env
    }
  }
}

terraform {

  // TODO/Contribution: support dynamic options/s3 backend
  backend "local" {
    path = "../statefile/local.tfstate"
  }

  required_version = ">= 0.13.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.19"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.12"
    }
  }
}