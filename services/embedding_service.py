from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import joblib
import os

VECTORIZER_PATH = "data/tfidf_vectorizer.joblib"

class EmbeddingService:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.dense_model = SentenceTransformer(model_name)
        self.sparse_vectorizer = self._load_vectorizer()

    def _load_vectorizer(self):
        """Loads the TF-IDF vectorizer from disk if it exists."""
        if os.path.exists(VECTORIZER_PATH):
            print("Loading fitted TF-IDF vectorizer from disk.")
            return joblib.load(VECTORIZER_PATH)
        else:
            print("Vectorizer not found. Initializing a new one. It must be fitted before use.")
            return TfidfVectorizer()

    def fit_sparse_vectorizer(self, corpus):
        """
        Fits the TF-IDF vectorizer on the corpus and saves it to disk.
        """
        print("Fitting TF-IDF vectorizer on the corpus...")
        self.sparse_vectorizer.fit(corpus)
        joblib.dump(self.sparse_vectorizer, VECTORIZER_PATH)
        print(f"TF-IDF vectorizer fitted and saved to {VECTORIZER_PATH}.")

    def generate_embeddings(self, text):
        """
        Generates both dense and sparse vector embeddings for a given text.
        """
        # Generate dense vector
        dense_vector = self.dense_model.encode(text).tolist()

        # Generate sparse vector
        sparse_embedding = self.sparse_vectorizer.transform([text])
        
        # Convert sparse matrix to the format Pinecone expects
        indices = sparse_embedding.indices.tolist()
        values = sparse_embedding.data.tolist()
        
        sparse_vector = {
            "indices": indices,
            "values": values
        }

        return dense_vector, sparse_vector

embedding_service = EmbeddingService()
