# Webapp für Entscheidunge POC

## Getting started

1. Create a virtualenv and install the requirements:

    ```bash
    python -m venv venv
    source venv/bin/activate
    python -m pip install -r requirements-dev.txt
    ```

2. Set required environment variables `SECRET_KEY`, `OPENAI_API_KEY` and
`SQLALCHEMY_DATABASE_URI` (`.env` files are supported).

3. Run the app in development mode:

    ```bash
    flask --app caseweb run --debug
    ```

## Deployment

Deploy to Google Cloud Run (project `poc-entscheide-bot`) using cloudbuild:

```bash
gcloud builds submit --project=poc-entscheide-bot
```

App URL: https://poc-web-6rxjtc7neq-oa.a.run.app/

## FAQ

### How to copy Cloud SQL database to local machine?

Start Cloud SQL proxy:

```bash
cloud-sql-proxy --port 54321 poc-entscheide-bot:europe-west1:vectorstore
```

Dump schema:

```bash
pg_dump --schema-only --no-owner --no-acl --host=127.0.0.1 --port=54321 --user=<USER> pgvector_weu_prod > pgvector_weu_prod_schema.sql
```

Dump data:

```bash
pg_dump --data-only --no-owner --no-acl --host=127.0.0.1 --port=54321 --user=<USER> pgvector_weu_prod > pgvector_weu_prod_data.sql
```

Then import the schema and data into the local database.
