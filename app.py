import streamlit as st
from rembg import remove
from PIL import Image
import io

# --- CONFIGURATION (SETTINGS) ---

# 1. QUALITY SETTINGS (Force HD Resolution)
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# 2. SIZE SETTING (Zoom Fix)
# 0.95 means user will occupy 95% of the frame width
SCALE_FACTOR = 0.95

# 3. POSITION SETTING (Grounded)
# 0.0 means feet will be exactly at the bottom edge
BOTTOM_BUFFER_PERCENT = 0.0

st.set_page_config(page_title="Photo Booth", page_icon="📸")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        .stApp { text-align: center; }
        img { border-radius: 10px; }
        /* Mobile view camera border */
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

location = st.selectbox("Select Destination", list(ASSETS.keys()))

# Camera Input
img_file_buffer = st.camera_input(f"Take Photo for {location}")

if img_file_buffer is not None:
    with st.spinner('Processing High Quality Image...'):
        try:
            # 1. Load & Force Resize Background to HD using LANCZOS
            bg_path = ASSETS[location]["bg"]
            # frame_path = ASSETS[location]["frame"] # Frame currently disabled
            
            background = Image.open(bg_path).convert("RGBA")
            background = background.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
            bg_w, bg_h = background.size
            
            # 2. Process User Image (Remove BG)
            user_img = Image.open(img_file_buffer)
            user_cutout = remove(user_img)
            
            # --- SCALING & POSITION ---
            orig_w, orig_h = user_cutout.size
            
            # Calculate new width (95% of background width)
            new_width = int(bg_w * SCALE_FACTOR)
            # Maintain aspect ratio for height
            ratio = new_width / orig_w
            new_height = int(orig_h * ratio)
            
            # Resize user image with high-quality filter
            user_cutout = user_cutout.resize((new_width, new_height), Image.LANCZOS)
            
            # Positioning Calculations
            x_offset = (bg_w - new_width) // 2
            
            # Bottom margin is 0 (Grounded)
            bottom_margin = int(bg_h * BOTTOM_BUFFER_PERCENT)
            y_offset = bg_h - new_height - bottom_margin
            
            if y_offset < 0: y_offset = 0

            # Paste User
            background.paste(user_cutout, (x_offset, y_offset), user_cutout)

            # --- FRAME LAYER (Uncomment below to enable frame) ---
            # frame_img = Image.open(frame_path).convert("RGBA")
            # frame_img = frame_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
            # background.paste(frame_img, (0, 0), frame_img)
            
            # --- FINAL PREVIEW ---
            # Showing a smaller preview to fit screen, but download will be HD
            st.image(background, caption="Preview", width=400)
            
            # --- RENAME & DOWNLOAD ---
            st.write("---")
            
            # English Label for renaming
            custom_name = st.text_input("Enter File Name:", value=f"{location}_Guest")
            
            if not custom_name.endswith(".png"):
                custom_name += ".png"
            
            # Prepare Download Buffer
            buf = io.BytesIO()
            background.save(buf, format="PNG", optimize=True)
            byte_im = buf.getvalue()
            
            st.download_button(
                label=f"📥 Download Image",
                data=byte_im,
                file_name=custom_name,
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")
