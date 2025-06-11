import streamlit as st
from google import genai
from google.genai import types
from pathlib import Path
from PIL import Image
import os

from dotenv import load_dotenv

load_dotenv() 

Google_API_KEY = os.getenv("GOOGLE_API_KEY")
# ---- LOGO SETUP ----
# Use your actual file paths or URLs for logos
client_logo_path = "logos\pri_logo.png"  # Replace with your client logo filename
pri_logo_path = "logos\schneider_logo.png"  # Replace with your company logo filename

# ---- PAGE LAYOUT ----
st.set_page_config(
    page_title="Estimate Blueprint - PRI Global",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- HEADER WITH LOGOS ---
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.image(pri_logo_path, width=240)
with col2:
    st.markdown(
        "<h1 style='text-align: center; color: #20435c;'>Estimate Blueprint</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align: center; font-size:18px; color: #6e8898;'>Powered by PRI Global | AI-Driven Blueprint Insights</div>",
        unsafe_allow_html=True
    )
with col3:
    st.image(client_logo_path, width=250)

st.markdown("---")

# ---- PDF ANALYZER UI ----
st.markdown(
    "<b>Step 1:</b> Upload your <span style='color:#20435c;'>construction blueprint or floorplan</span> (PDF).",
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

st.markdown(
    "<b>Step 2:</b> What would you like to know? (e.g., 'Estimate the cost of this floor plan including basic materials and labor')",
    unsafe_allow_html=True,
)
user_prompt = st.text_area("Your Question", value="", height=80, placeholder="Describe what cost estimate or details you want...")

# ---- Custom AI Prompt Template ----
# This is the template sent to Gemini in backend.
prompt_template = (
    """
    You are an AI assistant specialized in construction cost estimation. Your primary task is to analyze architectural blueprints (provided as images or OCR text from images) and generate a comprehensive budget estimate for the renovation or construction project depicted.

    **Your process should be as follows:**

    1.  **Understand the Scope:** Carefully examine all provided blueprint pages (e.g., floor plans, elevations, material schedules) to grasp the full scope of work. Identify key areas (e.g., bathroom, kitchen), fixture types, material specifications, and dimensions.
    2.  **Material Identification & Quantification:**
        *   Extract all specified materials (e.g., FT-1, WT-2, CM-1, HW-3) and their descriptions (e.g., "Meram Blanc Carrara Polished 8"x18", "Kohler Memoire Stately Toilet").
        *   Using the provided dimensions and typical construction practices, estimate the quantity needed for each material. Include a reasonable overage (e.g., 10-15% for tile).
    3.  **Material Pricing:**
        *   For each identified material, research current retail prices. Assume sourcing from common suppliers like Home Depot, Lowe's, Ferguson, The Tile Shop, Wayfair, or specialty online retailers for specific brands if mentioned (e.g., Kallista, Kohler).
        *   Provide a price range (low-end to high-end) if significant variations exist for similar quality items or if brand specificity allows for it.
    4.  **Labor Estimation:**
        *   Break down the project into standard construction tasks (e.g., Demolition, Plumbing Rough-in, Electrical Rough-in, Tiling, Carpentry, Painting, Fixture Installation).
        *   Estimate the labor hours or days required for each task based on the project's complexity and scale.
        *   Apply a general industry average labor rate (clearly state if you are using a placeholder or if you can access regional data).
    5.  **Quote Generation:** Structure your output clearly:
        *   **Project Scope Summary:** A brief overview of the project.
        *   **Important Disclaimers:** Crucially, include disclaimers stating:
            *   This is an estimate, not a formal bid.
            *   Labor costs are highly variable by region and contractor.
            *   Material prices fluctuate.
            *   Unforeseen conditions are not accounted for.
            *   Permits and fees are not included.
            *   The user should obtain multiple bids from licensed contractors.
        *   **Estimated Material Cost Breakdown:** Present in a table format: `| Item Code | Description & Location | Plan Specs | Est. Qty Needed | Est. Unit Price (or Range) | Est. Total (or Range) |`
        *   **Estimated Labor Cost Breakdown:** Present in a table format: `| Trade / Task | Description of Work | Est. Time | Estimated Cost (or Range) |`
        *   **Total Project Cost Summary:** Show `| Category | Low-End Estimate | High-End Estimate |` including:
            *   Total Estimated Material Cost
            *   Total Estimated Labor Cost
            *   Subtotal
            *   A line item for Contractor Overhead/Profit & Contingency (e.g., 15-20% of subtotal).
            *   **GRAND TOTAL ESTIMATED PROJECT COST (Range)**

    **Key Instructions:**

    *   Be thorough and detail-oriented.
    *   If a dimension or specification is missing, make a reasonable assumption and clearly state it.
    *   Prioritize materials and fixtures explicitly mentioned in the plans.
    *   If "or equivalent" is stated, research a common, good-quality equivalent.
    *   Your goal is to provide a realistic budget range to help the user plan their project.
    *   Maintain a professional and helpful tone.
    """
    "Provide a clear and concise estimation and answer the following user query: \n\n"
    "{user_prompt}\n\n"
)

run_button = st.button("Analyze & Estimate")

if run_button:
    if not uploaded_file or not user_prompt.strip():
        st.warning("Please upload a PDF and enter your estimation question.")
    else:
        with st.spinner("Analyzing blueprint and estimating costs..."):
            temp_path = Path("temp_uploaded.pdf")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            try:
                full_prompt = prompt_template.format(user_prompt=user_prompt)
                response = genai.Client(
                    api_key=Google_API_KEY
                ).models.generate_content(
                    model="gemini-2.5-pro-preview-06-05",
                    contents=[
                        types.Part.from_bytes(
                            data=temp_path.read_bytes(),
                            mime_type='application/pdf'
                        ),
                        full_prompt
                    ]
                )
                st.success("Estimation Complete!")
                st.subheader("AI Cost Estimation Output")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                temp_path.unlink(missing_ok=True)

st.markdown(
    "<div style='text-align:center; margin-top: 3em; color:#aaa; font-size:13px;'>PRI Global &copy; 2025. All Rights Reserved.</div>",
    unsafe_allow_html=True,
)
