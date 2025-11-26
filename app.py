import streamlit as st
from PIL import Image
import io
import pytesseract
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import numpy as np

# ============================
# THEME STATE
# ============================
if "theme" not in st.session_state:
    st.session_state.theme = "light"  # default light

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# ============================
# SIDEBAR THEME SWITCH
# ============================
st.sidebar.header("Theme")
st.sidebar.button(
    "🌙 Dark Mode" if st.session_state.theme == "light" else "☀️ Light Mode",
    on_click=toggle_theme
)

# ============================
# LIGHT & DARK MODE CSS + SOFT UI + GRADIENT + GLASSMORPHISM
# ============================

light_css = """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {
    background: linear-gradient(135deg, #FDE2F3, #E2D9F3);
    color: #4A3F55 !important;
    font-family: "Inter", sans-serif;
}

h1, h2, h3, h4 {
    color: #C276E8 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(255,255,255,0.9) !important;
    backdrop-filter: blur(8px);
    border-radius: 16px;
}

/* Upload box */
.upload-box {
    border: 2px dashed #F2A7C3;
    padding: 28px;
    border-radius: 16px;
    background: rgba(255,255,255,0.85);
    box-shadow: 0 10px 25px rgba(200, 150, 220, 0.2);
    transition: 0.3s;
}
.upload-box:hover {
    box-shadow: 0 12px 30px rgba(200, 150, 220, 0.35);
}

/* Buttons */
div.stButton > button {
    background-color: #F2A7C3 !important;
    color: white !important;
    border-radius: 16px;
    padding: 14px 28px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    background-color: #E58EB5 !important;
    transform: scale(1.05);
}

/* Textareas */
textarea, .stTextArea textarea {
    background-color: rgba(255, 255, 255, 0.85) !important;
    color: #4A3F55 !important;
    border-radius: 14px !important;
    border: 1px solid #F2A7C3 !important;
    backdrop-filter: blur(5px);
    padding: 10px !important;
}
</style>
"""

dark_css = """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {
    background: linear-gradient(135deg, #2B2137, #4A2E5C);
    color: #FBE9FF !important;
    font-family: "Inter", sans-serif;
}

h1, h2, h3, h4 {
    color: #ECA7FF !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(60,45,85,0.9) !important;
    backdrop-filter: blur(8px);
    border-radius: 16px;
}

/* Upload box */
.upload-box {
    border: 2px dashed #EE9DC5;
    padding: 28px;
    border-radius: 16px;
    background: rgba(58,44,76,0.85);
    box-shadow: 0 10px 25px rgba(238,157,197,0.25);
    transition: 0.3s;
}
.upload-box:hover {
    box-shadow: 0 12px 30px rgba(238,157,197,0.35);
}

/* Buttons */
div.stButton > button {
    background-color: #EE9DC5 !important;
    color: white !important;
    border-radius: 16px;
    padding: 14px 28px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    background-color: #E285B2 !important;
    transform: scale(1.05);
}

/* Textareas */
textarea, .stTextArea textarea {
    background-color: rgba(75,58,92,0.85) !important;
    color: #FBE9FF !important;
    border-radius: 14px !important;
    border: 1px solid #EE9DC5 !important;
    backdrop-filter: blur(5px);
    padding: 10px !important;
}
</style>
"""

st.markdown(light_css if st.session_state.theme == "light" else dark_css, unsafe_allow_html=True)

# ============================
# MAIN APP
# ============================

st.title("📄 Text Photo to PDF")

st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded = st.file_uploader("Upload Photo", type=["png", "jpg", "jpeg"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded:
    img = Image.open(uploaded).convert("RGB")

    st.subheader("Preview")
    st.image(img, use_column_width=True, output_format="PNG")

    st.sidebar.header("PDF Options")
    page_size_choice = st.sidebar.selectbox("Page Layout", ["A4", "LETTER"])
    include_photo = st.sidebar.checkbox("Include Original Photo in PDF", value=True)
    extract_text_opt = st.sidebar.checkbox("Extract Text (OCR)", value=True)

    PAGE_SIZES = {"A4": A4, "LETTER": LETTER}
    page_size = PAGE_SIZES[page_size_choice]

    extracted_text = ""

    # ---------------- OCR ----------------
    if extract_text_opt:
        try:
            extracted_text = pytesseract.image_to_string(img, lang="eng")
        except:
            try:
                import easyocr
                reader = easyocr.Reader(["en"], gpu=False)
                result = reader.readtext(np.array(img))
                extracted_text = "\n".join([r[1] for r in result])
            except:
                st.error("OCR failed. Please install Tesseract or EasyOCR.")

        st.text_area("Extracted Text", value=extracted_text, height=200)

    # ---------------- PDF Generator ----------------
    def create_pdf(img_pil, text, include_image, page_size):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=page_size)

        w, h = page_size
        y = h - 50

        if include_image and img_pil:
            img_w, img_h = img_pil.size
            max_w = w - 100
            scale = max_w / img_w
            new_w = img_w * scale
            new_h = img_h * scale

            img_buf = io.BytesIO()
            img_pil.save(img_buf, format="PNG")
            img_buf.seek(0)

            c.drawImage(ImageReader(img_buf), 50, y - new_h, width=new_w, height=new_h)
            y -= new_h + 40

        if text:
            text_obj = c.beginText(50, y)
            text_obj.setFont("Helvetica", 11)
            for line in text.split("\n"):
                text_obj.textLine(line)
            c.drawText(text_obj)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    # ---------------- PDF BUTTON ----------------
    if st.button("Create PDF"):
        pdf_output = create_pdf(
            img if include_photo else None,
            extracted_text if extract_text_opt else "",
            include_photo,
            page_size
        )
        st.success("PDF başarıyla oluşturuldu!")

        st.download_button(
            "Download PDF",
            data=pdf_output,
            file_name="text-photo.pdf",
            mime="application/pdf"
        )

else:
    st.info("Lütfen bir fotoğraf yükleyin.")
