from sparse_retrieval_code import ElasticSearchRetrieval
from dense_retriever_code import TransformerSearchRetrieval
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from sparse_relevancy import SparseSimilarity
from dense_relevancy import DenseSimilarity
from typing import List, Dict
import spacy
from collections import defaultdict


class SearchEngine:

    def __init__(self, dense_llm_model: str, data_path: str):
        self.dense_llm_model = dense_llm_model
        self.data = pd.read_excel(data_path)
        self.nlp = spacy.load("en_core_web_sm")
        self.sparse_retriever = None
        self.dense_retriever = None
        self.sparse_cos_similarity = None
        self.dense_cos_similarity = None
        self.novelty_scores = None

    def initialize_sparse_retriever(self, query, top_k=100):
        """
        Initialize the sparse retriever using ElasticSearch
        :return:
        """
        self.sparse_retriever = ElasticSearchRetrieval(host='localhost')
        self.sparse_retriever.set_index('bbc_news')
        sparse_data = self.sparse_retriever.search(match_dictionary={"processed_text": query}, top_k=top_k)
        return sparse_data

    def calculate_sparse_similarity(self):
        sparse_similarity = SparseSimilarity(self.data)
        self.sparse_cos_similarity = sparse_similarity.sparse_cosine_similarity()

    def calculate_dense_similarity(self):
        dense_similarity = DenseSimilarity(self.dense_retriever)
        self.dense_cos_similarity = dense_similarity.semantic_similarity()

    def initialize_dense_retriever(self):
        """
        Initialize the dense retriever using open-source LLMs
        :return:
        """
        model = SentenceTransformer(self.dense_llm_model)
        self.dense_retriever = TransformerSearchRetrieval(model, self.data, save_embeddings=True)
        self.dense_retriever.load_embeddings()

    def estimate_novelty_scores(self):
        self.novelty_scores = self.novelty_score(self.dense_cos_similarity, self.sparse_cos_similarity)

    def get_top_n_columns(self, df, n):
        """
        It ranks the columns of a dataframe for each row to identify the top n
        most relevant news articles.
        """
        sorted_df = pd.DataFrame(np.sort(df.values)[:, ::-1][:, :n],
                                 index=df.index, columns=range(n))
        return sorted_df

    def novelty_score(self, dense_cosine_sim, sparse_cosine_sim):
        """
        It estimates the novelty score for each news article.
        """
        alpha = 0.4
        novelty_score_dict = {}
        for (d1, dense_sim), (d2, sparse_sim) in zip(dense_cosine_sim.items(), sparse_cosine_sim.items()):
            row_means_dense = alpha * self.get_top_n_columns(dense_sim, 10).mean(axis=1)
            row_means_sparse = (1-alpha) * self.get_top_n_columns(sparse_sim, 10).mean(axis=1)
            novelty_score_dict[d1] = pd.DataFrame({'file_index': dense_sim.index,
                                                   'novelty_score': (((1 - row_means_dense) +
                                                                      (1 - row_means_sparse))/2)})
        return novelty_score_dict

    def article_relevancy(self, extraction_row):
        """
        It estimates the novelty score for a particular news article.
        """
        novelty_score = self.novelty_scores[extraction_row['theme']].loc[extraction_row['file_index']].values[1]
        return novelty_score

    def reciprocal_ranking_fusion(self, sparse_rank, dense_rank):
        """
        It calculates the Reciprocal Ranking Fusion score from the rankings generated from the
        dense and sparse retriever.
        """
        alpha = 0.5
        rrf_score = 1 / (alpha/int(sparse_rank) + (1-alpha)/int(dense_rank))
        return rrf_score

    def hybrid_retrieval(self, query, top_k=100):
        """
        It estimates the reciprocal rank fusion score and return the most
        relevant news articles to the provided search query.
        """
        self.initialize_dense_retriever()
        dense_data = self.dense_retriever.dense_retrieval(query, top_k=top_k)
        sparse_data = self.initialize_sparse_retriever(query, top_k=top_k)
        if (sparse_data.shape[0] > 0) and (dense_data.shape[0] > 0):
            final_df = sparse_data.merge(dense_data, on='file_index', how="inner", suffixes=("", "_dense"))
            if final_df.shape[0] == 0:
                final_df = sparse_data
            else:
                final_df['rrf_score'] = final_df.apply(
                    lambda row: self.reciprocal_ranking_fusion(row["sparse_rank"], row['dense_rank']), axis=1)
                final_df = final_df.sort_values(by='rrf_score').reset_index(drop = True)
                final_df['relevance'] = 1 - (final_df['rrf_score']/sum(final_df['rrf_score']))
        elif (sparse_data.shape[0] == 0) and (dense_data.shape[0] == 0):
            final_df = pd.DataFrame()
        elif dense_data.shape[0] == 0:
            final_df = sparse_data
        else:
            final_df = dense_data
        return final_df

    def identify_relevant_news(self, news_id, topic, top_k=3):
        """
        It returns the top_k relevant news articles to the provided news article with
        id news_id.
        """
        selected_row = self.dense_cos_similarity[topic].loc[news_id]
        ranked_columns = selected_row.rank(ascending=False)
        resulted_df = pd.DataFrame({'Relevance': selected_row, 'Ranks': ranked_columns})
        resulted_df = resulted_df.sort_values(by='Ranks').iloc[1:]
        resulted_df.reset_index(inplace=True)
        data_theme = self.data[self.data['theme'] == topic][['file_index', 'content']]
        resulted_df = resulted_df.merge(data_theme, on='file_index')
        return resulted_df

    def entity_recognition(self, text):
        """
        It performs named entity recognition (NER) for the provided text.
        """
        doc = self.nlp(text)
        entities = defaultdict(set)
        for ent in doc.ents:
            entities[ent.label_].add(ent.text)
        return entities

    def search_engine(self, search_term: str) -> List[Dict]:
        """
        Your should include a working function implementation here, this takes in a search string and finds the most relevant articles;
        returning a list of the form given in the task introduction
        {'topic':'your_topic_here', 'relevance': 0.1, 'novelty': 0.1, 'article': full_article_object}
        e.g.
        :param search_term: string containing the search
        :return:            list of result objects as detailed above
        """
        response = self.hybrid_retrieval(search_term, top_k=100)
        response.rename(columns={'theme': 'topic', 'content': 'article'}, inplace=True)
        response_dict = response[['file_index', 'topic', 'article']].to_dict('records')
        response_extra = [d for d in response_dict]
        return response_extra

