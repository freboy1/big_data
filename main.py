from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import asyncpg
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")  
DB_URL = os.getenv("DATABASE_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("just greeting message")

def send_to_api(text: str):
    # response = requests.post(API_URL, json={"text": text})
    # response.raise_for_status()
    # return response.json()
    simulated_response = {
        "text": text,
        "priority": "средний",
        "object": "автобус",
        "time": datetime.now().isoformat(),
        "place": "Остановка 'Центральная'",
        "aspect": "пунктуальность",
        "recommendation": "Улучшить расписание автобусов",
        "reply_text": f"Ваш запрос '{text}' обработан успешно!"
    }
    return simulated_response


async def save_to_db(data: dict):
    from datetime import datetime
    time_str = data.get("time")
    try:
        report_time = datetime.fromisoformat(time_str) if time_str else datetime.now()
    except ValueError:
        report_time = datetime.now()

    conn = await asyncpg.connect(DB_URL)
    await conn.execute(
        """
        INSERT INTO reports(
            text,
            priority,
            object,
            time,
            place,
            aspect,
            recommendation
        ) VALUES($1, $2, $3, $4, $5, $6, $7)
        """,
        data.get("text"),
        data.get("priority"),
        data.get("object"),
        report_time,
        data.get("place"),
        data.get("aspect"),
        data.get("recommendation")
    )
    await conn.close()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        api_response = send_to_api(user_text)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обращении к API: {e}")
        return

    reply_text = api_response.get("reply_text", "Нет текста для ответа")
    await update.message.reply_text(reply_text)

    await save_to_db(api_response)



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"Ты написал: {user_message}. Я бот и просто отвечаю!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущен...")
    app.run_polling()

