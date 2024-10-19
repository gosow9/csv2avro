# commands to build docker image

```cmd
build . --tag doc-html-cleaning
```

```cmd
docker tag doc-html-cleaning europe-west6-docker.pkg.dev/poc-entscheide-bot/cloud-run-source-deploy/doc-html-cleaning:latest
```

```cmd
docker push europe-west6-docker.pkg.dev/poc-entscheide-bot/cloud-run-source-deploy/doc-html-cleaning:latest
```
# Set environment variables
ENV PROJECT_ID=poc-entscheide-bot \
    PROJECT_REGION=europe-west1 \
    INSTANCE_NAME=vectorstore \
    DB_USER=pipeline \
    DB_PASS=Blender13== \
    DB_NAME=pgvector_weu_dev


docker pull \
    europe-west6-docker.pkg.dev/poc-entscheide-bot/cloud-run-source-deploy/doc-html-cleaning:latest