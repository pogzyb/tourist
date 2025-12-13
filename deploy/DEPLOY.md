
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
Tourist setup script.

positional arguments:
  {apply,destroy,plan}  The OpenTofu action to perform.

options:
  -h, --help            show this help message and exit
  -b STATE_BUCKET, --state-bucket STATE_BUCKET
                        This AWS S3 bucket stores the statefile. This should
                        be created in your AWS account as a prerequisite to
                        deploying.
  -g REGION, --region REGION
                        The AWS region where to deploy the resources.
  -n NAME_PREFIX, --name-prefix NAME_PREFIX
                        A custom prefix you can add to the name of the
                        infrastructure resources that are created.
  -k X_API_KEY, --x-api-key X_API_KEY
                        The value of the X-API-KEY header used to authorize
                        use of the endpoint.
```

#### Example

1. Deploying the infrastructure into your AWS account:
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --env-file .env \
    ghcr.io/pogzyb/tourist-deploy:latest \
    apply \
    -b tourist-statefile \
    -k SeCretTK3y
```

2. Destroying (removing the infrastructure):
```
docker run \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --env-file .env \
    ghcr.io/pogzyb/tourist-deploy:latest \
    destroy \
    -b tourist-statefile
```