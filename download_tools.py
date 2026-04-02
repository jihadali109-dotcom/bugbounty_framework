import urllib.request
import zipfile
import os
import json

# لیستی ئامرازەکان لەگەڵ سەرچاوەی API لە گیتهاب
tools = {
    "subfinder": "https://api.github.com/repos/projectdiscovery/subfinder/releases/latest",
    "httpx": "https://api.github.com/repos/projectdiscovery/httpx/releases/latest",
    "nuclei": "https://api.github.com/repos/projectdiscovery/nuclei/releases/latest",
    "katana": "https://api.github.com/repos/projectdiscovery/katana/releases/latest"
}

print("📥 دەستکردن بە داونلۆدکردنی ڕاستەوخۆی فایلە ئامادەکراوەکانی (.exe)...")

for tool, api_url in tools.items():
    print(f"\n--- پشکنین بۆ ئامرازی {tool} ---")
    try:
        # دروستکردنی داواکاری (Request) بۆ دۆزینەوەی تازەترین وەشانی ئامرازەکە
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            download_url = None
            
            # گەڕان بەدوای فایلی زیپ بۆ ویندۆز (windows_amd64)
            for asset in data.get('assets', []):
                asset_name = asset['name'].lower()
                if 'windows' in asset_name and 'amd64' in asset_name and asset_name.endswith('.zip'):
                    download_url = asset['browser_download_url']
                    break
            
            if download_url:
                zip_path = f"{tool}.zip"
                print(f"📥 داونلۆدکردنی {tool} لە {download_url}...")
                urllib.request.urlretrieve(download_url, zip_path)
                
                print(f"📦 دەرهێنان (Extracting) ی فایلی .exe ...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # تەنها فایلی سەرەکی (.exe) دەردەهێنین بۆ ناو فۆڵدەری پڕۆژەکە
                    for member in zip_ref.namelist():
                        if member.endswith('.exe'):
                            # پاراستنی تەنها فایلی exe بەبێ فۆڵدەرە زیادەکان
                            filename = os.path.basename(member)
                            with zip_ref.open(member) as source, open(filename, "wb") as target:
                                target.write(source.read())
                            print(f"✅ فایلی {filename} دەرهێنرا.")
                
                # سڕینەوەی فایلی زیپەکە دوای تەواوبوون
                os.remove(zip_path)
                print(f"✨ ئامرازی {tool} بە سەرکەوتوویی ئامادە کرا.")
            else:
                print(f"❌ هیچ وەشانی ویندۆز (amd64.zip) بۆ {tool} نەدۆزرایەوە.")
    except Exception as e:
        print(f"⚠️ هەڵەیەک لە داونلۆدکردنی {tool} ڕوویدا: {e}")

print("\n🎉 هەموو ئامرازەکان ئامادەن بۆ کارکردن!")
