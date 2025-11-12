from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Загружаем Gemma
model_name = "google/gemma-2b"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

SYSTEM_PROMPT = (
    "Ты — аналитик жалоб граждан. Определи срочность жалобы (priority). "
    "Отвечай строго одним словом: низкий, средний или высокий.\n"
    "Примеры:\n"
    "Жалоба: Автобус опоздал на остановку.\nОтвет: низкий\n"
    "Жалоба: Водопровод не работает уже неделю.\nОтвет: высокий\n"
    "Жалоба: Сломан фонарь на улице.\nОтвет: средний\n"
)


def classify_priority(text: str):
    prompt = f"{SYSTEM_PROMPT}\nЖалоба: {text}\nОтвет:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=20, do_sample=False)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if "Ответ:" in answer:
        priority_text = answer.split("Ответ:")[-1].strip()
    else:
        priority_text = answer.strip()
    
    priority_word = priority_text.split()[0]

    return priority_word


# Пример
complaint = "№30 автобус таңертең толып келді, кондиционер істемейді."
priority = classify_priority(complaint)
print(f"Срочность жалобы: {priority}")
