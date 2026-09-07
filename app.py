import os
import re
import io
import zipfile
import pandas as pd
import streamlit as st
from icrawler.builtin import BingImageCrawler
from PIL import Image, ImageOps
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Exact Food Image Downloader", page_icon="⚡", layout="wide")

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

st.markdown('<div class="title-text">⚡ Pure Clean HD Food Studio Pro (Bing Exact Search)</div>', unsafe_allow_html=True)
st.write("✨ **Exact Indian Dish Photos Clean 500x500 PNG Output**")

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
    st.info("Output Format: **PNG Crisp 500x500 Square**")
    st.markdown('</div>', unsafe_allow_html=True)

def process_single_dish(item):
    index, raw_dish = item
    clean_dish = re.sub(r'[\(\[\{].*?[\)\]\}]', '', str(raw_dish)).strip()
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_dish)
    
    final_filename = f"{safe_filename}.png"
    file_bytes = None
    
    search_query = (
        f"{clean_dish} food isolated dish photography top view "
        f"-youtube -thumbnail -recipe -blog -poster -banner -text -tamil -hindi"
    )

    temp_dir = f"temp_{index}_{safe_filename}"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        crawler = BingImageCrawler(
            downloader_threads=2,
            storage={'root_dir': temp_dir},
            log_level=50
        )
        crawler.crawl(keyword=search_query, max_num=1)

        files = os.listdir(temp_dir)
        if files:
            downloaded_file_path = os.path.join(temp_dir, files[0])
            
            with Image.open(downloaded_file_path) as img:
                img = img.convert('RGB')
                cropped_img = ImageOps.fit(
                    img, 
                    (500, 500), 
                    method=Image.Resampling.LANCZOS, 
                    centering=(0.5, 0.5)
                )
                
                buf = io.BytesIO()
                cropped_img.save(buf, format="PNG", quality=100)
                file_bytes = buf.getvalue()

    except Exception:
        pass
    finally:
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

    return clean_dish, final_filename, file_bytes

st.divider()

if uploaded_file and column_name:
    if st.button("🚀 START CLEAN BULK PROCESSING"):
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            metric_progress = st.metric("Processing Status", "0%")
        with m_col2:
            metric_count = st.metric("Dishes Downloaded", f"0 / {len(df)}")
            
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        items = [(i, row[column_name]) for i, row in df.iterrows()]
        total_items = len(items)
        completed = 0
        processed_files = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
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
        
        final_zip_data = zip_buffer.getvalue()

        st.balloons()
        st.success("🎉 All photos processed clean without text or watermarks!")
        
        st.download_button(
            label="📦 DOWNLOAD CLEAN IMAGES (PNG ZIP)",
            data=final_zip_data,
            file_name="Clean_Food_Images_500x500.zip",
            mime="application/zip",
            use_container_width=True
        )