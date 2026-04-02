import aiohttp
import logging
import asyncio

async def fetch_new_targets():
    """ڕاکێشانی لیستی ئامانجەکان لە هەموو پلاتفۆرمە جیهانییەکانی Bug Bounty"""
    sources = [
        # HackerOne targets (from community maintained data)
        "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/hackerone_data.json",
        
        # BugCrowd targets
        "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/bugcrowd_data.json",
        
        # Intigriti targets
        "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/intigriti_data.json",
        
        # YesWeHack targets
        "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/yeswehack_data.json",
        
        # Chaos Public targets (ProjectDiscovery)
        "https://raw.githubusercontent.com/projectdiscovery/public_bounty_programs/master/main.json",
        
        # FireBounty aggregation
        "https://raw.githubusercontent.com/Osb0rn/bugbounty-targets/main/programs.json"
    ]
    
    all_domains = []
    
    async with aiohttp.ClientSession() as session:
        for url in sources:
            try:
                logging.info(f">>> پشکنینی سەرچاوەی نوێ لە: {url.split('/')[-1]}")
                # Timeout ی کەمتر بۆ ئەوەی نەوەستێت ئەگەر لینکێک کێشەی نیتۆرکی هەبوو
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json(content_type=None)
                        
                        # شێوازی دەرهێنانی داتا دەگۆڕێت بەپێی جۆری JSON
                        if isinstance(data, list):
                            for program in data:
                                # بۆ hackerone, bugcrowd, intigriti, yeswehack
                                targets = program.get("targets", {}).get("in_scope", [])
                                for target in targets:
                                    if target.get("asset_type") in ["URL", "Domain", "domain"]:
                                        identifier = target.get("asset_identifier", "")
                                        process_identifier(identifier, all_domains)
                                
                                # بۆ هەندێک لیستی تر (وەک Chaos یان یەکەم ئاستی لیستەکان)
                                if "domain" in program:
                                    process_identifier(program["domain"], all_domains)
                                elif "url" in program:
                                    process_identifier(program["url"], all_domains)
                        
                        elif isinstance(data, dict):
                            # بۆ Chaos یان ئەو جۆرانەی دیکشنرین
                            programs = data.get("programs", [])
                            for p in programs:
                                domains = p.get("domains", [])
                                for d in domains:
                                    process_identifier(d, all_domains)
                                    
            except Exception as e:
                logging.error(f"⚠️ کێشەیەک لە خوێندنەوەی {url} هەبوو (لەوانەیە فۆرماتەکەی جیاواز بێت)")
                
    # تەنها دۆمەینە بێ دووبارەکان بگەڕێنەوە
    unique_domains = list(set(all_domains))
    logging.info(f"✅ پڕۆسەی کۆکردنەوە کۆتایی هات. کۆی گشتی {len(unique_domains)} ئامانجی جیاواز کۆکرایەوە.")
    
    return unique_domains

def process_identifier(identifier, domain_list):
    """پاککردنەوە و زیادکردنی دۆمەین بۆ لیستەکە"""
    if not identifier or not isinstance(identifier, str):
        return
        
    # سڕینەوەی نیشانەکانی وەک *. و http و هتد
    clean = identifier.lower().replace("*.", "").replace("http://", "").replace("https://", "").split("/")[0].strip()
    
    # دڵنیابوونەوە لەوەی دۆمەینێکی دروستە
    if clean and "." in clean and not clean.startswith("*"):
        domain_list.append(clean)
