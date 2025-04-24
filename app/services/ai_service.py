from typing import Dict, Any, Optional
from app.models.business import BusinessDetails
from app.models.question import QuestionResponse
from app.utils.logging import logger

class AIService:
    """Service for AI-related operations"""
    
    @staticmethod
    def extract_answer_from_business_details(question: str, business_details: BusinessDetails) -> Optional[QuestionResponse]:
        """Extract answer from business details based on question"""
        question = question.lower()
        
        # Industry related questions
        if any(keyword in question for keyword in ["industry", "sector", "business type"]):
            return QuestionResponse(
                answer=business_details.industry.industry,
                confidence=business_details.industry.confidence_score,
                source="industry_data"
            )
        
        # Company size related questions
        if any(keyword in question for keyword in ["size", "employees", "how big", "how many people"]):
            return QuestionResponse(
                answer=business_details.company_size.size_category,
                confidence=business_details.company_size.confidence_score,
                source="company_size_data"
            )
        
        # Location related questions
        if any(keyword in question for keyword in ["location", "headquarters", "where", "based"]):
            return QuestionResponse(
                answer=business_details.location.headquarters,
                confidence=business_details.location.confidence_score,
                source="location_data"
            )
        
        return None

    @staticmethod
    async def analyze_website(extracted_data: Dict[str, Any], url: str) -> BusinessDetails:
        """Analyze website content to extract business details"""
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
        
        return await AIService.call_llm(enriched_content, url)

    @staticmethod
    async def call_llm(enriched_content: str, url: str) -> BusinessDetails:
        """Call LLM to analyze website content"""
        try:
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
            
            response_text = await AIService.gpt_call(prompt)
            business_data = BusinessDetails.parse_raw(response_text)
            return business_data
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            logger.error(f"Response text: {response_text}")
            return BusinessDetails()

    @staticmethod
    async def gpt_call(prompt: str, temperature: float = 0.0) -> str:
        """Make a call to GPT API"""
        import os
        from openai import OpenAI
        
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
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content.strip() 