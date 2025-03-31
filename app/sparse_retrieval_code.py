import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import spacy

from string import punctuation

spacy.load('en_core_web_sm')
STOP_WORDS = spacy.lang.en.stop_words.STOP_WORDS


class ElasticSearchRetrieval:
    def __init__(self, host, port=9200, scheme="http"):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.client = Elasticsearch([{'host': self.host, 'port': 9200, "scheme": "http"}],
                                    use_ssl=False)
        print("Client Information = \n", self.client.info())

    def set_index(self, index):
        self.index = index

    def available_indices(self):
        return self.client.indices.get_mapping()

    def index_exists(self, index):
        indices = self.available_indices()
        if index in indices:
            return True
        else:
            return False

    def delete_index(self, index):
        self.client.indices.delete(index= index, ignore=[400, 404])

    def create_bulk_payload(self, df, content_column, metadata_columns):
        """
        Create the bulk payload for the elasticsearch
        :param df:
        :param content_column:
        :param metadata_columns:
        :return:
        """
        bulk_upload = []
        for i , row in df.iterrows():

            payload = {
                '_index': self.index,
                '_id': row['file_index'],
                '_source': {"processed_text": row[content_column]}
            }
            metadata_payload = {}
            for column in metadata_columns:
                metadata_payload[column] = row[column]
            payload['_source'].update(metadata_payload)
            bulk_upload.append(payload)

        return bulk_upload

    def post_bulk_upload(self, df, content_column, metadata_columns):
        bulk_upload = self.create_bulk_payload(df, content_column, metadata_columns)
        if self.index_exists(self.index):
            print("Deleting Index as it is Already present!")
            self.delete_index(self.index)

        bulk(self.client, bulk_upload)
        print("Bulk Upload Complete")

    def remove_stop_words(self, sentence):
        """Removes the stop words from a sentence"""
        words = sentence.split(' ')
        words = [word for word in words if word not in STOP_WORDS and word not in list(punctuation)]
        return ' '.join(words)

    def search(self, match_dictionary, filter_dictionary=None, top_k = 5, filter_stop_words=True):
        """
        It performs the search operation in ElasticSearch
        :param match_dictionary: A dictionary with the search query
        :param filter_dictionary: Dictionary to filter the search universe
        :param top_k: the number of articles to return
        :param filter_stop_words:
        :return: A dataframe with the top_k identified articles
        """
        conditionals = []
        for k, v in match_dictionary.items():
            if filter_stop_words:
                v = self.remove_stop_words(v)

            clause = {"match": {k: v}}
            conditionals.append(clause)

        if filter_dictionary is not None:
            for k, v in filter_dictionary.items():
                clause = {"match_phrase": {k: v}}
                conditionals.append(clause)

        search_query = {"query": {
            "bool": {
                "must": conditionals
            }
        }
        }

        output = self.client.search(index = self.index, body = search_query, size = top_k)
        records = []
        for rank, hit in enumerate(output["hits"]["hits"]):
            record = {}
            record["id"] = hit["_id"]
            record["sparse_rank"] = rank + 1
            record["sparse_score"] = hit["_score"]
            for k, v in hit["_source"].items():
                record[k] = v
            records.append(record)

        return pd.DataFrame(records)


