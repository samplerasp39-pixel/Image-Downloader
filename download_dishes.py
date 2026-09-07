# import os
# import re
# import pandas as pd
# from icrawler.builtin import BingImageCrawler
# from PIL import Image, ImageOps

# # Load CSV file
# df = pd.read_csv('dishes.csv')

# # Output directory
# output_dir = 'dish_images_clean_500x500'
# os.makedirs(output_dir, exist_ok=True)

# for index, row in df.iterrows():
#     raw_dish = str(row['Dish names'])
    
#     # Clean up dish name
#     clean_dish = re.sub(r'[\(\[\{].*?[\)\]\}]', '', raw_dish).strip()
    
#     # Exclude YouTube, Tamil text, blog posters, and recipe cards
#     search_query = (
#         f"{clean_dish} food dish photography isolated plate "
#         f"-youtube -thumbnail -recipe -blog -poster -banner -text -tamil"
#     )
    
#     print(f"[{index+1}/{len(df)}] Downloading clean image: {clean_dish}...")
    
#     safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_dish)
#     temp_dir = os.path.join(output_dir, safe_filename)
    
#     crawler = BingImageCrawler(
#         downloader_threads=2,
#         storage={'root_dir': temp_dir}
#     )
#     # Search top 3 results to bypass bad/text-heavy images
#     crawler.crawl(keyword=search_query, max_num=1)
    
#     # Process image into crisp 500x500 PNG without distortion
#     if os.path.exists(temp_dir):
#         files = os.listdir(temp_dir)
#         if files:
#             downloaded_file_path = os.path.join(temp_dir, files[0])
#             png_file_path = os.path.join(output_dir, f"{safe_filename}.png")
            
#             try:
#                 with Image.open(downloaded_file_path) as img:
#                     img = img.convert('RGB')
                    
#                     # Crop center without stretching
#                     cropped_img = ImageOps.fit(
#                         img, 
#                         (500, 500), 
#                         method=Image.Resampling.LANCZOS, 
#                         centering=(0.5, 0.5)
#                     )
#                     cropped_img.save(png_file_path, 'PNG', quality=100)
                    
#                 os.remove(downloaded_file_path)
#             except Exception as e:
#                 print(f"Error processing {clean_dish}: {e}")
                
#         try:
#             os.rmdir(temp_dir)
#         except Exception:
#             pass

# print("\nDone! All images saved as clean 500x500 PNGs without text banners.")

# --------------------------------------download background removed images with transparent background--------------------------------------

# import os
# import re
# import pandas as pd
# from icrawler.builtin import BingImageCrawler
# from PIL import Image, ImageOps
# from rembg import remove, new_session

# # Load CSV file
# df = pd.read_csv('dishes.csv')

# # Output folder
# output_dir = 'dish_images_transparent_500x500'
# os.makedirs(output_dir, exist_ok=True)

# # Use 'u2net' model for clean cutout without losing plate edges
# rembg_session = new_session('u2net')

# for index, row in df.iterrows():
#     raw_dish = str(row['Dish names'])
    
#     # Clean dish name
#     clean_dish = re.sub(r'[\(\[\{].*?[\)\]\}]', '', raw_dish).strip()
    
#     search_query = f"{clean_dish} food dish photo isolated plate -text -poster -banner"
#     print(f"[{index+1}/{len(df)}] Processing: {clean_dish}...")
    
#     safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_dish)
#     temp_dir = os.path.join(output_dir, safe_filename)
    
#     crawler = BingImageCrawler(
#         downloader_threads=2,
#         storage={'root_dir': temp_dir}
#     )
#     crawler.crawl(keyword=search_query, max_num=1)
    
#     if os.path.exists(temp_dir):
#         files = os.listdir(temp_dir)
#         if files:
#             downloaded_file_path = os.path.join(temp_dir, files[0])
#             png_file_path = os.path.join(output_dir, f"{safe_filename}.png")
            
#             try:
#                 with Image.open(downloaded_file_path) as input_img:
#                     # 1. AI Background removal
#                     transparent_img = remove(input_img, session=rembg_session)
                    
#                     # 2. Trim empty transparent border space around the food item
#                     bbox = transparent_img.getbbox()
#                     if bbox:
#                         transparent_img = transparent_img.crop(bbox)
                    
#                     # 3. PAD instead of CROP (Keeps full plate intact without stretching/cutting)
#                     final_img = ImageOps.pad(
#                         transparent_img,
#                         (500, 500),
#                         color=(0, 0, 0, 0), # Transparent padding
#                         centering=(0.5, 0.5)
#                     )
                    
#                     # 4. Save PNG
#                     final_img.save(png_file_path, 'PNG')
                    
#                 os.remove(downloaded_file_path)
#             except Exception as e:
#                 print(f"Error processing {clean_dish}: {e}")
                
#         try:
#             os.rmdir(temp_dir)
#         except Exception:
#             pass

# print("\nAll 285 dishes are perfectly centered, 100% full plate intact, with transparent background!")


import os
import re
import pandas as pd
from icrawler.builtin import BingImageCrawler
from PIL import Image, ImageOps
from rembg import remove, new_session

# CSV file load pannu
df = pd.read_csv('dishes.csv')

output_dir = 'dish_images_perfect_500x500'
os.makedirs(output_dir, exist_ok=True)

# Best rembg AI session
rembg_session = new_session('u2net')

# Unwanted dark background / blog recipe keywords filtering
exclude_terms = (
    "-dark -black -recipe -blog -text -watermark -writing "
    "-shutterstock -dreamstime -istock -alamy -adobestock"
)

for index, row in df.iterrows():
    raw_dish = str(row['Dish names'])
    
    clean_dish = re.sub(r'[\(\[\{].*?[\)\]\}]', '', raw_dish).strip()
    
    # Specific white background food photography query
    search_query = f"{clean_dish} studio food photo isolated white background {exclude_terms}"
    print(f"[{index+1}/{len(df)}] Downloading clean image for: {clean_dish}...")
    
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_dish)
    temp_dir = os.path.join(output_dir, safe_filename)
    
    crawler = BingImageCrawler(
        downloader_threads=2,
        storage={'root_dir': temp_dir}
    )
    
    # Search top 3 to pick a clear bright image
    crawler.crawl(keyword=search_query, max_num=3)
    
    if os.path.exists(temp_dir):
        files = os.listdir(temp_dir)
        if files:
            downloaded_file_path = os.path.join(temp_dir, files[0])
            png_file_path = os.path.join(output_dir, f"{safe_filename}.png")
            
            try:
                with Image.open(downloaded_file_path) as input_img:
                    input_img = input_img.convert('RGBA')
                    
                    # Background removal
                    transparent_img = remove(input_img, session=rembg_session)
                    
                    # Trim empty margins
                    bbox = transparent_img.getbbox()
                    if bbox:
                        transparent_img = transparent_img.crop(bbox)
                    
                    # Exact 500x500 padded center
                    final_img = ImageOps.pad(
                        transparent_img,
                        (500, 500),
                        color=(0, 0, 0, 0),
                        centering=(0.5, 0.5)
                    )
                    
                    final_img.save(png_file_path, 'PNG', compress_level=1)
                    
                for f in files:
                    os.remove(os.path.join(temp_dir, f))
            except Exception as e:
                print(f"Error processing {clean_dish}: {e}")
                
        try:
            os.rmdir(temp_dir)
        except Exception:
            pass

print("\nDone! Perfect transparent 500x500 menu images generated.")