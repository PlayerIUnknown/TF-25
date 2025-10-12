# AI Survey Summary Endpoint

## Overview
This endpoint aggregates all customer metadata for a survey and uses Groq AI to generate comprehensive insights and analytics.

## Endpoint Details

### URL
```
GET /api/surveys/{survey_uuid}/ai-summary
```

### Description
Fetches all customer responses for a survey, sends the aggregated data to Groq AI for analysis, and returns a structured summary with key metrics and insights.

## Request

### Method
`GET`

### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| survey_uuid | UUID | Yes | The unique identifier of the survey |

### Headers
```
Content-Type: application/json
```

### Example Request
```bash
curl -X GET http://localhost:8000/api/surveys/{survey_uuid}/ai-summary \
  -H "Content-Type: application/json"
```

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "data": {
    "survey_uuid": "abc-123-def-456",
    "survey_title": "B2B SaaS Market Research",
    "company": "TechCorp Inc.",
    "analysis_date": null,
    "summary": {
      "total_participants": 15,
      "completed_surveys": 12,
      "in_progress_surveys": 3,
      "completion_rate_percentage": 80,
      "positive_indicators": 45,
      "negative_indicators": 18,
      "top_keywords": [
        "automation",
        "integration",
        "scalability",
        "security",
        "cloud deployment",
        "API",
        "real-time data",
        "compliance"
      ],
      "key_pain_points": [
        "Manual data entry causing bottlenecks",
        "Legacy system integration challenges",
        "Lack of real-time reporting",
        "High training time for new employees"
      ],
      "common_workflows": [
        "Sales pipeline management",
        "Customer onboarding",
        "Support ticket processing",
        "Inventory management"
      ],
      "technology_trends": [
        "AI/ML automation",
        "Cloud-first infrastructure",
        "API-first architecture",
        "Microservices"
      ],
      "main_bottlenecks": [
        "Manual approval processes",
        "Data synchronization delays",
        "Limited API rate limits",
        "Complex user permissions"
      ],
      "budget_insights": "Most respondents allocated $50K-$100K annually for SaaS tools, with emphasis on ROI within 12 months. Budget flexibility exists for solutions showing clear operational efficiency gains.",
      "security_concerns": [
        "SOC 2 Type II compliance",
        "GDPR data residency",
        "SSO/SAML integration",
        "Role-based access control",
        "Data encryption at rest"
      ],
      "deployment_preferences": [
        "Cloud (AWS/Azure)",
        "Hybrid cloud",
        "Multi-region availability"
      ],
      "key_insights": "The majority of respondents struggle with manual processes and legacy system integration. There's strong demand for automation and real-time capabilities. Security and compliance are non-negotiable requirements.",
      "recommendations": "Focus on seamless integration capabilities, automated workflow features, and robust security certifications. Offer clear ROI metrics and consider a phased implementation approach to reduce training overhead."
    }
  },
  "message": "Success"
}
```

### Error Responses

#### Survey Not Found (404)
```json
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "Survey not found"
  }
}
```

#### No Customer Data (404)
```json
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "No customer data found for this survey"
  }
}
```

#### AI Service Error (500)
```json
{
  "success": false,
  "error": {
    "code": "ai_service_error",
    "message": "Failed to generate AI summary: [error details]"
  }
}
```

## Response Schema

The `summary` object contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| total_participants | number | Total number of customers who started the survey |
| completed_surveys | number | Number of customers who completed all 6 blocks |
| in_progress_surveys | number | Number of customers still in progress |
| completion_rate_percentage | number | Percentage of completed surveys (0-100) |
| positive_indicators | number | Count of positive sentiment/tone responses |
| negative_indicators | number | Count of negative sentiment/challenges mentioned |
| top_keywords | array[string] | 5-10 most frequently mentioned keywords or themes |
| key_pain_points | array[string] | 3-5 main pain points identified |
| common_workflows | array[string] | Most frequently mentioned workflows/processes |
| technology_trends | array[string] | Emerging technologies or trends mentioned |
| main_bottlenecks | array[string] | Frequently mentioned bottlenecks |
| budget_insights | string | Brief summary of budget-related responses |
| security_concerns | array[string] | Security/compliance requirements mentioned |
| deployment_preferences | array[string] | Most common deployment environments |
| key_insights | string | 2-3 sentence summary of important findings |
| recommendations | string | 2-3 sentence actionable recommendations |

## How It Works

### 1. Data Collection
The endpoint:
- Fetches all customers associated with the survey
- Retrieves their metadata (all completed blocks)
- Includes customer demographics (age, gender)
- Gets survey and company context

### 2. Data Aggregation
Structures the data for AI analysis:
```json
{
  "customer_name": "John Doe",
  "age": 35,
  "gender": "male",
  "status": "completed",
  "responses": [
    {
      "block_id": "domain_workflows",
      "data": { /* block parameters */ }
    },
    // ... all 6 blocks
  ]
}
```

### 3. AI Analysis
- Sends aggregated data to Groq AI
- Uses specialized prompt for market research analysis
- Requests structured JSON response
- Temperature: 0.3 (for consistent, focused analysis)
- Max tokens: 2000

### 4. Response Generation
- Parses AI-generated JSON
- Wraps in standard API response format
- Includes survey metadata and context

## Use Cases

### 1. Executive Dashboard
```javascript
// Fetch summary for dashboard
const response = await fetch(`/api/surveys/${surveyId}/ai-summary`);
const { data } = await response.json();

