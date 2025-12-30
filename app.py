import streamlit as st
from rembg import remove
from PIL import Image
import io

# --- CONFIGURATION ---
SCALE_FACTOR = 0.85
BOTTOM_BUFFER_PERCENT = 0.01 

st.set_page_config(page_title="Promoter Cam", page_icon="📸")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        .stApp { text-align: center; }
        img { border-radius: 10px; }
        div[data-testid="stCameraInput"] video {
            border-radius: 15px;
            border: 2px solid #ff4b4b;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 Brand Photo Booth")

# --- ASSETS SETTINGS ---
ASSETS = {
    "Bali": {"bg": "bali_bg.jpg", "frame": "frame.png"},
    "Paris": {"bg": "paris_bg.jpg", "frame": "frame.png"}
}

location = st.selectbox("Select Location", list(ASSETS.keys()))

# Camera Input
img_file_buffer = st.camera_input(f"Take Photo for {location}")

if img_file_buffer is not None:
    with st.spinner('Photo taiyaar ho rahi hai...'):
        try:
            # 1. Load Background
            bg_path = ASSETS[location]["bg"]
            # frame_path = ASSETS[location]["frame"] # Frame abhi band hai
            
            background = Image.open(bg_path).convert("RGBA")
            bg_w, bg_h = background.size
            
            # 2. Process User Image
            user_img = Image.open(img_file_buffer)
            user_cutout = remove(user_img)
            
            # --- SCALING & POSITION ---
            orig_w, orig_h = user_cutout.size
            new_width = int(bg_w * SCALE_FACTOR)
            ratio = new_width / orig_w
            new_height = int(orig_h * ratio)
            user_cutout = user_cutout.resize((new_width, new_height))
            
            x_offset = (bg_w - new_width) // 2
            bottom_margin = int(bg_h * BOTTOM_BUFFER_PERCENT)
            y_offset = bg_h - new_height - bottom_margin
            if y_offset < 0: y_offset = 0

            # Paste User
            background.paste(user_cutout, (x_offset, y_offset), user_cutout)
            
            # --- FINAL SHOW ---
            st.image(background, caption="Final Look", use_column_width=True)
            
            # --- RENAME OPTION (NAYA FEATURE) ---
            st.write("---") # Line separator
            
            # User se naam puchna (Default naam: Bali_Trip)
            custom_name = st.text_input("File ka naam likhein:", value=f"{location}_Guest")
            
            # Agar user ne .png nahi lagaya to hum laga denge
            if not custom_name.endswith(".png"):
                custom_name += ".png"
            
            # Prepare Download
            buf = io.BytesIO()
            background.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            # Download Button
            st.download_button(
                label=f"📥 Download '{custom_name}'",
                data=byte_im,
                file_name=custom_name,
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")
