import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core import Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


# from llama_index.core.schema import TextNode
import pandas as pd

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)

# Current CORS settings
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # This allows all origins
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# More specific CORS settings (recommended for production)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your frontend URL
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

df = pd.read_csv("imdb_movies-1.csv")

CHROMA_DB_PATH = "./chroma_db_data"

LLM_MODEL = "llama3.1:8b"
EMBED_MODEL = "mxbai-embed-large:latest"

llm = Ollama(model=LLM_MODEL, request_timeout=30.0)

embed_model = OllamaEmbedding(
    model_name=EMBED_MODEL,
    base_url="http://localhost:11434",
)

# Set global settings
Settings.llm = llm
Settings.embed_model = embed_model

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


@app.route('/api/chat/initialize', methods=['POST'])
def store_reviews_as_collection():

    try:
        data = request.json
        if not data or 'movie' not in data:
            return jsonify({'error': 'Movie data is required'}), 400

        movie = data['movie']
        id = movie['id']

        chroma_collection = chroma_client.get_or_create_collection(str(id) + '_reviews')
        documents = SimpleDirectoryReader(input_files=[f"data/reviews/{id}_reviews.txt"]).load_data()

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

        context = {
        'title': movie['title'],
        'overview': movie['overview'],
        'rating': movie['rating'],
        'genres': movie['genres'],
        'release_year': movie['release_year'],
        'language': movie['language'],
            'country': movie['country']
        }

        return jsonify({
            'status': 'success',
            'message': 'Chat initialized successfully',
            'context': context
        })

    except Exception as e:
        print(f"Error initializing chat: {str(e)}")
        return jsonify({'error': 'Failed to initialize chat'}), 500

def query_from_collection(id):

    chroma_collection = chroma_client.get_or_create_collection(str(id) + '_reviews')
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )

    return index
    

@app.route('/api/chat/query', methods=['POST'])
def query_collection():
    # index = store_reviews_as_collection(id)
    try:
        data = request.json
        if not data or 'movieId' not in data or 'question' not in data:
            return jsonify({'error': 'Movie ID and question are required'}), 400

        movie_id = data['movieId']
        question = data['question']

        index = query_from_collection(movie_id)
        
        response = index.as_query_engine(similarity_top_k=5).query(question)
        return jsonify({
            'role': 'assistant',
            'content': str(response)
        })
    
    except Exception as e:
        print(f"Error in chat query: {str(e)}")
        return jsonify({'error': 'Failed to process question'}), 500
    
def main():
    print(query_collection(13, "talk about the director and naming of this movie"))

if __name__ == "__main__":

    # main()
    print(f"Database path: {CHROMA_DB_PATH}")
    app.run(host='0.0.0.0', port=5001, debug=True) 