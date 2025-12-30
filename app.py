import streamlit as st
from rembg import remove
from PIL import Image
import io

# --- CONFIGURATION ---
# Scale Factor: User background ki width ka kitna % hoga (0.85 = 85%)
SCALE_FACTOR = 0.85

# Bottom Buffer: Niche se kitni jagah chhodni hai
# 0.01 ka matlab sirf 1% jagah (Bilkul zameen par)
BOTTOM_BUFFER_PERCENT = 0.01 

st.set_page_config(page_title="Promoter Cam", page_icon="📸")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        .stApp { text-align: center; }
        img { border-radius: 10px; }
        /* Mobile view fix */
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
    with st.spinner('Adjusting Position & Proportions...'):
        try:
            # 1. Load Background
            bg_path = ASSETS[location]["bg"]
            frame_path = ASSETS[location]["frame"]
            
            background = Image.open(bg_path).convert("RGBA")
            bg_w, bg_h = background.size
            
            # 2. Process User Image
            user_img = Image.open(img_file_buffer)
            user_cutout = remove(user_img)
            
            # --- SMART SCALING (Proportion Fix) ---
            orig_w, orig_h = user_cutout.size
            new_width = int(bg_w * SCALE_FACTOR)
            ratio = new_width / orig_w
            new_height = int(orig_h * ratio)
            user_cutout = user_cutout.resize((new_width, new_height))
            
            # --- POSITIONING LOGIC ---
            
            # X: Center mein rakhna
            x_offset = (bg_w - new_width) // 2
            
            # Y: Bottom se thoda upar uthana (Buffer add karna)
            bottom_margin = int(bg_h * BOTTOM_BUFFER_PERCENT)
            y_offset = bg_h - new_height - bottom_margin
            
            # Ensure karte hain ki photo top se bahar na nikal jaye
            if y_offset < 0: y_offset = 0

            # Paste User (Layer 2)
            background.paste(user_cutout, (x_offset, y_offset), user_cutout)
            
            # Paste Frame (Layer 3) - ABHI KE LIYE BAND KIYA HAI
            # frame_img = Image.open(frame_path).convert("RGBA")
            # frame_img = frame_img.resize((bg_w, bg_h))
            # background.paste(frame_img, (0, 0), frame_img)
            
            # --- FINAL RESULT ---
            st.image(background, caption="Final Look", use_column_width=True)
            
            # Download Ready
            buf = io.BytesIO()
            background.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 Download Perfect Photo",
                data=byte_im,
                file_name=f"{location}_trip.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")
