variable "api_name" {
  type = string
}

variable "env" {
  type = string
}

# TODO/Contribution: modularize and add domain name.
variable "domain_name" {
  type    = string
  default = ""
}

variable "app_function_name" {
  type = string
}

variable "auth_function_name" {
  type = string
}

variable "ecr_repo_name" {
  type = string
}

variable "image_tag" {
  type = string
}

variable "push_image_to_ecr" {
  type = bool
}

variable "region" {
  type = string
}

variable "statefile_path" {
  type = string
}