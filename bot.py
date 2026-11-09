import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, ConversationHandler, CommandHandler
from playwright.async_api import async_playwright

TOKEN = os.environ.get("TELEGRAM_TOKEN")
ASK_ID, ASK_PASS = range(2)
USER_DATA = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعت الـ ID بتاعك:")
    return ASK_ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_DATA['id'] = update.message.text
    await update.message.reply_text("ابعت الباسورد:")
    return ASK_PASS

async def get_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_DATA['pass'] = update.message.text
    await update.message.reply_text("جاري الدخول للمنصة...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto("https://me-portal.qureo.education/login", timeout=30000)
            
            # محاولة إدخال البيانات
            await page.fill('input[name="login_id"]', USER_DATA['id'])
            await page.fill('input[name="password"]', USER_DATA['pass'])
            await page.click('button[type="submit"]')
            
            await page.wait_for_timeout(5000)
            
            current_url = page.url
            if "login" not in current_url:
                await update.message.reply_text("✅ تم الدخول للمنصة! البوت شغال.")
            else:
                await update.message.reply_text("❌ فشل الدخول. تأكد من البيانات.")
            
            await browser.close()
            
    except Exception as e:
        await update.message.reply_text(f"إيرور: {str(e)}")
    
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_id)],
            ASK_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pass)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)
    app.run_polling()
