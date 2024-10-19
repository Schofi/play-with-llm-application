import os
from sentence_transformers import SentenceTransformer
import numpy as np

def load_embedding_model():
    """
    加载bge-small-zh-v1.5模型
    :return: 返回加载的bge-small-zh-v1.5模型
    """
    print(f"加载Embedding模型中")
    # SentenceTransformer读取绝对路径下的bge-small-zh-v1.5模型，非下载
    embedding_model = SentenceTransformer(os.path.abspath('/home/xxx/data/modeldata/rag_app/bge-small-zh-v1.5'))
    print(f"bge-small-zh-v1.5模型最大输入长度: {embedding_model.max_seq_length}")
    return embedding_model

def test_embedding_model():
    # 加载模型
    model = load_embedding_model()

    # 测试查询和可能的匹配字符串
    query = "人工智能的应用"
    test_strings = [
        "人工智能在医疗领域的应用",
        "机器学习算法",
        "自然语言处理技术",
        "深度学习在图像识别中的应用",
        "传统数据库系统",
        "网络安全策略",
        "云计算服务",
        "区块链技术",
        "物联网设备"
    ]

    # 生成查询的嵌入向量
    query_embedding = model.encode([query])[0]

    # 生成测试字符串的嵌入向量
    test_embeddings = model.encode(test_strings)

    # 计算相似度
    similarities = np.dot(test_embeddings, query_embedding) / (np.linalg.norm(test_embeddings, axis=1) * np.linalg.norm(query_embedding))

    # 打印结果
    print(f"查询: '{query}'")
    print("相似度结果:")
    for string, similarity in zip(test_strings, similarities):
        print(f"- '{string}': {similarity:.4f}")

    # 设定一个相似度阈值
    threshold = 0.5
    print(f"\n使用阈值 {threshold} 的匹配结果:")
    for string, similarity in zip(test_strings, similarities):
        if similarity > threshold:
            print(f"匹配: '{string}' (相似度: {similarity:.4f})")
        else:
            print(f"不匹配: '{string}' (相似度: {similarity:.4f})")

if __name__ == "__main__":
    test_embedding_model()



# 加载Embedding模型中
# bge-small-zh-v1.5模型最大输入长度: 512
# 查询: '人工智能的应用'
# 相似度结果:
# - '人工智能在医疗领域的应用': 0.8409
# - '机器学习算法': 0.4915
# - '自然语言处理技术': 0.4909
# - '深度学习在图像识别中的应用': 0.6101
# - '传统数据库系统': 0.4277
# - '网络安全策略': 0.4008
# - '云计算服务': 0.4526
# - '区块链技术': 0.4452
# - '物联网设备': 0.4824
#
# 使用阈值 0.5 的匹配结果:
# 匹配: '人工智能在医疗领域的应用' (相似度: 0.8409)
# 不匹配: '机器学习算法' (相似度: 0.4915)
# 不匹配: '自然语言处理技术' (相似度: 0.4909)
# 匹配: '深度学习在图像识别中的应用' (相似度: 0.6101)
# 不匹配: '传统数据库系统' (相似度: 0.4277)
# 不匹配: '网络安全策略' (相似度: 0.4008)
# 不匹配: '云计算服务' (相似度: 0.4526)
# 不匹配: '区块链技术' (相似度: 0.4452)
# 不匹配: '物联网设备' (相似度: 0.4824)