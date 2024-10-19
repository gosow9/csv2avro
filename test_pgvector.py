import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector


DATABASE=os.environ.get("DB_NAME", "postgres")
USER=os.environ.get("DB_USER", "postgres")
PASSWORD=os.environ.get("DB_PASS", "postgres")
COLLECTION_NAME = "main_vectore_store"
CONNECTION_STRING = f"postgresql+pg8000://{USER}:{PASSWORD}@127.0.0.1:5432/{DATABASE}"

embeddings = OpenAIEmbeddings()
store = PGVector(
    collection_name=COLLECTION_NAME,
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
)


if __name__ == "__main__":
    query = "Eine strafe fürs velo fahren auf der autobahn"
    docs_with_score = store.similarity_search_with_score(query)
    for doc, score in docs_with_score:
        print("-" * 80)
        print("Score: ", score)
        print(doc.page_content)
        print("-" * 80)