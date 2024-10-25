from openai import OpenAI
import json


def generate_formatted_json(user_input: str):
    client = OpenAI(
        api_key="sk-9dfe516b634f401188428c18493a9c46",
        base_url="https://api.deepseek.com",
    )

    # 定义返回格式
    functions = [
        {
            "name": "format_json",
            "description": "Format user input into structured JSON",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Person's name"
                    },
                    "age": {
                        "type": "integer",
                        "description": "Person's age"
                    },
                    "interests": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of interests"
                    }
                },
                "required": ["name"]
            }
        }
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": user_input}
        ],
        functions=functions,
        function_call={"name": "format_json"}
    )

    # 解析返回的 JSON
    return json.loads(response.choices[0].message.function_call.arguments)


# 使用示例
result = generate_formatted_json("小明今年18岁，喜欢篮球和编程")
# 输出:
# {
#     "name": "小明",
#     "age": 18,
#     "interests": ["篮球", "编程"]
# }