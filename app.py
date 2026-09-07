import os
import re
import pandas as pd
from icrawler.builtin import BingImageCrawler
from PIL import Image, ImageOps
from concurrent.futures import ThreadPoolExecutor

# CSV File Path
CSV_FILE = 'dishes.csv'

# Output directory
OUTPUT_DIR = 'dish_images_clean_500x500'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load CSV
df = pd.read_csv(CSV_FILE)

# Get the exact dish column name
dish_col = df.columns[0]  # First column use panni automatic-a edukku

def process_dish(item):
    index, raw_dish = item
    clean_dish = re.sub(r'[\(\[\{].*?[\)\]\}]', '', str(raw_dish)).strip()
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_dish)
    
    png_final_path = os.path.join(OUTPUT_DIR, f"{safe_filename}.png")
    
    # Skips if already downloaded
    if os.path.exists(png_final_path):
        print(f"⏩ [{index+1}/{len(df)}] Already exists: {clean_dish}")
        return

    # High precision search query for exact food item without text/watermark
    search_query = (
        f"{clean_dish} food isolated dish photography top view "
        f"-youtube -thumbnail -recipe -blog -poster -banner -text -tamil -hindi"
    )

    temp_dir = os.path.join(OUTPUT_DIR, f"temp_{safe_filename}")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        print(f"⚡ [{index+1}/{len(df)}] Downloading exact image: {clean_dish}...")
        
        crawler = BingImageCrawler(
            downloader_threads=4,
            storage={'root_dir': temp_dir},
            log_level=50  # Suppress internal noise logs
        )
        
        # Crawls top 1 result
        crawler.crawl(keyword=search_query, max_num=1)

        files = os.listdir(temp_dir)
        if files:
            downloaded_file_path = os.path.join(temp_dir, files[0])
            
            with Image.open(downloaded_file_path) as img:
                img = img.convert('RGB')
                
                # Perfect 500x500 square cropping without distortion
                cropped_img = ImageOps.fit(
                    img, 
                    (500, 500), 
                    method=Image.Resampling.LANCZOS, 
                    centering=(0.5, 0.5)
                )
                cropped_img.save(png_final_path, 'PNG', quality=100)
                print(f"✅ Saved clean PNG: {safe_filename}.png")

    except Exception as e:
        print(f"❌ Error downloading {clean_dish}: {e}")
        
    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, f))
                except Exception:
                    pass
            try:
                os.rmdir(temp_dir)
            except Exception:
                pass

def main():
    items = [(index, row[dish_col]) for index, row in df.iterrows()]
    
    print(f"🚀 Starting fast download for {len(items)} items...\n")
    
    # Run 4 parallel downloads at once for speed
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_dish, items)

    print("\n🎉 DONE! All exact images saved in 'dish_images_clean_500x500' folder.")

if __name__ == "__main__":
    main()