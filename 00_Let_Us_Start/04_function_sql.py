import json
import os
from zhipuai import ZhipuAI
import dotenv

def generate_sql(db_schema: str, query: str) -> str:
    """
    调用LLM,利用工具调用能力,生成SQL语句
    :param db_schema: 数据库表结构信息
    :param query: 用户的原始提问
    :return: 生成的结构化SQL
    """

    # 加载环境变量
    dotenv.load_dotenv()

    # 创建智谱AI客户端
    client = ZhipuAI(api_key="")

    # 定义工具的详细描述,便于LLM理解用户的需求
    tool_desc = f"""根据用户提问，生成的SQL语句，用于回答用户的问题。
                生成的SQL语句基于如下的数据库表结构定义：
                {db_schema}
                最终的SQL语句以纯文本的格式输出，不要使用json或者其它的结构化格式。
                """

    # 定义工具
    tools = [
        {
            "type": "function",  # 工具类型为function函数调用
            "function": {  # 函数定义
                "name": "generate_sql",  # 函数名称
                "description": "该函数用于回答用户提出的关于音乐的相关问题。 "
                               "生成的结果是结构化的标准SQL语句。",
                # 函数描述
                "parameters": {  # 函数参数定义
                    "type": "object",
                    "properties": {
                        "sql": {  # 参数名称
                            "type": "string",  # 参数类型
                            "description": tool_desc,  # 参数描述
                        },
                    },
                    "required": ["sql"],  # 必需的参数
                },
            }
        }
    ]

    # 创建消息列表
    messages = [
        {"role": "system",
         "content": "请根据用户的提问，基于Chinook Music数据库的信息，生成SQL语句来回答用户的问题。"},
        {"role": "user", "content": f"{query}"},
    ]

    # 执行工具调用,获取结果
    completion = client.chat.completions.create(
        model="glm-4-plus",
        messages=messages,
        tools=tools,
        tool_choice="auto"  # 工具选择模式为auto,表示由LLM自行推理,觉得是生成普通消息还是进行工具调用
    )

    # 将工具调用结果解析成sql字符串,并返回
    return json.loads(completion.choices[0].message.tool_calls[0].function.arguments).get("sql")


if __name__ == '__main__':
    # 创建sqlite数据库连接

    # 获取数据库的schema信息
    db_schema = """
       CREATE TABLE Album (
           AlbumId INTEGER PRIMARY KEY,
           Title TEXT NOT NULL,
           ArtistId INTEGER NOT NULL,
           FOREIGN KEY (ArtistId) REFERENCES Artist(ArtistId)
       );

       CREATE TABLE Artist (
           ArtistId INTEGER PRIMARY KEY,
           Name TEXT NOT NULL
       );

       CREATE TABLE Track (
           TrackId INTEGER PRIMARY KEY,
           Name TEXT NOT NULL,
           AlbumId INTEGER,
           MediaTypeId INTEGER NOT NULL,
           GenreId INTEGER,
           Composer TEXT,
           Milliseconds INTEGER NOT NULL,
           Bytes INTEGER,
           UnitPrice DECIMAL(10,2) NOT NULL,
           FOREIGN KEY (AlbumId) REFERENCES Album(AlbumId),
           FOREIGN KEY (GenreId) REFERENCES Genre(GenreId),
           FOREIGN KEY (MediaTypeId) REFERENCES MediaType(MediaTypeId)
       );

       CREATE TABLE Genre (
           GenreId INTEGER PRIMARY KEY,
           Name TEXT NOT NULL
       );

       CREATE TABLE MediaType (
           MediaTypeId INTEGER PRIMARY KEY,
           Name TEXT NOT NULL
       );

       CREATE TABLE Playlist (
           PlaylistId INTEGER PRIMARY KEY,
           Name TEXT NOT NULL
       );

       CREATE TABLE PlaylistTrack (
           PlaylistId INTEGER NOT NULL,
           TrackId INTEGER NOT NULL,
           PRIMARY KEY (PlaylistId, TrackId),
           FOREIGN KEY (PlaylistId) REFERENCES Playlist(PlaylistId),
           FOREIGN KEY (TrackId) REFERENCES Track(TrackId)
       );
       """

    # 在控制台循环获取用户输入
    while True:
        query = input("用户提问: ")
        if query == "bye":
            break

        # 将用户提问翻译成SQL
        sql = generate_sql(db_schema, query)
        print("--------------------------------------------------")
        print(f"生成的SQL语句: \n{sql}")

        # 执行SQL,获取结果
        # answer = exec_sql(conn, sql)
        print("--------------------------------------------------")
        # print(f"执行结果: {answer}")


