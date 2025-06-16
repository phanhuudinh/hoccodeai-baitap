import pandas as pd
import weaviate
from weaviate.classes.config import Property, DataType, Tokenization
from weaviate.embedded import EmbeddedOptions

embeadded_options = EmbeddedOptions(
    additional_env_vars={
        "ENABLE_MODULES": "backup-filesystem, text2vec-transformers",
        "BACKUP_FILESYSTEM_PATH": "/tmp/backups",
        "LOG_LEVEL": "panic",
        "TRANSFORMERS_INFERENCE_API": "http://localhost:8001",
    },
    persistence_data_path="data"
)

vector_db_client = weaviate.WeaviateClient(
    embedded_options=embeadded_options
)

vector_db_client.connect()
print(f"DB is ready: {vector_db_client.is_connected()}")

COLLECTION_NAME = "BookCollection"


def create_collection():
    book_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        # columns: title,author,description,grade,genre,lexile,path,is_prose,date,intro,excerpt,license,notes
        properties=[
            Property(name="title", data_type=DataType.TEXT, vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="author", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="description", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
            Property(name="grade", data_type=DataType.INT, skip_vectorization=True),
            Property(name="genre", data_type=DataType.TEXT, tokenization=Tokenization.WORD),
            Property(name="lexile", data_type=DataType.INT, skip_vectorization=True),
            Property(name="path", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="is_prose", data_type=DataType.INT, vectorize_property_name=False),
            Property(name="date", data_type=DataType.TEXT, vectorize_property_name=False),
            Property(name="intro", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
            Property(name="excerpt", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
            Property(name="license", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
            Property(name="notes", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
        ]
    )

    data = pd.read_csv('./books.csv')
    data.fillna({
        "lexile": 0,  # Fill NaN values in 'lexile' with 0
    }, inplace=True)

    sent_to_vector_db = data.to_dict(orient='records')
    total_records = len(sent_to_vector_db)
    print(f"Total records to insert: {total_records}")

    with book_collection.batch.dynamic() as batch:
        for record in sent_to_vector_db:
            batch.add_object(properties=record)

    print("Data inserted successfully!")


if vector_db_client.collections.exists(COLLECTION_NAME):
    print(f"Collection '{COLLECTION_NAME}' already exists.")
else:
    create_collection()

vector_db_client.close()
