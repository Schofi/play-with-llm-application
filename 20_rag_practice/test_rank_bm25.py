import jieba
from rank_bm25 import BM25Okapi

# 示例文档
corpus = [
    "华为是中国领先的科技公司，以智能手机和5G技术闻名。",
    "阿里巴巴是中国最大的电子商务平台，也涉足云计算。",
    "腾讯以社交媒体和游戏业务为主，是中国互联网巨头。",
    "小米公司生产智能手机和智能家居产品。"
]

# 使用jieba进行中文分词
tokenized_corpus = [list(jieba.cut(doc)) for doc in corpus]

# 创建BM25模型
bm25 = BM25Okapi(tokenized_corpus)

# 查询
query = "中国科技公司"
tokenized_query = list(jieba.cut(query))

# 获取每个文档的得分
doc_scores = bm25.get_scores(tokenized_query)

# 打印结果
for i, score in enumerate(doc_scores):
    print(f"文档 {i+1} 得分: {score:.4f}")

# 获取排序后的文档索引
ranked_docs = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)

print("\n排序结果:")
for rank, doc_index in enumerate(ranked_docs):
    print(f"第 {rank+1} 名: 文档 {doc_index+1}")
    print(f"内容: {corpus[doc_index]}")
    print(f"得分: {doc_scores[doc_index]:.4f}")
    print()