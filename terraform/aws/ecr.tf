module "docker_image_in_ecr" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo  = true
  image_tag        = var.image_tag
  docker_file_path = "../../Dockerfile.main"
  source_path      = "../../"
  platform         = "linux/amd64"

  ecr_repo = var.ecr_repo_name
  ecr_repo_lifecycle_policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Keep only the last 2 images",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 2
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })
}