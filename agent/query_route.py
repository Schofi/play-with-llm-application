from typing import List, Dict, Union
import json


class QueryRouter:
    def __init__(self, router_config: List[Dict]):
        """
        初始化路由配置

        Args:
            router_config: 路由规则配置列表
        """
        self.router_config = router_config

    def route_query(self, user_query: str) -> Dict[str, Union[str, float]]:
        """
        根据用户查询选择合适的路由

        Args:
            user_query: 用户的查询文本

        Returns:
            Dict包含选中的路由名称和匹配置信任度
        """
        matches = []

        for router in self.router_config:
            confidence = self._calculate_match_confidence(
                user_query,
                router["RouterDescription"],
                router["用户查询举例"]
            )
            matches.append({
                "router_name": router["Routername"],
                "confidence": confidence
            })

        # 选择置信度最高的路由
        best_match = max(matches, key=lambda x: x["confidence"])
        return best_match

    def _calculate_match_confidence(
            self,
            query: str,
            description: str,
            examples: List[str]
    ) -> float:
        """
        计算查询与路由的匹配置信度

        Args:
            query: 用户查询
            description: 路由描述
            examples: 示例查询列表

        Returns:
            匹配置信度分数 (0-1)
        """
        # 实现基于规则的匹配逻辑
        confidence = 0.0

        # 1. 检查是否包含关键词
        if "提取" in query and "表格" in query:
            confidence += 0.4  # ExtractTextFromDoc 路由的特征

        if any(word in query for word in ["销量", "生产量", "产量"]):
            if "文章" in query:
                confidence += 0.3  # 倾向于 ExtractTextFromDoc
            else:
                confidence += 0.6  # 倾向于 QueryDatabase

        # 2. 与示例的相似度匹配
        for example in examples:
            if self._calculate_similarity(query, example) > 0.7:
                confidence += 0.3
                break

        return min(confidence, 1.0)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度

        Args:
            text1: 第一个文本
            text2: 第二个文本

        Returns:
            相似度分数 (0-1)
        """
        # 这里可以实现更复杂的相似度计算算法
        # 简单示例仅作演示
        common_words = set(text1) & set(text2)
        total_words = set(text1) | set(text2)
        return len(common_words) / len(total_words) if total_words else 0.0


# 使用示例
if __name__ == "__main__":
    # 路由配置
    router_config = [
        {
            "Routername": "QueryDatabase",
            "RouterDescription": "企业内部的数据库或应用系统，可以回答公司内部应用的私有生产数据等内容",
            "用户查询举例": [
                "5月份的总销量是多少",
                "今年2月的生产量是多少"
            ]
        },
        {
            "Routername": "ExtractTextFromDoc",
            "RouterDescription": "执行用户指定的数据源的工作",
            "用户查询举例": [
                "把这个文章里关于xx的数据提取出来汇聚成表格"
            ]
        }
    ]

    # 创建路由器实例
    router = QueryRouter(router_config)

    # 测试查询
    test_query = "把这个文章里关于煤矿产量的数据提取出来汇聚成表格"
    result = router.route_query(test_query)
    print(f"Query: {test_query}")
    print(f"Selected Router: {result}")