from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import asyncio
import os
import time
import asyncpg
from datetime import datetime

import ollama
import json
from datetime import datetime

client = ollama.Client()


load_dotenv()  
TOKEN = os.getenv("TOKEN")
DB_URL = os.getenv("DATABASE_URL")


async def wait_for_db(retries=10, delay=3):
    for i in range(retries):
        try:
            conn = await asyncpg.connect(DB_URL)
            await conn.close()
            print("Database is ready!")
            return
        except Exception as e:
            print(f"DB not ready, retrying in {delay}s... ({i+1}/{retries})")
            await asyncio.sleep(delay)
    raise Exception("Could not connect to the database.")

asyncio.run(wait_for_db())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''
    Сәлеметсіз бе! 👋\n\n"
    Мен – қоғамдық көлік саласындағы шағымдарды талдайтын интеллектуалды агентпін.\n
    🚍 Сіздің хабарламаңызды қабылдап, негізгі мәселені, орнын және басымдығын анықтаймын.\n\n
    Жай ғана шағымыңызды немесе байқаған мәселеңізді жазыңыз – мен талдауды бастаймын! ⚡️
''')

def send_to_api(text: str):

    response = client.generate(
        model="qwen3-complaints",
        prompt=text
    )
    
    json_text = response.response
    
    try:
        data = json.loads(json_text)  
    except json.JSONDecodeError:
        data = {
            "text": text,
            "priority": "көрсетілмеген",
            "object": "көрсетілмеген",
            "time": datetime.now().isoformat(),
            "place": "көрсетілмеген",
            "aspect": "көрсетілмеген",
            "recommendation": "көрсетілмеген"
        }
    
    return data



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

    reply_text = api_response.get("recommendation", "Нет текста для ответа")
    await update.message.reply_text(reply_text)

    await save_to_db(api_response)



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"Ты написал: {user_message}. Я бот и просто отвечаю!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    # app.bot.request.timeout = 60
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущен...")
    app.run_polling()

