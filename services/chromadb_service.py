from chromadb.config import Settings
import chromadb
import uuid
import streamlit as st

# Initialize ChromaDB
chroma_client = chromadb.Client(Settings(allow_reset=True,is_persistent=True))

# Get or create collection instead of just creating
try:
    collection = chroma_client.get_collection(name="documents")
except:
    collection = chroma_client.create_collection(name="documents", metadata={"hnsw:space": "cosine"})

def save_document_to_chroma(content, metadatas, embeddings):
    try:
        document_id = str(uuid.uuid4())
        collection.add(
            ids=[document_id],
            documents=[content],
            metadatas=[metadatas],
            embeddings=[embeddings],
        )

        print(f"Document stored successfully with ID: {document_id}")
        return document_id

    except Exception as e:
        print(f"Failed to store document in ChromaDB: {e}")
        return None

def retrieve_document_from_chroma(document_id):
   
    try:
    
        results = collection.get(ids=[document_id])

        if results:
            document_content = results["documents"][0]
            metadata = results["metadatas"][0]

            print("Document retrieved successfully!")
            return {
                "content": document_content,
                "metadata": metadata,
            }
        else:
            print("No document found with the provided ID.")
            return None

    except Exception as e:
        print(f"Failed to retrieve document from ChromaDB: {e}")
        return None


def list_documents():
    try:
        # Get all documents from the collection
        results = collection.get()
        documents = {}
        for i, metadata in enumerate(results['metadatas']):
            if metadata:
                file_name = metadata.get('file_name')
                if file_name:
                    if file_name not in documents:
                        documents[file_name] = {
                            'file_name': file_name,
                            'file_type': metadata.get('file_type'),
                            'metadata': metadata,
                            'chunk_count': 1,
                            'id': results['ids'][i]
                        }
                    else:
                        documents[file_name]['chunk_count'] += 1
        
        return {
            "total_documents": len(documents),
            "documents": list(documents.values())
        }
    except Exception as e:
       print("Exception")

def retrieve_matching_documents(query_embeddings, policy_type, top_k=20):
    try:
        # Query ChromaDB for matching documents
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=top_k,
        )
        # Ensure the necessary keys exist in results
        if "documents" not in results or "metadatas" not in results or "distances" not in results:
            print("Error: Missing required result fields")
            return []

        # Process and filter results by policy_type
        matches = []
        for i in range(len(results["documents"])):
            document_metadata = results["metadatas"][i]
    
            # Filter by policy_type
            if document_metadata[0].get("policy_type") == policy_type:
                matches.append({
                    "content": results["documents"][i],
                    "metadata": document_metadata,
                    "score": results["distances"][i],
                })
           
        return matches

    except Exception as e:
        print(f"Error retrieving matching documents: {e}")
        return []

    except Exception as e:
        print(f"Failed to retrieve matching documents: {e}")
        return []
    
def reset_chroma_db():
    try:
        chroma_client.reset()
        chroma_client.create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        st.success("Database reset successful")
    except Exception as e:
        st.error(e)




