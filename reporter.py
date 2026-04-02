import aiohttp
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def send_telegram_message(message: str):
    """ناردنی نامە بۆ تێلیگرام بە شێوەی خێرا (Async)"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logging.warning("تۆکنی تێلیگرام بوونی نییە. نامەکە نانێردرێت.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logging.error(f"کێشە لە ناردنی تێلیگرام هەبوو: {error_text}")
                    return False
                return True
    except Exception as e:
        logging.error(f"هەڵەی تێلیگرام: {e}")
        return False

def format_report(finding_data: dict) -> str:
    """ئامادەکردنی ڕاپۆرتەکە (Draft) لە شێوەی قاڵبێکی جوان بۆ تێلیگرام"""
    template_id = finding_data.get("template-id", "نەزانراو")
    target = finding_data.get("host", "نەزانراو")
    severity = finding_data.get("info", {}).get("severity", "info").upper()
    name = finding_data.get("info", {}).get("name", "ناوی کەلێن نەزانراوە")
    
    extracted_results = finding_data.get("extracted-results", [])
    matched_at = finding_data.get("matched-at", target)
    
    # دروستکردنی قاڵبە جوانەکە بۆ تێلیگرام بەMarkdown
    msg = f"🟢 *لاوازییەکی نوێ دۆزرایەوە!* 🟢\n\n"
    msg += f"📍 **ئامانج:** `{target}`\n"
    msg += f"⚠️ **ئاستی مەترسی:** `{severity}`\n"
    msg += f"🛡️ **جۆری کەلێن:** {name}\n"
    msg += f"🏷️ **ناوی تەمپلەیت:** `{template_id}`\n\n"
    
    msg += f"🔗 **شوێنی دۆزینەوە:**\n`{matched_at}`\n\n"
    
    if extracted_results:
        msg += f"📝 **بەڵگەی سەلماندن (PoC):**\n`{extracted_results[0]}`\n\n"
        
    msg += "⚠️ *تێبینی:* تکایە پێداچوونەوەی بۆ بکە بزانە ڕاستە یان نا، ئەگەر ڕاست بوو ڕاپۆرتی بکە بۆ وەرگرتنی پارەکە."
    
    return msg
def format_summary_report(total_scanned, findings_count, new_targets_count) -> str:
    """ئامادەکردنی ڕاپۆرتی پوختەی کاروچالاکییەکان بە شێوەیەکی جوان"""
    msg = "📊 *ڕاپۆرتی کاروچالاکی ڕاوچی (Hunter Summary)* 📊\n\n"
    msg += f"✅ **کۆی گشتی پشکنینەکان:** `{total_scanned}`\n"
    msg += f"🚀 **ئامانجی نوێ دۆزراوەتەوە:** `{new_targets_count}`\n"
    msg += f"🛡️ **کەلێنە دۆزراوەکان:** `{findings_count}`\n\n"
    
    if findings_count > 0:
        msg += "🔥 *دەستخۆش! ئەمڕۆ ڕۆژێکی پڕ بەرهەم بوو!* 💰\n"
    else:
        msg += "💤 *ئەم وەجبەیە هیچی تێدا نەبوو، بەڵام پشکنین بەردەوامە...*\n"
        
    msg += "\n🕒 *سیستەمەکە بەردەوامە لە چاودێریکردن...*"
    return msg
