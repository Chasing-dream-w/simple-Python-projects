---
frameworks:
- Pytorch
license: Apache License 2.0
tasks:
- sentence-similarity

model-type:
- word2vec

domain:
- nlp

language:
- cn 


tags:
- pretrained

---

腾讯词向量（Tencent AI Lab Embedding Corpus for Chinese Words and Phrases）提供了预训练好的800万中文词汇的word embedding（200维词向量），可以应用于很多NLP的下游任务。


- light_Tencent_AILab_ChineseEmbedding.bin, 轻量版腾讯词向量，二进制，111MB

---
语料具有以下特点：

- 覆盖面广：收录了许多领域专业词汇和常用俗语，如： “喀拉喀什河”, “皇帝菜”, “不念僧面念佛面”, “冰火两重天”, “煮酒论英雄" 等。
- 新颖：包括了最近出现的新词和流行词，如： “新冠病毒”, “元宇宙”, “了不起的儿科医生”, “流金岁月”, “凡尔赛文学”, “yyds” 等。
- 准确性高：基于大规模的预料以及精心设计的训练算法，能更准确地反映中文词语与短语的语义。

- 数据来源：新闻、网页、小说。
- 词表构建：维基百科、百度百科，以及Corpus-based Semantic Class Mining: Distributional vs. Pattern-Based Approaches论文中的方法发现新词。
- 训练方法：Directional Skip-Gram: Explicitly Distinguishing Left and Right Context for Word Embeddings论文中有介绍。

- 关于分词：可以使用任何开源分词工具，可以同时考虑细粒度和粗粒度的分词方式。
- 关于停用词、数字、标点：为了满足一些场景的需求，腾讯词向量并没有去掉这些，使用的时候需要自己构建词表并忽略其他无关词汇。


## 腾讯词向量使用举例
以查找近义词为例，介绍腾讯词向量的使用方法。

首先需要将已有的包含词和词向量的txt文件读入（使用KeyedVectors）

`keyedVectors`可以很方便地从训练好的词向量中读取词的向量表示，快速生成 {词：词向量}
其中binary=False，加载的是txt文件，binary=True，加载的是二进制文件，
然后构建词汇和索引的映射表，并用json格式离线保存，方便以后直接加载annoy索引时使用。


# usage
`pip install text2vec`


```py

from text2vec import Word2Vec


def compute_emb(model):
    # Embed a list of sentences
    sentences = [
        '卡',
        '银行卡',
        '如何更换花呗绑定银行卡',
        '花呗更改绑定银行卡',
        'This framework generates embeddings for each input sentence',
        'Sentences are passed as a list of string.',
        'The quick brown fox jumps over the lazy dog.',
        '敏捷的棕色狐狸跳过了懒狗',
    ]
    sentence_embeddings = model.encode(sentences, show_progress_bar=True, normalize_embeddings=True)
    print(type(sentence_embeddings), sentence_embeddings.shape)

    # The result is a list of sentence embeddings as numpy arrays
    for sentence, embedding in zip(sentences, sentence_embeddings):
        print("Sentence:", sentence)
        print("Embedding shape:", embedding.shape)
        print("Embedding head:", embedding[:10])
        print()


if __name__ == "__main__":
    # 中文词向量模型(word2vec)，中文字面匹配任务和冷启动适用
    w2v_model = Word2Vec("w2v-light-tencent-chinese")
    compute_emb(w2v_model)
```



