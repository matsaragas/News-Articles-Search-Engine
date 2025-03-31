import pandas as pd
from datasets import Dataset, load_from_disk


class TransformerSearchRetrieval:

    def __init__(self, model, data, save_embeddings=False):
        self.model = model
        self.data = data
        self.save_embeddings = save_embeddings
        self.data_with_embeddings = None
        self.loaded_embeddings = None

    def generate_embedding(self):
        """
        Generates embeddings for each article.
        :return:
        """
        dataset = Dataset.from_pandas(self.data)
        self.data_with_embeddings = dataset.map(lambda example: {
            'embeddings': self.model.encode(example['content'])})
        self.data_with_embeddings.add_faiss_index(column='embeddings')
        if self.save_embeddings:
            self.data_with_embeddings.save_faiss_index('embeddings', 'my_index.faiss')

        self.data_with_embeddings.drop_index('embeddings')
        self.data_with_embeddings.save_to_disk(dataset_path="bbc_news_data")

    def load_embeddings(self):
        self.data_with_embeddings = load_from_disk("../bbc_news_data")
        # Load the FAISS index
        print('Load Embeddings....')
        self.data_with_embeddings.load_faiss_index('embeddings', '../data/my_index.faiss')

    def dense_retrieval(self, query, top_k=100):
        """
        It returns the top_k most relevant articles to the provided search query
        :param query: the Search query
        :param top_k: the number of relevant documents to return
        :return: A DataFrame with the retrieved articles.
        """
        scores, retrieved_examples = self.data_with_embeddings.get_nearest_examples(
            'embeddings', self.model.encode(query), k=top_k)
        retrieved_examples['score'] = list(scores)
        retrieved_examples = pd.DataFrame(retrieved_examples)
        retrieved_examples.sort_values("score", ascending=True, inplace=True)
        retrieved_examples['dense_rank'] = range(1, len(retrieved_examples) + 1)
        return retrieved_examples

















