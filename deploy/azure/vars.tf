variable "x_api_key" {
  type = string
}

variable "mode" {
  type    = string
  default = "app"
}

variable "ghcr_uri" {
  type    = string
  default = "ghcr.io/pogzyb/tourist"
}

variable "project_name" {
  type    = string
  default = "tourist"
}

variable "resource_group_name" {
  type    = string
  default = "touristResourceGroup"
}

variable "container_registry_name" {
  type    = string
  default = "touristRegistry"
}

variable "storage_account_name" {
  type    = string
  default = "tourist"
}

variable "service_plan_name" {
  type    = string
  default = "touristServicePlan"
}

variable "region" {
  type    = string
  default = "eastus"
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "timeout" {
  type    = number
  default = 900
}
