api_name           = "tourist"
env                = "main"
auth_function_name = "tourist-auth"
app_function_name  = "tourist-app"
ecr_repo_name      = "tourist"
region             = "us-east-1"

# You should update this value to something secret!
auth_secret_value = "supersecret"

# IMPORTANT: this is mounted into the container from a path on your machine.
# Check the docker-compose.yml file.
statefile_path = "../statefile/local.tfstate"

# View latest tags here: https://github.com/pogzyb/tourist/releases
image_tag         = "latest"
push_image_to_ecr = true
