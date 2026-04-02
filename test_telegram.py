import asyncio
from reporter import send_telegram_message

async def main():
    message = "🚀 سلاو جیهاد گیان! بۆتەکەت بە سەرکەوتوویی بەگەڕخرا.\n\n🛡️ لەمەودوا هەر کەلێنێک لە ڕێگەی پڕۆژەی BugBounty بدۆزرێتەوە، لێرە ئاگادارت دەکەمەوە.\n\n✨ دەستخۆشییەکی زۆر لە خۆت بکە بۆ ئەم کارە نایابە!"
    result = await send_telegram_message(message)
    if result:
        print("✅ نامەکە بە سەرکەوتوویی نێردرا بۆ تێلیگرام!")
    else:
        print("❌ کێشەیەک لە ناردنی نامەکەدا هەبوو. دڵنیابەرەوە کە تۆکن و ئایدییەکە ڕاستن و دووگمەی Startـت لێداوە.")

if __name__ == "__main__":
    asyncio.run(main())
