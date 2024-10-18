from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional

app = FastAPI()

# 设置随机数种子，确保实验可重复性
torch.manual_seed(0)

# 模型路径
PATH = '/home/xxx/minicpm3data'

# 加载分词器和模型
tokenizer = AutoTokenizer.from_pretrained(PATH)
model = AutoModelForCausalLM.from_pretrained(PATH, torch_dtype=torch.bfloat16, device_map='cuda', trust_remote_code=True)

class ChatRequest(BaseModel):
    message: str
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response, _ = model.chat(tokenizer, request.message, temperature=request.temperature, top_p=request.top_p)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)