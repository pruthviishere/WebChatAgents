# Website Business Analyzer

An AI-powered application that extracts key business information from website homepages using web scraping and natural language processing.

## 🌟 Features

- Extract company information from any website homepage
- Identify industry, company size, location, and more
- Secure API with authentication
- User-friendly Streamlit interface
- Detailed JSON responses using Pydantic models

## 🏗️ Architecture

![Architecture Diagram](https://i.imgur.com/KjVYjPL.png)

The system is built with the following components:

1. **FastAPI Backend**:
   - RESTful API for processing website analysis requests
   - Authentication middleware for securing API endpoints
   - Web scraping module for extracting website content
   - AI integration for analyzing website data

2. **Streamlit Frontend**:
   - User-friendly web interface
   - Form for submitting website URLs
   - Results display with visual elements
   - Error handling and validation

3. **External Integrations**:
   - OpenAI GPT for natural language processing
   - BeautifulSoup for web scraping

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern, high-performance web framework
- **Pydantic**: Data validation and parsing
- **BeautifulSoup4**: HTML parsing and data extraction
- **LangChain**: Framework for working with large language models
- **OpenAI API**: GPT-4 model for analyzing website content

### Frontend
- **Streamlit**: Interactive web application interface

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## 📊 Database Schema

This application does not use a persistent database. All data is processed in memory and returned directly to the user. Future versions may include:

- Request logging
- Caching mechanism for previously analyzed websites
- User management system

## 🚀 Deployment Instructions

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Custom API key for authentication

### Environment Variables
Create a `.env` file with the following variables:
```
API_KEY=your_custom_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Local Deployment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/website-business-analyzer.git
cd website-business-analyzer
```

2. Start the application using Docker Compose:
```bash
docker-compose up -d
```

3. Access:
   - API: http://localhost:8000
   - Streamlit UI: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

### Cloud Deployment

The application can be deployed to various cloud platforms:

#### Deploy to Railway
1. Create a new project on Railway
2. Connect your GitHub repository
3. Add environment variables
4. Deploy

#### Deploy to Render
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure build and start commands
4. Add environment variables
5. Deploy

## 📝 API Documentation

### Endpoints

#### POST /analyze
Analyzes a website homepage and extracts business information.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Headers:**
```
Authorization: Bearer your_api_key_here
```

**Response:**
```json
{
  "company_name": "Example Company",
  "website_url": "https://example.com",
  "industry": {
    "industry": "Technology",
    "confidence_score": 0.95,
    "sub_industries": ["Software", "Web Services"]
  },
  "company_size": {
    "size_category": "Medium",
    "employee_range": "50-200",
    "confidence_score": 0.8
  },
  "location": {
    "headquarters": "San Francisco, CA",
    "offices": ["New York", "London"],
    "countries_of_operation": ["United States", "United Kingdom"],
    "confidence_score": 0.9
  },
  "description": "Example Company provides web solutions for businesses.",
  "products_services": ["Website Development", "E-commerce Solutions"],
  "technologies": ["React", "Node.js", "AWS"],
  "founded_year": 2015
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## 💻 Local Development

### Without Docker

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r streamlit-requirements.txt
```

3. Set environment variables:
```bash
export API_KEY=your_custom_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
# On Windows:
# set API_KEY=your_custom_api_key_here
# set OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the FastAPI application:
```bash
uvicorn app.main:app --reload
```

5. Run the Streamlit application (in a separate terminal):
```bash
streamlit run streamlit_app.py
```

## 🧪 Testing

Run the test suite:
```bash
pytest
```

## 🔒 Security Considerations

- API authentication is implemented using a bearer token
- HTTPS is recommended for production deployment
- Environment variables are used for sensitive information
- Input validation is performed using Pydantic

## 🔜 Future Enhancements

- Support for multi-page scraping
- Social media integration for additional company insights
- Competitor analysis
- Historical data tracking
- Export functionality (PDF, CSV)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.