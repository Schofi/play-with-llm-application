import os
from mem0 import Memory

# 依赖LLM提取记忆，所以需要open ai
os.environ["OPENAI_API_KEY"] = "xxx"

# 吃石化 Mem0
m = Memory()

# 通过add方法，存储非结构化的记忆，metadata提供schema定义
result = m.add("I am working on improving my tennis skills. Suggest some online courses.", user_id="alice", metadata={"category": "hobbies"})
print(result)
# Created memory: Improving her tennis skills. Looking for online suggestions.

# Retrieve memories
all_memories = m.get_all()
print(all_memories)

# 搜索记忆  Search memories
related_memories = m.search(query="What are Alice's hobbies?", user_id="alice")
print(related_memories)

# 更新记忆 Update a memory
result = m.update(memory_id="m1", data="Likes to play tennis on weekends")
print(result)

# Get memory history
history = m.history(memory_id="m1")
print(history)