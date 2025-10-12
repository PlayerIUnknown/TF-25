# AI Summary Quick Start Guide

## What is it?

The AI Summary endpoint analyzes all customer responses from a survey and generates intelligent insights using Groq AI. It provides metrics like pain points, keywords, trends, and actionable recommendations.

## Quick Setup

### 1. Install Dependencies
```bash
cd TF
pip install -r requirements.txt  # Includes groq==0.32.0
```

### 2. Configure API Key
Add to your `.env` file or use the default in `config.py`:
```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Start the Server
```bash
python app.py
# Server runs on http://localhost:8000
```

## Usage

### Simple GET Request
```bash
curl http://localhost:8000/api/surveys/{survey_uuid}/ai-summary
```

### Using Python
```python
import requests

survey_uuid = "abc-123-def-456"
response = requests.get(f'http://localhost:8000/api/surveys/{survey_uuid}/ai-summary')
data = response.json()

summary = data['data']['summary']
print(f"Participants: {summary['total_participants']}")
print(f"Completion Rate: {summary['completion_rate_percentage']}%")
print(f"Top Pain Point: {summary['key_pain_points'][0]}")
```

### Using JavaScript/Fetch
```javascript
const surveyUuid = 'abc-123-def-456';
const response = await fetch(`/api/surveys/${surveyUuid}/ai-summary`);
const { data } = await response.json();

console.log('Completion Rate:', data.summary.completion_rate_percentage);
console.log('Top Keywords:', data.summary.top_keywords);
console.log('Key Insights:', data.summary.key_insights);
```

## What You Get

### Metrics Returned
```json
{
  "total_participants": 15,
  "completed_surveys": 12,
  "completion_rate_percentage": 80,
  "positive_indicators": 45,
  "negative_indicators": 18,
  "top_keywords": ["automation", "integration", "scalability"],
  "key_pain_points": ["Manual data entry", "Integration issues"],
  "common_workflows": ["Sales pipeline", "Customer onboarding"],
  "technology_trends": ["AI/ML", "Cloud-first"],
  "main_bottlenecks": ["Manual approvals", "Data sync delays"],
  "budget_insights": "Budget range $50K-$100K annually...",
  "security_concerns": ["SOC 2", "GDPR", "SSO"],
  "deployment_preferences": ["Cloud (AWS/Azure)", "Hybrid"],
  "key_insights": "Summary of important findings...",
  "recommendations": "Actionable recommendations..."
}
```

## Examples

### Example 1: Dashboard Widget
```javascript
async function displaySurveyMetrics(surveyId) {
  const response = await fetch(`/api/surveys/${surveyId}/ai-summary`);
  const { data } = await response.json();
  const { summary } = data;
  
  document.getElementById('participants').textContent = summary.total_participants;
  document.getElementById('completion-rate').textContent = 
    `${summary.completion_rate_percentage}%`;
  
  // Display top pain points
  const painPointsList = document.getElementById('pain-points');
  summary.key_pain_points.forEach(point => {
    const li = document.createElement('li');
    li.textContent = point;
    painPointsList.appendChild(li);
  });
}
```

### Example 2: Generate Report
```python
from example_ai_summary_usage import SurveyAnalyzer

analyzer = SurveyAnalyzer()

# Print formatted report
analyzer.print_summary_report('your-survey-uuid')

# Export to JSON
analyzer.export_to_json('your-survey-uuid', 'report.json')
```

### Example 3: Compare Surveys
```python
analyzer = SurveyAnalyzer()

survey_ids = ['uuid-1', 'uuid-2', 'uuid-3']
analyzer.compare_surveys(survey_ids)
```

## Testing

### Test Script
```bash
chmod +x test_ai_summary.sh
./test_ai_summary.sh your-survey-uuid
```

This will:
- Fetch the AI summary
- Display key metrics
- Show top keywords and pain points
- Save full response to JSON file

## Response Time

| Survey Size | Expected Time |
|-------------|---------------|
| 1-10 customers | 3-5 seconds |
| 11-50 customers | 5-10 seconds |
| 50+ customers | 10-20 seconds |

## Common Use Cases

### 1. Executive Dashboard
Show high-level metrics and insights to stakeholders.

### 2. Product Planning
Use pain points and recommendations to prioritize features.

### 3. Market Research
Analyze keywords and trends across multiple surveys.

### 4. Sales Enablement
Extract key insights for sales presentations.

### 5. Competitive Analysis
Compare pain points and requirements across customer segments.

## Tips

### 1. Best Results
- Wait for at least 5-10 completed surveys
- More data = better insights
- Complete surveys provide richer analysis

### 2. Performance
- Cache results for completed surveys
- Consider background processing for large surveys
- Implement rate limiting

### 3. Customization
- Modify the prompt in `routes/surveys.py` for specific needs
- Adjust temperature (0.1-0.5) for different analysis styles
- Increase max_tokens for more detailed responses

## Troubleshooting

### Error: "No customer data found"
**Solution**: Ensure customers have enrolled and completed at least some blocks.

### Error: "AI service error"
**Solution**: Check your GROQ_API_KEY is valid and has credits.

### Slow Response
**Solution**: Reduce the amount of data or implement caching.

### Invalid JSON Response
**Solution**: The AI occasionally returns malformed JSON. The endpoint handles this gracefully and returns the raw response.

## API Reference

Full documentation: [AI_SUMMARY_ENDPOINT.md](./AI_SUMMARY_ENDPOINT.md)

**Endpoint**: `GET /api/surveys/{survey_uuid}/ai-summary`

**Response Structure**:
```json
{
  "success": true,
  "data": {
    "survey_uuid": "...",
    "survey_title": "...",
    "company": "...",
    "summary": { /* metrics object */ }
  }
}
```

## Next Steps

1. ✅ Test the endpoint with your survey
2. ✅ Integrate into your frontend
3. ✅ Set up caching for completed surveys
4. ✅ Build visualizations for metrics
5. ✅ Create automated reports

## Support

- **Documentation**: [AI_SUMMARY_ENDPOINT.md](./AI_SUMMARY_ENDPOINT.md)
- **Examples**: [example_ai_summary_usage.py](./example_ai_summary_usage.py)
- **Test Script**: [test_ai_summary.sh](./test_ai_summary.sh)

---

**That's it!** You now have AI-powered survey analysis. 🚀

