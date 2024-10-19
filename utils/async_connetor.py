import os
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector


async def async_con():
    loop = asyncio.get_running_loop()
    project_id = os.environ.get("PROJECT_ID", "default_value")
    region = os.environ.get("PROJECT_REGION", "default_value")
    instance_name = os.environ.get("INSTANCE_NAME", "default_value")
    instance_connection_name = f"{project_id}:{region}:{instance_name}"
    db_user = os.environ.get("DB_USER", "default_user")
    db_pass = os.environ.get("DB_PASS", "default_password")
    db_name = os.environ.get("DB_NAME", "default_db")
    
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database
        conn: asyncpg.Connection = await connector.connect_async(
            instance_connection_name,
            "asyncpg",
            user=f"{db_user}",
            password=f"{db_pass}",
            db=f"{db_name}"
        )
        return conn