## News Articles Search Engine

In this repo, we have developed a search engine that allow users to identify news articles using search queries. 
The Engine is capable to also `identify the most similar articles` to the ones selected by the user. Finally, the search 
engine indicates `how novel a news article is` by comparing it to all the published articles so far.

# Solution

First, we load the news articles data used in `D. Greene and P. Cunningham. "Practical Solutions to the Problem of Diagonal Dominance in Kernel Document Clustering", Proc. ICML 2006` - http://mlg.ucd.ie/datasets/bbc.htmldata by running the method `download_news_articles` in the `data_loader` script. To enrich our dataset, we also incorporate the HuffingPost data, which can be found here https://www.kaggle.com/datasets/rmisra/news-category-dataset. Additionally, we could generate more data by paraphrasing the existing BBC data. However, due to time constraints, we will simply download additional news data from the web.

## Searching Approach
Our solution is based on a hybrid search approach, combining both sparse and dense retrievers. The Sparse retriever uses `ElasticSearch` to run the search query against all articles, identifying co-existing keywords and phrases between the search query and documents. The higher the number of hits (number of co-existing keywords/phrases between query and the articles), the higher the score returned by the sparse retriever, indicating that the documents are potentially relevant to the search query.

The dense retriever leverages embeddings extracted by a pre-trained transformer `sentence-transformers/nli-bert-large-max-pooling` (https://huggingface.co/sentence-transformers/nli-bert-large-max-pooling). This transformer generates embeddings for both the search query and each article. By calculating the cosine similairity score between the search query embedding and the embeddings of each article, we can identify documents that are semantically similar to the search query. A higher similarity score indicates a greater likelihood that the document is relevant to the search query.

The ranking results from the sparse and dense retriever are combined using the `Reciprocal Rank Fusion (RRF)` score. RRF ranks each article based on its position in both the sparse and dense retrieval rankings and then merges these rankings to produce a unified result list. The RRF score is calculated by summing the inverse rankings from each list, effectively integrating both retrieval approaches to enhance the relevance of the final results.

## Install packages

Python 3.8.8 was used to develop the search engine. Please follow the next steps to run the search approach:
* Step 1: Install ElasticSearch on you local machine. Download and 
install the pre-built packages based on the operating systems: https://www.elastic.co/downloads/past-releases/elasticsearch-7-17-9 
<br>
<br>
* Step 2: Once ElasticSearch is downloaded and unzipped, run the binary of it, here:

  ``` elasticsearch-7.17.9/bin/elasticsearch```

  When ElasticSearch is up and running successfully we will see the following in our terminal:
   ``` [2024-07-17T12:12:31,856][INFO ][o.e.h.AbstractHttpServerTransport] [Pet-Pav-Mac-Air.local] publish_address {127.0.0.1:9200}, bound_addresses {[::1]:9200}, {127.0.0.1:9200}```
<br>
<br>
* Step 3: Make sure the host and port (here, `port=9200` and `host=localhost`) is configured correctly in the python script `sparse_retrieval_code.py`
<br>
<br>
* Step 4: Installed all the python package by running the following command in terminal: `pip install -r requirements.txt`  
<br>
<br>
* Step5: Install the Spacy model `en_core_web_sm` by running the following python command on terminal: `python -m spacy download en_core_web_sm`



## Generate Data

To generate the data for the application:

1) Run script [`data_loader.py`](data/data_loader.py) to download the [`bbc news dataset`](http://mlg.ucd.ie/datasets/bbc.html)
2) Run Script [`data_initiation.py`](data/data_initiation.py) to load the text data into our sparse and dense retrievers.
## Enrich the News Data

* Step1: Download additional news data from Kaggle (Huffing Post data: https://www.kaggle.com/datasets/rmisra/news-category-dataset) and place the downloaded json file in the 
data folder that is created when we download the bbc news