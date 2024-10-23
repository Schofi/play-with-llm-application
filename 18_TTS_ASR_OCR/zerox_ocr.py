from pyzerox import zerox
import os
import asyncio


# model = "gpt-4-vision-preview"  # 使用 OpenAI 的视觉模型
os.environ["OPENAI_API_KEY"] = ""  # 你的API密钥

file_path = "img.png"
output_dir = "./output_test"

async def main():
    result = await zerox(file_path=file_path, output_dir=output_dir )
    print(result)

# 运行异步函数
if __name__ == "__main__":
    asyncio.run(main())