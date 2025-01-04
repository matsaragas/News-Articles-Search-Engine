import pandas as pd
from datasets import Dataset


class TransformerSearchRetrieval:

    def __init__(self, model, data, save_embeddings=False):
        self.model = model
        self.data = data
        self.save_embeddings = save_embeddings
        self.data_with_embeddings = None

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

















