variable "x_api_key" {
  type = string
}

variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "cloudwatch_logs_retention_in_days" {
  type    = number
  default = 14
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "timeout" {
  type    = number
  default = 900
}

variable "memory_size" {
  type    = number
  default = 1024 * 10
}

variable "num_functions" {
  type = number
  default = 1
}