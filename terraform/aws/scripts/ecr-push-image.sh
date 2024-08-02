# The tourist image needs to be in AWS ECR in the user's AWS account, 
# so we pull it from github, tag it, and push it to ECR.
# docker pull ghcr.io/pogzyb/tourist:${TOURIST_VERSION}
docker pull ghcr.io/pogzyb/czdsdump:0.1.0
docker login -u AWS -p $(aws ecr get-login-password --region $REGION) $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker tag ghcr.io/pogzyb/czdsdump:0.1.0 $REPO_URL:$TOURIST_VERSION
docker push $REPO_URL:$TOURIST_VERSION