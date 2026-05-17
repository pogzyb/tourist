
### Deploying

Tourist can be deployed using the `ghcr.io/pogzyb/tourist-deploy` container.

Behind the scenes the deployment container uses [OpenTofu](https://opentofu.org/) to build and manage the Tourist infrastructure in your AWS account.

#### Prerequisites

1. AWS Account and Credentials (passed to container via `.env` or `-e`)
2. S3 Bucket for storing an OpenTofu statefile
3. Docker Daemon


Getting started:
```
docker run ghcr.io/pogzyb/tourist-deploy:latest --help
```

```
 Usage: deploy.py [OPTIONS] COMMAND [ARGS]...                                   
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ aws    Deploy tourist to AWS Lambda.                                         │
│ azure  Deploy tourist to Azure Container Apps.                               │
╰──────────────────────────────────────────────────────────────────────────────╯
```

#### Example

1. Deploying `tourist` in `app` mode into your AWS account:
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --env-file .env \
    ghcr.io/pogzyb/tourist-deploy:latest aws deploy \
    --state-bucket llmabda-statefile \
    --region us-east-1 \
    --mode app \
    --x-api-key secretKEy123
```

2. Destroying (removing the infrastructure):
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --env-file .env \
    ghcr.io/pogzyb/tourist-deploy:latest aws destroy \
    -b tourist-statefile
```

---

1. Deploying `tourist` in `mcp` mode into your Azure account:
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --env-file .env \
    ghcr.io/pogzyb/tourist-deploy:latest azure deploy \
    --tofu-resource-group "tofu-resource-group" \
    --tofu-storage-account-name "tofustatemanagment" \
    --tofu-container-name "statefiles" \
    --x-api-key "MySEECrTKey" \
    --mode mcp
```
