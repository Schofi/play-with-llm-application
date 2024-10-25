from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. 初始化 Qdrant 客户端
client = QdrantClient(path="")  # Persists changes to disk, fast prototyping

# 2. 初始化 Sentence Transformer 模型
# 这里使用 all-MiniLM-L6-v2 模型，它是一个轻量级但效果不错的模型
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# 3. 创建集合配置
collection_name = "my_collection"
vectors_config = models.VectorParams(
    size=model.get_sentence_embedding_dimension(),  # 384 for all-MiniLM-L6-v2
    distance=models.Distance.COSINE
)

# 4. 创建集合
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=vectors_config
)

# 5. 示例：添加一些文档
texts = [
    "这是第一个文档",
    "这是第二个文档",
    "这是第三个文档"
]

# 6. 将文本转换为向量
vectors = model.encode(texts)

# 7. 准备要插入的点
points = [
    models.PointStruct(
        id=idx,
        vector=vector.tolist(),
        payload={"text": text}
    )
    for idx, (text, vector) in enumerate(zip(texts, vectors))
]

# 8. 插入数据
client.upsert(
    collection_name=collection_name,
    points=points
)

# 9. 示例：搜索最相似的文档
query_text = "第二个文档"
query_vector = model.encode(query_text).tolist()

search_results = client.search(
    collection_name=collection_name,
    query_vector=query_vector,
    limit=3
)

# 打印搜索结果
for result in search_results:
    print(f"Score: {result.score:.4f}, Text: {result.payload['text']}")