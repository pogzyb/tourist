#!/usr/bin/env sh

# The tourist image needs to be in AWS ECR in the user's AWS account
docker login -u AWS -p $(aws ecr get-login-password --region $REGION) $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker tag ghcr.io/pogzyb/tourist:${TOURIST_VERSION:-latest} $REPO_URL:${TOURIST_VERSION:-latest}
docker push $REPO_URL:${TOURIST_VERSION:-latest}

# Sometimes the AWS lambda creation will fail because the image needs to exist for a few seconds before lambda can find it.
sleep 10s