import json
from openai import OpenAI
import os
from typing import Dict, Optional


class FinancialProductFSM:
    def __init__(self):
        self.states = {
            'START': 'START',
            'YOUNG': 'YOUNG',
            'OLD': 'OLD',
            'LOW_RISK': 'LOW_RISK',
            'HIGH_RISK': 'HIGH_RISK',
            'HIGH_INCOME': 'HIGH_INCOME',
            'LOW_INCOME': 'LOW_INCOME'
        }
        self.current_state = self.states['START']

        self.transitions = {
            (self.states['START'], 'young'): self.states['YOUNG'],
            (self.states['START'], 'old'): self.states['OLD'],
            (self.states['YOUNG'], 'low_risk'): self.states['LOW_RISK'],
            (self.states['YOUNG'], 'high_risk'): self.states['HIGH_RISK'],
            (self.states['OLD'], 'low_risk'): self.states['LOW_RISK'],
            (self.states['OLD'], 'high_risk'): self.states['HIGH_RISK'],
        }

        self.product_recommendations = {
            (self.states['LOW_RISK'], self.states['HIGH_INCOME']): '高收益储蓄账户',
            (self.states['HIGH_RISK'], self.states['HIGH_INCOME']): '股票和共同基金',
            (self.states['LOW_RISK'], self.states['LOW_INCOME']): '定期存款（CD）',
            (self.states['HIGH_RISK'], self.states['LOW_INCOME']): '高风险投资基金',
        }

    def process_input(self, user_info: Dict) -> str:
        age = user_info.get('age')
        risk = user_info.get('risk')
        income = user_info.get('income')

        new_state = self.update_state(age, risk)
        if new_state is None:
            return '输入无效'

        self.current_state = new_state
        return self.get_recommendation(income)

    def update_state(self, age: str, risk: str) -> Optional[str]:
        if age in ['young', 'old']:
            state_after_age = self.transitions.get((self.states['START'], age))
            return self.transitions.get((state_after_age, risk)) if state_after_age else None
        return None

    def get_recommendation(self, income: str) -> str:
        for (risk_state, income_state), product in self.product_recommendations.items():
            if self.current_state == risk_state:
                return product if income_state == (
                    self.states['HIGH_INCOME'] if income == 'high_income' else self.states['LOW_INCOME']) else None
        return '没有合适的产品推荐'


async def get_user_info_from_openai(dialogue: str) -> Optional[Dict]:
    """
    使用OpenAI API提取用户信息
    """
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url="你的API基础URL"  # 如果使用代理或其他API地址
    )

    try:
        # 使用函数调用来获取结构化数据
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "你是一个金融顾问助手，负责从对话中提取用户的年龄、风险偏好和收入水平信息。"},
                {"role": "user", "content": dialogue}
            ],
            functions=[
                {
                    "name": "extract_user_info",
                    "description": "从对话中提取用户信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "age": {
                                "type": "string",
                                "enum": ["young", "old"],
                                "description": "用户的年龄段"
                            },
                            "risk": {
                                "type": "string",
                                "enum": ["low_risk", "high_risk"],
                                "description": "用户的风险偏好"
                            },
                            "income": {
                                "type": "string",
                                "enum": ["high_income", "low_income"],
                                "description": "用户的收入水平"
                            }
                        },
                        "required": ["age", "risk", "income"]
                    }
                }
            ],
            function_call={"name": "extract_user_info"}
        )

        # 从返回结果中提取函数调用参数
        function_args = json.loads(response.choices[0].message.function_call.arguments)
        return function_args

    except Exception as e:
        print(f"OpenAI API调用错误: {e}")
        return None


async def main():
    fsm = FinancialProductFSM()
    print("欢迎来到金融产品推荐系统！")

    # 示例对话
    dialogue_history = """
    用户: 我年轻，喜欢高风险投资，而且收入挺高的。
    """

    # 使用OpenAI提取用户信息
    user_info = await get_user_info_from_openai(dialogue_history)

    if user_info:
        # 显示提取的用户信息
        print(f"提取的用户信息: {json.dumps(user_info, ensure_ascii=False)}")

        # 处理提取的信息并推荐金融产品
        recommendation = fsm.process_input(user_info)
        print(f"推荐的产品: {recommendation}")
    else:
        print("无法根据用户输入生成推荐。")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())