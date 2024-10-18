from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel, PeftConfig

# 加载原始的基础模型和tokenizer
base_model_path = '/home/xxx/data/modeldata/ckpt/Qwen1.5-1.8B-Chat'
tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(base_model_path, trust_remote_code=True)

# 加载保存的LoRA权重
lora_weights_path = '/home/xxx/data/modeldata/ckpt/Qwen1.5-1.8B-Chat-24-10-16'
peft_config = PeftConfig.from_pretrained(lora_weights_path)
model = PeftModel.from_pretrained(base_model, lora_weights_path)

# 合并LoRA权重到基础模型
merged_model = model.merge_and_unload()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

model.eval()

# 定义测试示例
test_examples = [
    {
        "instruction": "使用中医知识正确回答适合这个病例的中成药。",
        "input": "肛门疼痛，痔疮，肛裂。"
    },
    {
        "instruction": "使用中医知识正确回答适合这个病例的中成药。",
        "input": "有没有能够滋养肝肾、清热明目的中药。"
    }
]

for example in test_examples:
    context = f"Instruction: {example['instruction']}\nInput: {example['input']}\nAnswer: "
    inputs = tokenizer(context, return_tensors="pt")
    outputs = model.generate(inputs.input_ids.to(model.device), max_length=512, num_return_sequences=1, no_repeat_ngram_size=2)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Input: {example['input']}")
    print(f"Output: {answer}\n")