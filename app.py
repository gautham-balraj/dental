import streamlit as st
import io
from PIL import Image
from google import genai
from google.genai import types
import base64

# Configuration
st.set_page_config(
    page_title="Dental Radiography Analysis Tool",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hard-coded API key (replace with your actual API key)
API_KEY = "AIzaSyB38bA4GgxitJT3KiSOCzrxS26g0dHcY7M"

# Initialize Gemini client
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=API_KEY)

# Analysis prompt
ANALYSIS_PROMPT = """
You are a specialist in dental radiographic interpretation and periodontics. Analyze the provided dental image and extract all relevant findings, organized under the following headings:

1. Radiographic Data Extracted by AI in Periodontics  
   a. Bone Level Measurements  
      - Alveolar bone height relative to the cementoenamel junction (CEJ)  
      - Pattern and extent of bone loss (horizontal vs. vertical)  
      - Percentage bone loss per tooth or site  
      - Comparative bone loss across arches or quadrants  

   b. Furcation Involvement  
      - Detection and grading of furcation defects (molars)  
      - Classification (Grade I–III) based on visibility  

   c. Periodontal Ligament (PDL) Space Analysis  
      - PDL widening indicative of trauma or mobility  
      - Assessment of tooth support  

   d. Calculus Detection  
      - Radiopaque deposits on root surfaces  
      - Location and extent of subgingival calculus  

   e. Crestal Bone Morphology  
      - Interproximal crestal contour evaluation  
      - Irregular or blunted crests suggesting early disease  

   f. Tooth-Specific Findings  
      - Predicted tooth mobility (based on bone support)  
      - Pathologic migration or drifting  
      - Root proximity or divergence  

   g. Periapical Pathologies  
      - Radiolucencies suggestive of abscesses  
      - Endo-perio lesion identification  

   h. Implant Analysis (if present)  
      - Marginal bone loss around implants  
      - Signs of peri-implantitis  
      - Thread exposure detection  

2. Additional Periodontics-Specific Observations  
   - Other periodontics-related findings (e.g., periodontal cysts, anatomic variants, imaging artifacts).

Present each section in concise bullet points, include any quantitative measurements you can derive, and offer clear clinical interpretation.  
Exclude any patient identifiers or unrelated information—report only the details extracted from the image.
"""

def analyze_dental_image(image_bytes, mime_type):
    """Analyze dental radiograph using Gemini API"""
    try:
        client = genai.Client(api_key=API_KEY)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
                ANALYSIS_PROMPT
            ]
        )
            
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def main():
    # Header
    st.title("🦷 Dental Radiography Analysis Tool")
    st.markdown("Upload a dental radiograph (JPG or PNG) for AI-powered periodontal analysis")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("Instructions")
        st.markdown("""
        **How to use:**
        1. Upload a dental X-ray image (JPG or PNG)
        2. Wait for the AI analysis to complete
        3. Review the detailed radiographic findings
        4. Use the 'Clear' button to analyze a new image
        
        **Supported formats:**
        - JPG/JPEG
        - PNG
        
        **Note:** This tool is for educational purposes only and should not replace professional dental diagnosis.
        """)
    
    # Initialize session state
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a dental radiograph image...",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=False
    )
    
    # Clear button
    if st.button("🗑️ Clear", type="secondary"):
        st.session_state.clear()  # This also clears all session state
        st.rerun()
    
    # Process uploaded image
    if uploaded_file is not None:
        # Store uploaded image in session state
        st.session_state.uploaded_image = uploaded_file
        
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📸 Uploaded Image")
            # Reset file pointer before opening with PIL
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)
            st.image(image, caption="Dental Radiograph", use_container_width=True)
        
        with col2:
            st.subheader("📋 Analysis Results")
            
            # Analyze button
            if st.button("🔍 Analyze Radiograph", type="primary"):
                # Show spinner while processing
                with st.spinner("🔄 Analyzing radiograph... Please wait for a min"):
                    # Reset file pointer and read image bytes
                    uploaded_file.seek(0)
                    image_bytes = uploaded_file.read()
                    
                    # Determine MIME type more reliably
                    file_type = uploaded_file.type
                    if file_type == "image/jpg":
                        mime_type = "image/jpeg"
                    elif file_type in ["image/jpeg", "image/png"]:
                        mime_type = file_type
                    else:
                        # Fallback based on file name
                        if uploaded_file.name.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        elif uploaded_file.name.lower().endswith('.png'):
                            mime_type = "image/png"
                        else:
                            mime_type = "image/jpeg"  # Default fallback
                    
                    # Analyze image
                    result = analyze_dental_image(image_bytes, mime_type)
                    st.session_state.analysis_result = result
                
                # Success message
                st.success("✅ Analysis completed!")
            
            # Display results if available
            if st.session_state.analysis_result:
                st.markdown("### Analysis Results")
                st.markdown(st.session_state.analysis_result)
                
                # Download button for results
                st.download_button(
                    label="📄 Download Analysis Report",
                    data=st.session_state.analysis_result,
                    file_name="dental_radiography_analysis.md",
                    mime="text/markdown"
                )
    
    # Display example if no image uploaded
    else:
        st.info("👆 Please upload a dental radiograph image to begin analysis")
        
        # Example section
        st.markdown("---")
        st.subheader("🔍 What this tool analyzes:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Bone Level Measurements:**
            - Alveolar bone height
            - Bone loss patterns
            - Percentage calculations
            
            **Periodontal Assessment:**
            - Furcation involvement
            - PDL space analysis
            - Crestal bone morphology
            """)
        
        with col2:
            st.markdown("""
            **Pathology Detection:**
            - Calculus deposits
            - Periapical lesions
            - Implant complications
            
            **Clinical Insights:**
            - Mobility predictions
            - Treatment recommendations
            - Risk assessments
            """)

if __name__ == "__main__":
    main()