displayMetrics({
  participants: data.summary.total_participants,
  completionRate: data.summary.completion_rate_percentage,
  topPainPoints: data.summary.key_pain_points
});
```

### 2. Report Generation
```javascript
// Generate PDF report with AI insights
const summary = await getSurveyAISummary(surveyId);
generatePDFReport({
  title: summary.survey_title,
  company: summary.company,
  insights: summary.summary.key_insights,
  recommendations: summary.summary.recommendations
});
```

### 3. Competitive Analysis
```javascript
// Compare multiple surveys
const surveys = ['uuid1', 'uuid2', 'uuid3'];
const summaries = await Promise.all(
  surveys.map(id => fetch(`/api/surveys/${id}/ai-summary`))
);

compareKeywords(summaries.map(s => s.data.summary.top_keywords));
comparePainPoints(summaries.map(s => s.data.summary.key_pain_points));
```

## Configuration

The endpoint uses the following configuration from `TF/config.py`:

```python
# Groq API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'default_key')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
```

### Environment Variables
```bash
# .env file
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile  # or other Groq model
```

## Performance Considerations

### Response Time
- Small surveys (1-10 customers): ~3-5 seconds
- Medium surveys (11-50 customers): ~5-10 seconds
- Large surveys (50+ customers): ~10-20 seconds

### Data Limits
- Recommended: Up to 100 customers per survey
- Maximum: Limited by Groq API token limits (~8K tokens input)
- For very large surveys, consider pagination or sampling

### Optimization Tips
1. **Cache Results**: Cache AI summaries for completed surveys
2. **Async Processing**: For large surveys, process in background
3. **Partial Analysis**: Analyze only completed surveys
4. **Rate Limiting**: Implement rate limits to avoid API abuse

## Error Handling

The endpoint handles several error scenarios:

### 1. Invalid Survey UUID
```python
# Returns 404 if survey doesn't exist
if not survey.data:
    return error_response('Survey not found', 'not_found', 404)
```

### 2. No Customer Data
```python
# Returns 404 if no customers enrolled
if not customers.data or len(customers.data) == 0:
    return error_response('No customer data found', 'not_found', 404)
```

### 3. AI Service Failure
```python
# Returns 500 if Groq API fails
except Exception as e:
    return error_response(
        f'Failed to generate AI summary: {str(e)}',
        'ai_service_error',
        500
    )
```

### 4. Invalid JSON from AI
```python
# Wraps invalid JSON in error object
except json.JSONDecodeError:
    summary = {
        "error": "AI response was not valid JSON",
        "raw_response": ai_response
    }
```

## Testing

### Manual Test
```bash
#!/bin/bash

SURVEY_UUID="your-survey-uuid-here"

# Get AI summary
curl -X GET "http://localhost:8000/api/surveys/${SURVEY_UUID}/ai-summary" \
  -H "Content-Type: application/json" \
  | jq '.'

# Check specific metrics
curl -X GET "http://localhost:8000/api/surveys/${SURVEY_UUID}/ai-summary" \
  | jq '.data.summary | {
    participants: .total_participants,
    completion_rate: .completion_rate_percentage,
    top_pain_points: .key_pain_points
  }'
```

### Integration Test
```python
import requests

def test_ai_summary_endpoint():
    survey_uuid = "test-survey-uuid"
    response = requests.get(f'http://localhost:8000/api/surveys/{survey_uuid}/ai-summary')
    
    assert response.status_code == 200
    data = response.json()
    
    assert 'summary' in data['data']
    summary = data['data']['summary']
    
    assert 'total_participants' in summary
    assert 'key_insights' in summary
    assert 'recommendations' in summary
    assert isinstance(summary['top_keywords'], list)
    assert isinstance(summary['key_pain_points'], list)
```

## Security Considerations

1. **API Key Protection**: Keep GROQ_API_KEY secure in environment variables
2. **Input Validation**: Survey UUID is validated before processing
3. **Data Privacy**: Customer names are included; consider anonymization for sensitive data
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **CORS**: Ensure proper CORS configuration for frontend access

## Future Enhancements

### Planned Features
1. **Caching**: Cache completed survey summaries
2. **Export Options**: PDF, CSV export of summaries
3. **Comparative Analysis**: Compare multiple surveys side-by-side
4. **Custom Prompts**: Allow custom analysis prompts
5. **Sentiment Trends**: Track sentiment over time
6. **Demographic Breakdown**: Analyze by age/gender groups
7. **Real-time Updates**: WebSocket for live summary updates

### API Evolution
- Version 2 may include filtering options (by date, completion status, etc.)
- Support for custom metric definitions
- Integration with BI tools (Tableau, PowerBI)

## Dependencies

```python
# TF/requirements.txt
groq==0.32.0  # Added for this feature
Flask==3.0.0
supabase==2.3.0
```

Install dependencies:
```bash
cd TF
pip install -r requirements.txt
```

## Related Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/surveys/{uuid}` | GET | Get survey details |
| `/api/surveys/{uuid}/stats` | GET | Get basic survey statistics |
| `/api/surveys/{uuid}/customers` | GET | List all survey customers |
| `/api/surveys/{uuid}/customers/{uuid}/metadata` | GET | Get individual customer metadata |

## Changelog

### Version 1.0 (Current)
- Initial release
- Basic AI-powered summary generation
- Support for all 6 survey blocks
- Structured JSON response format

---

**Need help?** Check the [main README](./README.md) or contact support.

