from app.sparse_retrieval_code import ElasticSearchRetrieval
from sentence_transformers import SentenceTransformer
from app.dense_retriever_code import TransformerSearchRetrieval
import pandas as pd
import os


class DataInit:

    def __init__(self, data_path: str, llm_model: str):
        self.data_path = data_path
        self.llm_model = llm_model
        self.data = None

    def load_data(self):
        self.data = pd.read_excel(self.data_path)

    def initialize_sparse_retriever(self) -> None:
        """
        Initialize the sparse retriever using ElasticSearch
        :return:
        """
        sparse_retriever = ElasticSearchRetrieval(host='localhost')
        sparse_retriever.set_index('bbc_news')
        sparse_retriever.post_bulk_upload(
            self.data, 'content', metadata_columns=['file_id', 'theme', 'file_index'])

    def initialize_dense_retriever(self) -> None:
        """
        Initialize the dense retriever using open-source LLMs
        :return:
        """
        model = SentenceTransformer(self.llm_model)
        dense_retriever = TransformerSearchRetrieval(model, self.data, save_embeddings=True)
        dense_retriever.generate_embedding()


if __name__ == "__main__":
    data_path = "news_articles.xlsx"
    llm_model = "nli-bert-large-max-pooling"
    embeddings_file = "my_index.faiss"
    ds = DataInit(data_path, llm_model)
    ds.load_data()
    ds.initialize_sparse_retriever()
    if not os.path.exists(embeddings_file):
        ds.initialize_dense_retriever()



