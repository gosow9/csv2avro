import yaml
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy import (
    BigInteger, Boolean, CHAR, Date, DateTime, Float, Integer, 
    LargeBinary, Numeric, SmallInteger, String, Text, Time, 
    TIMESTAMP, VARBINARY, VARCHAR
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoSuchTableError

class TableUpdater:
    """
    A class to create or update database tables based on a YAML schema and perform bulk data insertions.

    Attributes:
        engine (Engine): The SQLAlchemy engine to connect to the database.
        schema_file (str): Path to the YAML file containing the table schema.
        metadata (MetaData): MetaData instance bound to the engine.
        tables (dict): A dictionary to store SQLAlchemy table objects.
    """
    
    def __init__(self, engine, schema_file):
        """
        Initializes the TableUpdater with a database engine and a path to a YAML schema file.

        Args:
            engine (Engine): The SQLAlchemy engine to connect to the database.
            schema_file (str): Path to the YAML file containing the table schema.
        """
        self.engine = engine
        self.schema_file = schema_file
        self.metadata = MetaData(bind=self.engine)
        self.tables = {}

    type_mapping = {
        'BigInteger': BigInteger,
        'Boolean': Boolean,
        'CHAR': CHAR,
        'Date': Date,
        'DateTime': DateTime,
        'Float': Float,
        'Integer': Integer,
        'LargeBinary': LargeBinary,
        'Numeric': Numeric,
        'SmallInteger': SmallInteger,
        'String': String,
        'Text': Text,
        'Time': Time,
        'TIMESTAMP': TIMESTAMP,
        'VARBINARY': VARBINARY,
        'VARCHAR': VARCHAR
    }

    def load_schema(self):
        """
        Loads the table schema from the YAML file.

        Returns:
            list: A list of dictionaries representing the table schema.
        """
        with open(self.schema_file, 'r') as file:
            return yaml.safe_load(file)


    def create_or_update_table(self):
        """
        Creates new tables or updates existing ones based on the loaded YAML schema.
        """
        schemas = self.load_schema()
        for schema in schemas:
            table_name = schema['name']
            
            columns = []
            for col in schema['columns']:

                col_type = self.type_mapping[col['type']]
                if col.get('timezone'):
                    col_type = col_type(timezone=True)
                if 'foreign_key' in col:
                    columns.append(Column(col['name'], col_type, ForeignKey(col['foreign_key'])))
                else:
                    columns.append(Column(col['name'], col_type, primary_key=col.get('primary_key', False)))

            table = Table(table_name, self.metadata, *columns, extend_existing=True)
            self.tables[table_name] = table
            with self.engine.connect() as conn:
                trans = conn.begin()
                try:
                    table.create(conn, checkfirst=True)
                    trans.commit()
                    print("trans_commit")
                except exc.SQLAlchemyError as e:
                    print(f"Error creating table: {e}")
                    trans.rollback()

            # Check for new columns using database's information schema
            with self.engine.connect() as conn:
                insp = inspect(conn)
                existing_columns = [col['name'] for col in insp.get_columns(table_name)]
                print(f"Existing columns in '{table_name}': {existing_columns}")

                for column in columns:
                    if column.name not in existing_columns:
                        ddl = DDL(f"ALTER TABLE {table_name} ADD COLUMN {column.name} {column.type.compile(dialect=conn.dialect)}")
                        print(f"Adding column: {column.name}")
                        trans = conn.begin()  # Start a new transaction
                        try:
                            conn.execute(ddl)
                            trans.commit()  # Commit the transaction
                        except exc.SQLAlchemyError as e:
                            print(f"Error altering table: {e}")
                            trans.rollback()  # Rollback in case of error
                    else:
                        print(f"Column already exists: {column.name}")

    def bulk_insert_data(self, table_name, data):
        """
        Performs a bulk insert of data into a specified table.

        Args:
            table_name (str): The name of the table to insert data into.
            data (list of dict): The data to be inserted, represented as a list of dictionaries.
        
        Raises:
            ValueError: If the specified table is not initialized.
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not initialized. Call create_or_update_table first.")

        table = self.tables[table_name]
        table_columns = table.columns.keys()

        with self.engine.connect() as conn:
            for item in data:
                # Ensure all columns are present in the item, fill missing ones with None
                complete_item = {col: item.get(col, None) for col in table_columns}

                stmt = insert(table).values(**complete_item).on_conflict_do_nothing()
                conn.execute(stmt)