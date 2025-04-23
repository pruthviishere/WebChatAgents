# app/core/analyzer.py
import re
import os
from typing import Dict, Any
import json
from app.extractors.factory import ExtractorFactory, ExtractorType
from app.models.business import BusinessDetails
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from app.utils.logging import logger
from fastapi import APIRouter, HTTPException, Depends
 # You'll need to create this if not exists
from pydantic import BaseModel, HttpUrl
from app.utils.auth import verify_api_key
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda

import openai
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


class WebsiteRequest(BaseModel):
    url: str = Field(..., description="Website URL to analyze", example="https://example.com")

# Create the router
router = APIRouter(
    prefix="/analyze",
    tags=["analyzer"]
)
# Add the endpoint
@router.post("/", response_model=BusinessDetails)
async def analyze_website_endpoint(
    request: WebsiteRequest,
    # api_key_valid: bool = Depends(verify_api_key)
):
    """
    Analyze a website homepage to extract business details.
    """
    try:
        # Select best extractor
        extractor_type = await select_best_extractor(str(request.url))
        
        # Create extractor instance
        extractor = ExtractorFactory.create_extractor(extractor_type)
        
        # Extract content
        extracted_data = await extractor.extract(str(request.url))
        
        # Analyze content
        business_details = await analyze_website(extracted_data, str(request.url))
        
        return business_details
        
    except Exception as e:
        logger.error(f"Error analyzing website: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing website: {str(e)}"
        )
    
async def select_best_extractor(url: str) -> ExtractorType:
    """Select the best extractor for a given URL.
    
    Args:
        url: The URL to analyze
        
    Returns:
        The most appropriate extractor type for the URL
    """
    # Check for common SPAs and JS-heavy websites
    spa_patterns = [
        r'react', r'vue', r'angular', r'svelte', r'next\.js', r'nuxt'
    ]
    
    # Check for common e-commerce platforms
    ecommerce_patterns = [
        r'shopify', r'magento', r'woocommerce', r'bigcommerce'
    ]
    
    # Default to BeautifulSoup for most sites
    extractor_type = ExtractorType.BEAUTIFUL_SOUP
    
    # For SPAs and complex JS sites, use Playwright
    for pattern in spa_patterns + ecommerce_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            extractor_type = ExtractorType.PLAYWRIGHT
            break
    
    logger.info(f"Selected extractor {extractor_type.value} for URL: {url}")
    return extractor_type

async def analyze_website(extracted_data: Dict[str, Any], url: str) -> BusinessDetails:
    """Analyze website content to extract business details.
    
    Args:
        extracted_data: Dictionary containing extracted website content
        url: The URL of the website
        
    Returns:
        BusinessDetails object with extracted business information
    """
    # Prepare content for LLM analysis
    title = extracted_data.get("title", "")
    meta_description = extracted_data.get("meta_description", "")
    meta_keywords = extracted_data.get("meta_keywords", "")
    content = extracted_data.get("content", "")
    
    # Create enriched content with metadata
    enriched_content = (
        f"Title: {title}\n"
        f"Meta Description: {meta_description}\n"
        f"Meta Keywords: {meta_keywords}\n\n"
        f"Content:\n{content}"
    )
    return call_llm(enriched_content,url)

def call_llm_json():
    pass
import os
from openai import OpenAI
from pydantic import BaseModel, Field

 

def gpt_call(prompt: str, temperature: float = 0.0) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides information in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature,
        response_format={"type": "json_object"}  # Correct parameter placement
    )
    
    response_content = response.choices[0].message.content.strip()
    print(f"Raw response: {response_content}")
    return response_content

def call_llm(enriched_content, url) -> BusinessDetails:
    # Generate the schema
    schema = BusinessDetails.model_json_schema()
    prompt = f"""
    You are an expert business analyst. Analyze the following website content and extract key business information.
    Website Content:
    {enriched_content}
    Website URL: {url}
    Return the results in JSON format with the following structure:
    {schema}
    """

    try:
        response_text = gpt_call(prompt)
        business_data = BusinessDetails.parse_raw(response_text)
        return business_data
    except Exception as e:
        print(f"Error processing response: {e}")
        print(f"Response text: {response_text}")
        # Return a default object to prevent crashes
        return BusinessDetails()

def call_llmw(enriched_content: str, url: str) -> BusinessDetails:
    # Initialize the LLM with aisuite
    llm = aisuite.LLM(model="openai:gpt-4o-mini" )
    json_schema = BusinessDetails.__get_pydantic_json_schema__
    logger.info("schema %s", json_schema)
    prompt_template = PromptTemplate(
        template="""
    You are an expert business analyst. Analyze the following website content and extract key business information.

    Website Content:
    {content}

    Website URL: {url}

    Extract the following information. Return your response **only** in JSON format that matches the structure below:

    {format_instructions}
    """,
        input_variables=["content", "url"],
        partial_variables={"format_instructions": json_schema}
    )
    # Format the prompt with the provided content and URL
    prompt = prompt_template.format(content=enriched_content, url=url)

    # Call the LLM to get the response
    response = llm.chat([{"role": "user", "content": prompt}])
    logger.info("reso %s",response)
    # Parse the response into the BusinessDetails model
    business_details = BusinessDetails.model_json_schema(response['choices'][0]['message']['content'])

    return business_details
  
def call_llm2(enriched_content,url)->BusinessDetails:

     # Prepare content for LLM analysis
 
    # Step 2: Create a parser based on the schema
    # parser = StructuredOutputParser.from_pydantic(BusinessDetails)
    # Step 1: Define parser
    parser = PydanticOutputParser(pydantic_object=BusinessDetails)
    # Step 2: Wrap the parser as a Runnable
    parser_runnable = RunnableLambda(parser.parse)
    content = enriched_content

    # Step 3: Create your prompt template with formatting instructions
    prompt = PromptTemplate(
        template="""
    You are an expert business analyst. Analyze the following website content and extract key business information.

    Website Content:
    {content}

    Website URL: {url}

    Extract the following information. Return your response **only** in JSON format that matches the structure below:

    {format_instructions}
    """,
        input_variables=["content", "url"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # Step 4: Build and invoke the chain
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2,   model_kwargs={"response_format": {"type": "json"}})
    
    chain = prompt | llm | parser_runnable

    # Step 5: Call the chain
    result = chain.invoke({
        "content": enriched_content,
        "url": url
    })

    # # Now `result` is a parsed BusinessDetails object!
    # return result

    
    # prompt = PromptTemplate(
    #     input_variables=["content", "url"],
    #     template=prompt_template
    # )
    
    # # Create and run chain
    # # chain = LLMChain(llm=llm, prompt=prompt)
    # # result = chain.run(content=enriched_content, url=url)
    # # Initialize your LLM
    # llm = OpenAI()

    # # Create the chain using LCEL
    # chain = prompt | llm | StrOutputParser()

    # # Invoke the chain with your inputs
    # result = chain.invoke({"content": enriched_content, "url": url})
    # # Parse the result (cleanup JSON and convert to BusinessDetails)
    # 
    # import re
    
    # # Find JSON content (sometimes LLM adds extra text before/after JSON)
    # json_match = re.search(r'({[\s\S]*})', result)
    # if json_match:
    #     result = json_match.group(1)
    
    # Parse JSON into BusinessDetails model
    business_data = json.loads(result)
    return BusinessDetails(**business_data)