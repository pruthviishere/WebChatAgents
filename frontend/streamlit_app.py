# streamlit_app.py
import streamlit as st
import requests
import json
from pydantic import HttpUrl, ValidationError
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import logging

# Create and configure logger
logging.basicConfig(filename="ui.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")


# Set page configuration
st.set_page_config(
    page_title="Website Business Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add CSS customization
st.markdown("""
<style>
    /* Main container styles */
    .main {
        background-color: #121212;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        background-color: #121212;
    }
    
    /* Card styles */
    .result-card {
        background-color: #1e1e1e;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        margin-bottom: 24px;
        border: 1px solid #2d2d2d;
        transition: transform 0.2s ease-in-out;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        border-color: #3d3d3d;
    }
    
    .metric-card {
        background-color: #2d2d2d;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 16px;
        border: 1px solid #3d3d3d;
    }
    
    /* Text styles */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
        font-weight: 600;
    }
    p, li {
        color: #e0e0e0;
        line-height: 1.6;
    }
    
    /* Confidence score colors */
    .confidence-high {
        color: #4caf50;
        font-weight: 600;
        background-color: rgba(76, 175, 80, 0.1);
        padding: 4px 8px;
        border-radius: 4px;
    }
    .confidence-medium {
        color: #ff9800;
        font-weight: 600;
        background-color: rgba(255, 152, 0, 0.1);
        padding: 4px 8px;
        border-radius: 4px;
    }
    .confidence-low {
        color: #f44336;
        font-weight: 600;
        background-color: rgba(244, 67, 54, 0.1);
        padding: 4px 8px;
        border-radius: 4px;
    }
    
    /* Button styles */
    .stButton>button {
        background-color: #2d2d2d;
        color: #ffffff;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        border: 1px solid #3d3d3d;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #3d3d3d;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Input styles */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #3d3d3d;
        padding: 0.75rem 1rem;
        background-color: #2d2d2d;
        color: #ffffff;
        transition: all 0.2s ease-in-out;
    }
    .stTextInput>div>div>input:focus {
        border-color: #4d4d4d;
        box-shadow: 0 0 0 2px rgba(77, 77, 77, 0.2);
    }
    
    /* Error message styles */
    .stAlert {
        background-color: rgba(244, 67, 54, 0.1);
        border: 1px solid #f44336;
        border-radius: 8px;
        padding: 1rem;
        color: #f44336;
    }
    
    /* Success message styles */
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.1);
        border: 1px solid #4caf50;
        border-radius: 8px;
        padding: 1rem;
        color: #4caf50;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1e1e1e;
    }
    ::-webkit-scrollbar-thumb {
        background: #3d3d3d;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #4d4d4d;
    }
    
    /* Streamlit specific overrides */
    .stMarkdown {
        color: #e0e0e0;
    }
    .stTextInput>label {
        color: #e0e0e0;
    }
    .stExpander {
        background-color: #1e1e1e;
        border: 1px solid #2d2d2d;
    }
    .stExpanderHeader {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def is_valid_url(url):
    """Check if the URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_confidence(score):
    """Format confidence score with color indication."""
    if score >= 0.8:
        return f"<span class='confidence-high'>{score:.2f}</span>"
    elif score >= 0.5:
        return f"<span class='confidence-medium'>{score:.2f}</span>"
    else:
        return f"<span class='confidence-low'>{score:.2f}</span>"

def analyze_website(url, api_key):
    """Send a request to the API to analyze the website."""
    try:
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/api/analyze",
            headers=headers,
            json={"url": url},
            timeout=60
        )
        logger.info("Request headers: %s", headers)
        logger.info("Response status: %s", response.status_code)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Unauthorized: Invalid API key. Please check your API key and try again.")
            return None
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        logger.error("API request failed: %s", str(e))
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error("Unexpected error: %s", str(e))
        return None

# Main application
def main():
    st.title("🔍 Website Business Analyzer")
    
    st.markdown("""
    This application analyzes company websites to extract key business information.
    Please enter your API key and the website URL below to get started.
    """)
    
    # API Key input
    api_key = st.text_input("Enter your app API Key", type="password")
    
    if not api_key:
        st.warning("Please enter your API key to continue")
        st.stop()
    
    # URL input
    url = st.text_input("Enter website URL", "https://www.3ds.com")
    
    with st.expander("Advanced Options", expanded=False):
        st.markdown("These options are for future expansion")
        st.checkbox("Include social media analysis", value=False, disabled=True)
        st.checkbox("Deep crawl (follow links)", value=False, disabled=True)
    
    # Submit button
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        submitted = st.button("Analyze Website", type="primary", use_container_width=True)
    with col2:
        clear = st.button("Clear Results", type="secondary", use_container_width=True)
    
    if clear:
        st.session_state.clear()
    
    if submitted and url:
        if not is_valid_url(url):
            st.error("Please enter a valid URL including http:// or https://")
        else:
            with st.spinner("Analyzing website... This may take a moment."):
                results = analyze_website(url, api_key)
                if results:
                    st.session_state.results = results
    
    # Display results
    if 'results' in st.session_state:
        results = st.session_state.results
        
        # Company header section
        st.markdown(f"## {results['company_name']}")
        st.markdown(f"**Website**: [{results['website_url']}]({results['website_url']})")
        st.markdown(f"**Description**: {results['description']}")
        
        # Main data cards
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container():
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.subheader("🏭 Industry Information")
                st.markdown(f"**Primary Industry**: {results['industry']['industry']}")
                st.markdown(f"**Confidence**: {format_confidence(results['industry']['confidence_score'])}", unsafe_allow_html=True)
                
                if results['industry']['sub_industries']:
                    st.markdown("**Sub-Industries**:")
                    for sub in results['industry']['sub_industries']:
                        st.markdown(f"- {sub}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.subheader("📍 Location")
                if results['location']['headquarters']:
                    st.markdown(f"**Headquarters**: {results['location']['headquarters']}")
                
                if results['location']['offices'] and len(results['location']['offices']) > 0 and results['location']['offices'][0] != "Not found":
                    st.markdown("**Offices**:")
                    for office in results['location']['offices']:
                        st.markdown(f"- {office}")
                
                if results['location']['countries_of_operation'] and len(results['location']['countries_of_operation']) > 0 and results['location']['countries_of_operation'][0] != "Not found":
                    st.markdown("**Countries of Operation**:")
                    for country in results['location']['countries_of_operation']:
                        st.markdown(f"- {country}")
                
                st.markdown(f"**Confidence**: {format_confidence(results['location']['confidence_score'])}", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.subheader("👥 Company Size")
                st.markdown(f"**Size Category**: {results['company_size']['size_category']}")
                if results['company_size']['employee_range'] and results['company_size']['employee_range'] != "Not found":
                    st.markdown(f"**Employee Range**: {results['company_size']['employee_range']}")
                st.markdown(f"**Confidence**: {format_confidence(results['company_size']['confidence_score'])}", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.subheader("💼 Business Information")
                
                if results['founded_year']:
                    st.markdown(f"**Founded**: {results['founded_year']}")
                
                st.markdown("**Products/Services**:")
                for product in results['products_services']:
                    st.markdown(f"- {product}")
                
                if results['technologies'] and len(results['technologies']) > 0 and results['technologies'][0] != "Not found":
                    st.markdown("**Technologies**:")
                    for tech in results['technologies']:
                        st.markdown(f"- {tech}")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Raw JSON data
        with st.expander("Raw JSON Data", expanded=False):
            st.json(results)
    
    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ using FastAPI and Streamlit")

if __name__ == "__main__":
    main()