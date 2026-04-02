import aiohttp
import logging
import json

async def fetch_new_targets():
    """کۆکردنەوەی ئامانجەکان لە سەرچاوە جیاوازەکانی جیهانییەوە (H1, BC, Intigriti, YWH, Chaos)"""
    urls = [
        "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackerone_data.json",
        "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/bugcrowd_data.json",
        "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/intigriti_data.json",
        "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/yeswehack_data.json",
        "https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/master/main.json"
    ]
    
    all_domains = set()
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url, timeout=20) as response:
                    if response.status == 200:
                        content = await response.text()
                        data = json.loads(content)
                        
                        # ئەگەر فۆرماتەکە لیست بێت (وەک H1, BC, Intigriti)
                        if isinstance(data, list):
                            for item in data:
                                targets = item.get("targets", {}).get("in_scope", [])
                                if targets:
                                    for t in targets:
                                        endpoint = t.get("endpoint", "")
                                        if endpoint and "." in endpoint and not endpoint.startswith("*"):
                                            all_domains.add(endpoint.strip().lower())
                                else:
                                    # ئەگەر فۆرماتەکە سادە بێت (وەک Chaos)
                                    domain = item.get("target", item.get("url", ""))
                                    if domain and "." in domain:
                                        all_domains.add(domain.strip().lower())
            except Exception as e:
                logging.error(f"Error fetching from {url}: {e}")
    
    # سڕینەوەی ئەو دۆمەینانەی کە دووبارەن یان تێکچوون
    clean_domains = {d for d in all_domains if len(d) > 3 and "." in d}
    return clean_domains
