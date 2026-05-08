import os
import base64
import requests
import json
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8706947561:AAEhgWJHAi4XB1D8vNwOz2QUPq4Cuuix620")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ًں‘‹ Hello! I'm your Serial Number Scanner bot.\n\n"
        "ًں“¸ Just send me a photo of any product label and I'll read the serial number for you automatically!\n\n"
        "Try it now â€” send a photo!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ًں”چ Reading your label, please wait...")
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        b64 = base64.b64encode(file_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64}},
                    {"text": "Read this product label image carefully. Extract all visible text fields. Return ONLY a raw JSON object, no markdown, no explanation:\n{\"serial_number\":\"value or null\",\"model\":\"value or null\",\"brand\":\"value or null\",\"article_number\":\"value or null\",\"lot\":\"value or null\"}"}
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 500
            }
        }

        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        # Safe extraction of text
        txt = ""
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                txt = candidate["content"]["parts"][0].get("text", "")
        
        if not txt:
            # Try to get error info
            error_msg = data.get("error", {}).get("message", "Unknown error")
            await update.message.reply_text(f"â‌Œ Gemini error: {error_msg}\n\nPlease try again.")
            return

        try:
            clean = txt.replace("```json","").replace("```","").strip()
            parsed = json.loads(clean)
        except:
            parsed = {"serial_number": txt.strip()[:100]}

        sn = parsed.get("serial_number") or "Not found"
        brand = parsed.get("brand")
        model = parsed.get("model")
        article = parsed.get("article_number")
        lot = parsed.get("lot")

        msg = "âœ… *Label Read Successfully!*\n\n"
        msg += f"ًں”¢ *Serial Number:*\n`{sn}`\n"
        if brand and brand != "null": msg += f"\nًںڈ·ï¸ڈ *Brand:* {brand}"
        if model and model != "null": msg += f"\nًں“¦ *Model:* {model}"
        if article and article != "null": msg += f"\nًں”– *Article No:* {article}"
        if lot and lot != "null": msg += f"\nًں“‹ *Lot:* {lot}"
        msg += "\n\n_Tap the serial number to copy it_"

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"â‌Œ Error: {str(e)}\n\nPlease try again.")

async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ًں“¸ Please send me a *photo* of the label to scan.", parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(~filters.PHOTO & ~filters.COMMAND, handle_other))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
