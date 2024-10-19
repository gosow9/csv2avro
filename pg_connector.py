import os
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
import pg8000

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres using environment variables.

    This function uses the Cloud SQL Python Connector package to establish a connection
    to a PostgreSQL database. It retrieves database connection details from environment variables.

    Returns:
        sqlalchemy.engine.base.Engine: An SQLAlchemy engine instance connected to the specified database.
    """
    # Retrieve connection details from environment variables
    project_id = os.environ.get("PROJECT_ID", "default_value")
    region = os.environ.get("PROJECT_REGION", "default_value")
    instance_name = os.environ.get("INSTANCE_NAME", "default_value")
    instance_connection_name = f"{project_id}:{region}:{instance_name}"
    db_user = os.environ.get("DB_USER", "default_user")
    db_pass = os.environ.get("DB_PASS", "default_password")
    db_name = os.environ.get("DB_NAME", "default_db")
    ip_type = IPTypes.PUBLIC  # or use os.environ.get("IP_TYPE", "PUBLIC") if you want to set it via env

    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        """
        Creates a database connection using the Cloud SQL Connector.

        Returns:
            pg8000.dbapi.Connection: A connection object to the PostgreSQL database.
        """
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool