import asyncio
import logging
import datetime
from database import init_db, is_duplicate, save_finding
from reporter import send_telegram_message, format_report, format_summary_report
from watcher import fetch_new_targets
import sys
import io
from workers import run_subfinder, run_httpx, run_nuclei

# ڕێکخستنی زمانی یۆنیکۆد بۆ ویندۆز تا ئیمۆجی و زمانی کوردی کێشە دروست نەکەن
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ڕێکخستنی فایلەکانی لۆگکردن بە یۆنیکۆد
logging.basicConfig(level=logging.INFO, 
                    format='%(message)s', 
                    handlers=[logging.FileHandler("hunter.log", encoding="utf-8"),
                              logging.StreamHandler(sys.stdout)])

async def process_target(domain):
    """قۆناغەکانی گەڕان بە یەک لە دوای یەک بەڵام بە شێوەی Async (Streaming Pipeline)"""
    logging.info(f"\n[+] ئۆپەراسیۆن دەستیپێکرد لەسەر ئامانجی: {domain}")
    
    from workers import run_subfinder, run_httpx, run_katana, run_nuclei
    
    try:
        # قۆناغی ١: دۆزینەوەی سەبدۆمەینەکان
        subdomains = await run_subfinder(domain)
        logging.info(f"   [✓] قۆناغی ١: دۆزرانەوەی {len(subdomains)} سەبدۆمەین.")
        
        # قۆناغی ٢: پشکنینی ناوە زیندووەکان
        if subdomains:
            live_urls = await run_httpx(subdomains)
            logging.info(f"   [✓] قۆناغی ٢: دڵنیابوونەوە لە {len(live_urls)} ماڵپەڕی زیندوو.")
            
            # ئەگەر httpx کێشەی هەبوو و هیچی نەدۆزییەوە، با دۆمەینە بنەڕەتییەکان بەکاربهێنین
            if not live_urls:
                logging.warning("   [!] HTTPX هیچی نەدۆزییەوە، بەکارهێنانی دۆمەینە بنەڕەتییەکان وەک جێگرەوە...")
                live_urls = [f"https://{d}" if not d.startswith("http") else d for d in subdomains]
        else:
            live_urls = []
            
        # قۆناغی ٣: Katana (پشکنینی قووڵ و کۆکردنەوەی هەموو لینکەکان)
        if live_urls:
            logging.info(f"   [>] دەستپێکردنی قۆناغی ٣: پشکنینی قووڵ لە ڕێگەی Katana...")
            katana_urls = await run_katana(live_urls)
            # تێکەڵکردنی هەموو لینکەکان (هەم ماڵپەڕە سەرەکییەکان و هەم ئەوانەی کاتانا دۆزییەوە)
            all_urls = list(set(live_urls + katana_urls))
            logging.info(f"   [✓] قۆناغی ٣: {len(all_urls)} لینکی جیاواز کۆکرایەوە.")
        else:
            all_urls = []

        # قۆناغی ٤: ڕاوچییە کۆتاییەکە (Nuclei)
        if all_urls:
            findings = await run_nuclei(all_urls)
            logging.info(f"   [✓] قۆناغی ٤: تاقیکردنەوەی لاوازییەکان کۆتایی هات. ژمارەی هەڕەشەکان: {len(findings)}")
            
            # قۆناغی ٥: ژووری عەمەلیات و کۆنترۆڵ
            for finding in findings:
                target_found = finding.get("host", "Unknown")
                template_id = finding.get("template-id", "Unknown")
                
                # پشکنین بۆ ڕێگریکردن لە دووبارە ناردن لەناو دیتابەیسەکە
                if not is_duplicate(target_found, template_id):
                    save_finding(target_found, template_id) 
                    report_msg = format_report(finding)     
                    
                    # ناردنی ڕاپۆرتەکە بۆ تێلیگرامی خاوەنەکەی
                    await send_telegram_message(report_msg)
                    logging.info(f"   [$$$] دەستکەوتی نوێ! نامە نێردرا: {target_found} بە کەلێنی {template_id}")
                else:
                    logging.info(f"   [-] دەستکەوتی کۆن دووبارە بووەوە: {target_found} -> {template_id}")
    except Exception as e:
        logging.error(f"  [!] هەڵەیەک ڕوویدا لەسەر {domain}: {e}")

async def main():
    """ژووری کۆنترۆڵی سەرەکی - The Orchestrator"""
    # دروستکردنی بنکەدراوە بۆ یەکەم جار کە دادەمەزرێت
    init_db()
    
    print("=" * 60)
    print("🚀 سیستەمی هێرشبەری زیرەک و ئۆتۆماتیکی (Distributed Hunter) بەگەڕخرا...")
    print("=" * 60 + "\n")
    
    logging.info(">>> چاودێرەکە بەدوای ئامانجی نوێدا دەگەڕێت لە پلاتفۆرمەکان...")
    
    # ڕاکێشانی دۆمەینەکان
    new_targets = await fetch_new_targets()
    new_targets_count = len(new_targets)
    
    # ڕیزکردنی ئامانجەکان بۆ ئەوەی هەر جارێک یەکسان بێن
    sorted_targets = sorted(list(new_targets))
    batch_size = 100
    total_batches = max(1, len(sorted_targets) // batch_size)
    
    # بەپێی کاتی ڕۆژ دیاریکردنی کامین دووری هەڵبژێریت
    # هەر کاتژمێرێک دووری جیاواز هەڵدەبژێرێت
    now = datetime.datetime.utcnow()
    minutes_today = now.hour * 60 + now.minute
    batch_index = (minutes_today // 60) % total_batches
    
    start = batch_index * batch_size
    queue_targets = sorted_targets[start : start + batch_size]
    
    logging.info(f">>> کۆی ئامانجەکان: {new_targets_count} | دووری ئێستا: {batch_index+1}/{total_batches} | ئامانج: {start+1} تا {start+len(queue_targets)}")
    
    # کرێکارەکان ئامادە دەکەین
    tasks = [process_target(domain) for domain in queue_targets]
    await asyncio.gather(*tasks)
    
    # ناردنی ڕاپۆرتی پوختە
    summary_msg = format_summary_report(len(queue_targets), 0, new_targets_count)
    await send_telegram_message(summary_msg)
    
    logging.info("=========================================")
    logging.info(f">>> وەجبەی دووری {batch_index+1} کۆتایی هات. خولی داهاتوو: دووری {(batch_index+2) % total_batches + 1}")
    logging.info("=========================================")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] سیستەمەکە ڕاگیرا لەلایەن بەکارهێنەرەوە.")
