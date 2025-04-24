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
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    st.error("API_KEY environment variable not set")
    st.stop()


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
    .main {
        background-color: #f5f7f9;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .confidence-high {
        color: #28a745;
    }
    .confidence-medium {
        color: #ffc107;
    }
    .confidence-low {
        color: #dc3545;
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

def analyze_website(url):
    """Send a request to the API to analyze the website."""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/api/analyze",
            headers=headers,
            json={"url": url},
            timeout=60
        )
        logger.info(" header %s response %s",headers,response )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

# Main application
def main():
    st.title("🔍 Website Business Analyzer")
    
    st.markdown("""
    This application analyzes company websites to extract key business information.
    Simply enter a website URL below to get started.
    """)
    
    # URL input
    url = st.text_input("Enter website URL", "https://www.example.com")
    
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
                results = analyze_website(url)
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