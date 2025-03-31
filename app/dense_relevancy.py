import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class DenseSimilarity:

    def __init__(self, dense_retriever):
        self.data = dense_retriever

    def semantic_similarity(self):
        df_embed = pd.DataFrame(self.data.data_with_embeddings)
        cos_sim_theme_dict = {}
        unique_themes = list(df_embed['theme'].unique())
        for theme in unique_themes:
            theme_df = df_embed[df_embed['theme'] == theme]
            cos_sim_theme = cosine_similarity(np.vstack(theme_df['embeddings'].values))
            cos_sim_theme_df = pd.DataFrame(cos_sim_theme, index = theme_df['file_index'], columns=theme_df['file_index'])
            cos_sim_theme_dict[theme] = cos_sim_theme_df

        return cos_sim_theme_dict

