import chromadb

from datetime import datetime

import uuid 

# Initialize Chroma client and collection
chroma_client = chromadb.Client()
try:
    collection = chroma_client.get_collection(name="documents")
except:
    collection = chroma_client.create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )
def store_document(content, metadata, embeddings):
    """
    Stores a document's content, metadata, and embeddings in ChromaDB.

    Args:
        content (str): The content of the document.
        metadata (dict): Metadata about the document (e.g., file name, type).
        embeddings (list): The embeddings of the document content.
    
    Returns:
        str: The unique ID of the stored document.
    """
    try:
        # Generate a unique document ID
        document_id = str(uuid.uuid4())

        # Add the document to ChromaDB
        collection.add(
            ids=[document_id],
            documents=[content],
            metadatas=[metadata],
            embeddings=[embeddings],
        )

        print(f"Document stored successfully with ID: {document_id}")
        return document_id

    except Exception as e:
        print(f"Failed to store document: {e}")
        return None


def retrieve_document_by_id(document_id):
    """
    Retrieves a document by its unique ID from ChromaDB.

    Args:
        document_id (str): The unique ID of the document to retrieve.

    Returns:
        dict: A dictionary containing the document content, metadata, and embeddings.
    """
    try:
        # Query ChromaDB for the document by ID
        results = collection.get(ids=[document_id])

        if not results['documents']:
            print("No document found with the given ID.")
            return None

        # Return the document data
        return {
            "content": results["documents"][0],
            "metadata": results["metadatas"][0],
            "embeddings": results["embeddings"][0],
        }

    except Exception as e:
        print(f"Failed to retrieve document: {e}")
        return None


def retrieve_similar_documents(query_embedding, top_n=5):
    """
    Retrieves the top N most similar documents based on the query embedding.

    Args:
        query_embedding (list): The embedding of the query content.
        top_n (int): The number of similar documents to retrieve.

    Returns:
        list: A list of dictionaries containing the content, metadata, and similarity scores of the top N similar documents.
    """
    try:
        # Perform a similarity search in ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_n,
        )

        similar_docs = []
        for i in range(len(results["documents"])):
            similar_docs.append({
                "content": results["documents"][i],
                "metadata": results["metadatas"][i],
                "score": results["distances"][i],  # Lower scores indicate higher similarity
            })

        return similar_docs

    except Exception as e:
        print(f"Failed to retrieve similar documents: {e}")
        return []

# Example Usage
if __name__ == "__main__":
    # Example metadata and content
    example_content = "This is an example document."
    example_metadata = {
        "file_name": "example.pdf",
        "file_type": "application/pdf",
        "timestamp": datetime.now().isoformat(),
    }

    # Example embedding (mock data)
    example_embedding = [0.1, 0.2, 0.3, 0.4]  # Replace with real embedding

    # Store the document
    document_id = store_document(example_content, example_metadata, example_embedding)

    # Retrieve the document by ID
    if document_id:
        retrieved_doc = retrieve_document_by_id(document_id)
        print("Retrieved Document:", retrieved_doc)

    # Perform similarity search
    query_embedding = [0.1, 0.2, 0.3, 0.4]  # Replace with real query embedding
    similar_docs = retrieve_similar_documents(query_embedding, top_n=3)
    print("Similar Documents:", similar_docs)
