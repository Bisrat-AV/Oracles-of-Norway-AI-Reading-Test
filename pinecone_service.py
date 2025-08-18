import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

class PineconeService:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set.")
        
        self.pinecone = Pinecone(api_key=self.api_key)
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "oracles-of-norway")

        print(f"Connecting to Pinecone index: {self.index_name}")
        self.index = self.pinecone.Index(self.index_name)
        print("Successfully connected to Pinecone index.")

    def create_and_connect_index(self, dimension: int):
        """
        Checks if an index exists, creates it if it doesn't, and then connects.
        This should be called by the data processing script.
        """
        if self.index_name not in self.pinecone.list_indexes().names():
            print(f"Creating new Pinecone index: {self.index_name}")
            self.pinecone.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="dotproduct",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"Index {self.index_name} created successfully.")
        else:
            print(f"Pinecone index '{self.index_name}' already exists.")
        
        self.index = self.pinecone.Index(self.index_name)

    def upsert_card(self, id: str, dense_vector: list, sparse_vector: dict, metadata: dict):
        """
        Upserts a card with both dense and sparse vectors into the index.
        """
        self.index.upsert(
            vectors=[
                {
                    "id": id,
                    "values": dense_vector,
                    "sparse_values": sparse_vector,
                    "metadata": metadata,
                }
            ]
        )

    def query(self, dense_vector: list, top_k: int, sparse_vector: dict = None, filter: dict = None):
        """
        Performs a hybrid query on the index.
        """
        return self.index.query(
            vector=dense_vector,
            sparse_vector=sparse_vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )

pinecone_service = PineconeService()
