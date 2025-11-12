from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "mistralai/Mistral-7B-Instruct-v0.3"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

SYSTEM_PROMPT = (
    "Ты — эксперт по анализу обращений граждан. "
    "Определи эмоциональный тон жалобы. "
    "Ответь строго одним словом: 'негатив', 'нейтрально' или 'позитивно'."
)

def detect_sentiment(text: str):
    prompt = f"{SYSTEM_PROMPT}\nЖалоба: {text}\nОтвет:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=15, temperature=0.3)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer.strip().split()[-1]

complaint = "Автобус №15 не пришёл утром в 8:00 на остановку «Мектеп»."
print("Тон жалобы:", detect_sentiment(complaint))
