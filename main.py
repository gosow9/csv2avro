from utils.pg_connector import connect_with_connector
import pandas as pd
from bs4 import BeautifulSoup
import logging
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RAW_DATA_TABLE_NAME = "raw_documents"
PROCESSED_DATA_TABLE_NAME = "processed_documents"

def remove_tags(html):
    try:
        if html is None:
            return ""
        soup = BeautifulSoup(html, "html.parser")

        for data in soup(['style', 'script']):
            data.decompose()

        return ' '.join(soup.stripped_strings)
    except Exception as e:
        logging.error(f"Error in remove_tags: {e}")
        return html

def download_table_to_df(engine, raw_table_name, processed_table_name, limit=100):
    try:
        query = f"""SELECT *
                        FROM {raw_table_name} t1
                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM {processed_table_name} t2
                            WHERE t1.id = t2.id
                        )
                        LIMIT {limit};"""
        
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        logging.error(f"Error in download_table_to_df: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    logging.info("-"*20 + "Start of job" + "-"*20)
    try:
        processed_count = 0
        error_columns = []
        engine = connect_with_connector()
        while True:
            try:
                df = download_table_to_df(engine, 
                                          RAW_DATA_TABLE_NAME, 
                                          PROCESSED_DATA_TABLE_NAME, 
                                          limit=100)
                processed_count += len(df)
                if df.empty:
                    logging.info("No new data to process.")
                    break

                columns_to_clean = ['abstract_de', 'abstract_it', 'abstract_fr', 'content']
                for column in columns_to_clean:
                    try:
                        df[column] = df[column].apply(remove_tags)
                        
                    except Exception as column_error:
                        logging.error(f"Error processing column {column}: {column_error}")
                        error_columns.append(column)
                
                df.to_sql(PROCESSED_DATA_TABLE_NAME, 
                          engine, 
                          index=False, 
                          if_exists='append', 
                          chunksize=2000, 
                          method="multi")
                logging.info("Data processing and insertion completed successfully.")
            
            except SQLAlchemyError as sql_error:
                logging.error(f"SQLAlchemy error: {sql_error}")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                break


    except Exception as main_error:
        logging.error(f"Error in main: {main_error}")
    
    logging.info(f"Processed rows count: {processed_count}")
    if error_columns:
        logging.info(f"Rows that failed to process: {error_columns}")
    logging.info("-"*20 + "End of job" + "-"*20)
