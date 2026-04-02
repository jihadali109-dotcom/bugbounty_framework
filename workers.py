import asyncio
import json
import logging
import os
from config import LOG_FILE, EXE_EXT

async def execute_command(cmd, log_prefix="Worker"):
    """فانکشنێکی یارمەتیدەر بۆ لێدانی فەرمانەکان بە Async"""
    logging.info(f"[{log_prefix}] جێبەجێکردنی فەرمانی: {cmd}")
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip()

# سەربازی یەکەم: Subfinder
async def run_subfinder(domain: str) -> list:
    """گەڕان بەدوای سەبدۆمەین بە قووڵی"""
    cmd = f"./subfinder{EXE_EXT} -d {domain} -all -silent"
    output = await execute_command(cmd, "Subfinder")
    
    subdomains = output.split('\n')
    results = [s.strip() for s in subdomains if s.strip()]
    
    # بۆ ئەوەی ئەگەر subfinder هیچی نەدۆزییەوە، هەر هیچ نەبێت دۆمەینە سەرەکییەکە سکان بکرێت
    if domain not in results:
        results.append(domain)
        
    return results

# سەربازی دووەم: HTTPX (زیادکردنی فیلتەری وردتر)
async def run_httpx(domains: list) -> list:
    """دۆزینەوەی ماڵپەڕە زیندووەکان"""
    if not domains: 
        return []
    
    temp_file = "temp_domains.txt"
    with open(temp_file, "w") as f:
        f.write("\n".join(domains))
        
    # -p http,https: تاقیکردنەوەی هەردووکیان
    # -t 15: کاتی وەڵامدانەوە زیاد کراوە
    cmd = f"./httpx{EXE_EXT} -l {temp_file} -silent -mc 200,301,302,403,404 -t 15"
    output = await execute_command(cmd, "HTTPX")
    
    live_urls = output.split('\n')
    
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return [url.strip() for url in live_urls if url.strip()]

# سەربازی سێیەم: Katana (Crawler & URL Discovery)
async def run_katana(urls: list) -> list:
    """پشکنینی قووڵ و دەرهێنانی لینک و پارامێتەرەکان"""
    if not urls:
        return []
    
    temp_file = "temp_katana_in.txt"
    with open(temp_file, "w") as f:
        f.write("\n".join(urls))
    
    # -d 3: قووڵی پشکنین (Depth)
    # -kf all: پاراستنی هەموو فۆرماتەکان
    cmd = f"./katana{EXE_EXT} -l {temp_file} -d 3 -kf all -silent"
    output = await execute_command(cmd, "Katana")
    
    discovered_urls = output.split('\n')
    
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return [u.strip() for u in discovered_urls if u.strip()]

# سەربازی چوارەم: Nuclei Engine (پاڵاوتنی ئاستی مەترسی)
async def run_nuclei(urls: list):
    """هێرشبردن لە ڕێگەی Nuclei بۆ دۆزینەوەی کەلێنەکان"""
    if not urls: 
        return []
    
    temp_file = "temp_nuclei_in.txt"
    with open(temp_file, "w") as f:
        f.write("\n".join(urls))
        
    output_file = "nuclei_results.json"
    
    # ئەپدەیتکردنی تەمپلەیتەکان
    await execute_command(f"./nuclei{EXE_EXT} -ut -silent", "Nuclei Update")
    
    # پشکنینی هەموو ئاستەکان بۆ ئەوەی چانسی دۆزینەوە زیاد بکات
    cmd = f"./nuclei{EXE_EXT} -l {temp_file} -json-export {output_file} -silent -severity low,medium,high,critical -rl 50"
    await execute_command(cmd, "Nuclei")
    
    results = []
    try:
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            results.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
            os.remove(output_file)
    except Exception as e:
        logging.error(f"Error reading Nuclei results: {e}")
        
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return results
