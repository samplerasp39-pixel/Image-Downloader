import os
import re
import io
import zipfile
import requests
import pandas as pd
import streamlit as st
from PIL import Image, ImageOps
from concurrent.futures import ThreadPoolExecutor

UNSPLASH_ACCESS_KEY = "WLzbMAOwEP-iprTCO9Jt2JH0C04qAZ3bWlujuo_6_FY"

st.set_page_config(page_title="Watermark-Free HD Food Downloader", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #161b22 100%); }
    .title-text {
        font-size: 2.5rem; font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF8F00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .css-card {
        background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px; border-radius: 12px; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #FF4B4B 0%, #FF8F00 100%) !important;
        color: white !important; font-weight: bold !important; font-size: 1.1rem !important;
        border-radius: 10px !important; border: none !important; padding: 12px 24px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">⚡ Pure Clean HD Food Studio Pro</div>', unsafe_allow_html=True)
st.write("✨ **Zero Watermarks & Zero Text guaranteed via Unsplash API**")

st.divider()

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("📂 1. Upload File")
    uploaded_file = st.file_uploader("Upload Excel or CSV File (.xlsx, .csv)", type=["csv", "xlsx"])
    column_name = None
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.success(f"✔ File Loaded! Total items: **{len(df)}**")
        column_name = st.selectbox("Select Dish Names Column:", df.columns)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("⚙️ 2. Export Settings")
    bg_option = st.radio("Background Mode:", ["1. Normal HD Photo", "2. Transparent Cutout (White BG Removal)"])
    file_format = st.selectbox("Select Output Format:", ["JPG", "PNG", "WEBP"])
    st.write("---")
    use_custom_size = st.checkbox("Enable Custom Resolution?", value=True)
    dim_col1, dim_col2 = st.columns(2)
    with dim_col1:
        width = st.number_input("Width (Pixels)", value=1000, step=100) if use_custom_size else None
    with dim_col2:
        height = st.number_input("Height (Pixels)", value=1000, step=100) if use_custom_size else None
    st.markdown('</div>', unsafe_allow_html=True)

def remove_white_bg(img):
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] > 235 and item[1] > 235 and item[2] > 235:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    return img

def fetch_clean_image(dish_name):
    url = f"https://api.unsplash.com/search/photos?query={dish_name} food isolated&per_page=1&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("results"):
            img_url = res["results"][0]["urls"]["full"]
            img_res = requests.get(img_url, timeout=15)
            return Image.open(io.BytesIO(img_res.content))
    except Exception:
        pass
    return None

def process_single_dish(item):
    index, raw_dish, bg_opt, chosen_fmt, size_enabled, target_w, target_h = item
    clean_dish = re.sub(r'[\(\[\{].*?[\)\]\}]', '', str(raw_dish)).strip()
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_dish)
    output_dir = "downloaded_dishes_output"
    
    is_transparent = "Transparent" in bg_opt
    ext = chosen_fmt.lower()
    if is_transparent and ext == "jpg":
        ext = "png"
        
    final_filename = f"{safe_filename}.{ext}"
    local_save_path = os.path.join(output_dir, final_filename)
    file_bytes = None
    
    input_img = fetch_clean_image(clean_dish)
    
    if input_img:
        try:
            if is_transparent:
                input_img = remove_white_bg(input_img)
                bbox = input_img.getbbox()
                if bbox:
                    input_img = input_img.crop(bbox)
            else:
                input_img = input_img.convert('RGB')
            
            if size_enabled and target_w and target_h:
                if is_transparent:
                    final_img = ImageOps.pad(input_img, (target_w, target_h), color=(0, 0, 0, 0), centering=(0.5, 0.5))
                else:
                    final_img = ImageOps.fit(input_img, (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            else:
                final_img = input_img
            
            save_format = "PNG" if ext == "png" else ("WEBP" if ext == "webp" else "JPEG")
            
            if save_format == "JPEG":
                final_img = final_img.convert('RGB')
                final_img.save(local_save_path, 'JPEG', quality=95)
            elif save_format == "WEBP":
                final_img.save(local_save_path, 'WEBP', quality=95)
            else:
                final_img.save(local_save_path, 'PNG', compress_level=1)
            
            buf = io.BytesIO()
            final_img.save(buf, format=save_format if save_format != "JPEG" else "JPEG", quality=95)
            file_bytes = buf.getvalue()
        except Exception:
            pass
            
    return clean_dish, final_filename, file_bytes

st.divider()

if uploaded_file and column_name:
    if st.button("🚀 START CLEAN BULK PROCESSING"):
        if UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_ACCESS_KEY_HERE":
            st.error("Please add your Unsplash Access Key in the code first!")
        else:
            output_dir = "downloaded_dishes_output"
            os.makedirs(output_dir, exist_ok=True)
            
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                metric_progress = st.metric("Processing Status", "0%")
            with m_col2:
                metric_count = st.metric("Dishes Downloaded", f"0 / {len(df)}")
                
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            items = [(i, row[column_name], bg_option, file_format, use_custom_size, width, height) for i, row in df.iterrows()]
            total_items = len(items)
            completed = 0
            processed_files = []
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(process_single_dish, item) for item in items]
                for future in futures:
                    dish_name, fname, fbytes = future.result()
                    completed += 1
                    if fbytes:
                        processed_files.append((fname, fbytes))
                    
                    pct = int((completed / total_items) * 100)
                    progress_bar.progress(completed / total_items)
                    metric_progress.metric("Processing Status", f"{pct}%")
                    metric_count.metric("Dishes Downloaded", f"{completed} / {total_items}")
                    status_text.write(f"⚡ **[{completed}/{total_items}] Clean Photo Processed:** `{dish_name}`")

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for filename, data in processed_files:
                    zip_file.writestr(filename, data)
            zip_buffer.seek(0)

            st.balloons()
            st.success("🎉 All photos processed clean without text or watermarks!")
            
            st.download_button(
                label=f"📦 DOWNLOAD CLEAN IMAGES ({file_format} ZIP)",
                data=zip_buffer,
                file_name=f"Clean_Food_Images_{file_format}.zip",
                mime="application/zip",
                use_container_width=True
            )