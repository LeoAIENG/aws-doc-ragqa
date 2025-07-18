from vector_database.qdrant_vector_db_client import (
    initialize_qdrant,
    initialize_async_qdrant,
    qdrant_vector_store,
    qdrant_async_vector_store,
    get_qdrant_url,
    get_collection_name,
)


def set_vector_store(vector_db: str, model_provider: str, async_mode: bool):
    match vector_db:
        case "qdrant":
            url = get_qdrant_url()
            collection_name = get_collection_name(model_provider)
            if async_mode:
                client = initialize_async_qdrant(url=url)
                vector_store = qdrant_async_vector_store(
                    client=client, collection_name=collection_name
                )
            else:
                client = initialize_qdrant(url=url)
                vector_store = qdrant_vector_store(
                    client=client, collection_name=collection_name
                )
        case _:
            raise Exception("The vector database is not available.")
    return vector_store
