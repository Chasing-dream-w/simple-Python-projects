"""提供词向量，计算余弦相似度"""

from data_base import Database
from text2vec import Word2Vec
from scipy import spatial

# 计算词向量余弦相似度
def compute_similarity(game1_vec, game2_vec):
    similarity_score = 1 - spatial.distance.cosine(game1_vec, game2_vec)
    return similarity_score


def load_model():
    w2v_model = Word2Vec("w2v-light-tencent-chinese")
    compute_emb(w2v_model)
    return w2v_model

def compute_emb(sentences)->list:
    # sentences是一个单元素的list
    model = load_model()
    sentence_embeddings = model.encode(sentences, show_progress_bar=True, normalize_embeddings=True)
    #print(type(sentence_embeddings), sentence_embeddings.shape)
    # The result is a list of sentence embeddings as numpy arrays
    # for sentence, embedding in zip(sentences, sentence_embeddings):
    #     print("Sentence:", sentence)
    #     print("Embedding shape:", embedding.shape)
    #     print("Embedding head:", embedding[:10])
    #     print()
    """返回游戏标签的向量"""
    return sentence_embeddings 


my_db = Database()
game_info = my_db.Get_Game_Info_No_Params()
game_similarity = []  # 存储游戏相似度



if __name__ == '__main__':
    # 示例：计算词向量
    w2v_model = Word2Vec("w2v-light-tencent-chinese")
    compute_emb(w2v_model)