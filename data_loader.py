import os
import pandas as pd
from pathlib import Path
import json
import urllib.request
import zipfile


class DataLoader:
    def __init__(self, path):
        self.path = path
        self.data = None

    @staticmethod
    def process_text_files(folder_path):
        topic_directory = Path(folder_path)
        file_paths = [str(file) for file in topic_directory.rglob("*") if file.is_file()]
        return file_paths

    def find_folders(self):
        folder_paths = {}
        for root, dirs, files in os.walk(self.path):
            for dir_name in dirs:
                folder_path = os.path.join(root, dir_name)
                folder_paths[dir_name]=self.process_text_files(folder_path)

        return folder_paths

    def read_text_files(self):
        """
        Reads the text files with the articles
        :return:
        """

        text_data = []
        data_dict = self.find_folders()
        for theme, file_list in data_dict.items():
            for file_path in file_list:
                with open(file_path, 'r') as file:
                    text = file.read()
                    text_data.append({
                        'file_id': os.path.splitext(os.path.basename(file_path))[0],
                        'theme': theme,
                        'content': text})
        self.data = pd.DataFrame(text_data)

    @staticmethod
    def filtered_news_articles(news_data):
        """
        It filters the additional articles to match the bbc news themes.
        :param news_data:
        :return: A DataFrame that contains the filtered news articles.
        """
        huffing_themes= ['BUSINESS','SPORTS', 'ENTERTAINMENT', 'POLITICS']
        theme_map = {'BUSINESS': 'business','SPORTS': 'sport',
                     'ENTERTAINMENT': 'entertainment',
                     'POLITICS': 'politics'}
        huffing_dataset = {'file_id':[], 'theme':[], 'content': []}
        for index, article  in enumerate(news_data):
            if article['category'] in huffing_themes:
                huffing_dataset['file_id'].append('h'+str(index))
                huffing_dataset['theme'].append(theme_map[article['category']])
                huffing_dataset['content'].append(article['headline'] + ' ' + article['short_description'])

        huffing_dataset_df = pd.DataFrame(huffing_dataset)
        huffing_dataset_df = huffing_dataset_df.sample(n=100)
        return huffing_dataset_df


    def enrich_data(self):
        """
        It adds more news articles to the initial news provided by bbc
        :return:
        """
        news_file = 'data/News_Category_Dataset_v3_Huffpost.json'
        news = []
        with open(news_file, 'r') as file:
            for line in file:
                news.append(json.loads(line))

        huffing_data_df = self.filtered_news_articles(news)
        self.data = pd.concat([self.data, huffing_data_df], ignore_index=True, sort=False)
        self.data['file_index'] = self.data.index

    @staticmethod
    def download_news_articles(self):
        url = "http://mlg.ucd.ie/files/datasets/bbc-fulltext.zip"
        extract_dir = "data"
        zip_path, _ = urllib.request.urlretrieve(url)
        with zipfile.ZipFile(zip_path, "r") as f:
            f.extractall(extract_dir)














