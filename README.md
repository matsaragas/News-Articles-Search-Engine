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


## Enrich the News Data

* Step1: Download additional news data from Kaggle (Huffing Post data: https://www.kaggle.com/datasets/rmisra/news-category-dataset) and place the downloaded json file in the 
data folder that is created when we download the bbc news