import streamlit as st
from rembg import remove
from PIL import Image
import io

# --- CONFIGURATION (SETTINGS) ---

# 1. QUALITY SETTINGS (Force HD Resolution)
# Hum tay kar rahe hain ki final photo 1080x1920 hi hogi.
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# 2. SIZE SETTING (Zoom Fix)
# User background ki chaudai ka 95% hissa lega (Pehle 85% tha).
# Isse user bada dikhega.
SCALE_FACTOR = 0.95

# 3. POSITION SETTING (Hawa me udna band)
# 0.0 matlab bilkul zameen (bottom edge) se chipka hua.
BOTTOM_BUFFER_PERCENT = 0.0

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
    with st.spinner('High Quality Processing...'):
        try:
            # 1. Load & Force Resize Background to HD using LANCZOS (Best Quality Filter)
            bg_path = ASSETS[location]["bg"]
            # frame_path = ASSETS[location]["frame"] # Frame abhi band hai
            
            # Background ko High Quality me resize karte hain
            background = Image.open(bg_path).convert("RGBA")
            background = background.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
            bg_w, bg_h = background.size # Ye ab 1080x1920 hoga
            
            # 2. Process User Image (Remove BG)
            user_img = Image.open(img_file_buffer)
            user_cutout = remove(user_img)
            
            # --- SCALING & POSITION ---
            orig_w, orig_h = user_cutout.size
            
            # Naya width calculate karna (95% of 1080)
            new_width = int(bg_w * SCALE_FACTOR)
            # Height ratio ke hisaab se
            ratio = new_width / orig_w
            new_height = int(orig_h * ratio)
            
            # User ko resize karna (High Quality filter ke sath)
            user_cutout = user_cutout.resize((new_width, new_height), Image.LANCZOS)
            
            # Positioning Calculations
            x_offset = (bg_w - new_width) // 2
            
            # Bottom margin ab 0 hai
            bottom_margin = int(bg_h * BOTTOM_BUFFER_PERCENT)
            y_offset = bg_h - new_height - bottom_margin
            
            # Ensure karte hain top se bahar na nikle
            if y_offset < 0: y_offset = 0

            # Paste User
            background.paste(user_cutout, (x_offset, y_offset), user_cutout)

            # --- FRAME LAYER (Agar future me chahiye ho to uncomment karein) ---
            # frame_img = Image.open(frame_path).convert("RGBA")
            # frame_img = frame_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
            # background.paste(frame_img, (0, 0), frame_img)
            
            # --- FINAL SHOW ---
            # Display thoda chhota dikhayenge taaki screen par fit ho, par download full quality hoga
            st.image(background, caption="Final High-Quality Look", width=400)
            
            # --- RENAME & DOWNLOAD ---
            st.write("---")
            custom_name = st.text_input("File ka naam likhein:", value=f"{location}_Guest")
            if not custom_name.endswith(".png"):
                custom_name += ".png"
            
            # Prepare Download (Full HD)
            buf = io.BytesIO()
            background.save(buf, format="PNG", optimize=True)
            byte_im = buf.getvalue()
            
            st.download_button(
                label=f"📥 Download HQ Image",
                data=byte_im,
                file_name=custom_name,
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")
