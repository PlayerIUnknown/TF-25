# AI Summary Schema Validation Guide

## Overview

The AI Summary endpoint now uses **strict schema validation** to ensure consistent, predictable responses that can be reliably displayed on the frontend.

## Key Features

✅ **Predefined Schema** - AI must return exact structure  
✅ **Type Validation** - All fields validated for correct types  
✅ **JSON Mode** - Groq API forced to return JSON  
✅ **Automatic Sanitization** - Invalid data corrected automatically  
✅ **Fallback Defaults** - Graceful handling of failures  
✅ **Frontend-Ready** - Consistent structure every time  

## Schema Structure

### Required Fields

```json
{
  "total_participants": 15,           // integer
  "completed_surveys": 12,            // integer
  "in_progress_surveys": 3,           // integer
  "completion_rate_percentage": 80.0, // float (0-100)
  "positive_indicators": 45,          // integer
  "negative_indicators": 18,          // integer
  "top_keywords": ["automation", "integration"],  // array[string], 3-10 items
  "key_pain_points": ["pain1", "pain2"],         // array[string], 2-5 items
  "common_workflows": ["workflow1"],              // array[string]
  "technology_trends": ["AI/ML"],                // array[string]
  "main_bottlenecks": ["bottleneck1"],           // array[string]
  "budget_insights": "Budget summary...",        // string
  "security_concerns": ["SOC2", "GDPR"],        // array[string]
  "deployment_preferences": ["Cloud"],           // array[string]
  "key_insights": "2-3 sentence summary...",     // string, 50-500 chars
  "recommendations": "Actionable advice..."      // string, 50-500 chars
}
```

## How It Works

### 1. Schema Definition
**File**: `ai_summary_schema.py`

Defines:
- Field names and types
- Required fields
- Constraints (min/max values, lengths)
- Validation rules

### 2. AI Prompt with Schema
The AI receives:
- Survey data to analyze
- **Exact schema template** it must follow
- Strict instructions on data types
- Examples of expected format

### 3. Forced JSON Mode
```python
response_format={"type": "json_object"}  # Groq API parameter
```
Forces AI to return valid JSON (no markdown, no extra text).

### 4. Response Validation
Every AI response is validated:
```python
is_valid, errors, sanitized_data = validate_summary_response(ai_response)
```

### 5. Sanitization
If validation fails:
- Missing fields → filled with defaults
- Wrong types → converted or defaulted
- Invalid values → corrected
- Frontend always gets valid data ✅

## Validation Rules

### Integer Fields
```python
# Must be integers
total_participants, completed_surveys, in_progress_surveys,
positive_indicators, negative_indicators
```
**Validation**: Converted to int, default to 0 if invalid

### Float Field
```python
# Must be 0-100
completion_rate_percentage: float
```
**Validation**: Must be between 0 and 100, rounded to 2 decimals

### Array Fields
```python
# Must be arrays of strings
top_keywords, key_pain_points, common_workflows,
technology_trends, main_bottlenecks, security_concerns,
deployment_preferences
```
**Validation**: 
- Converted to array if not
- All items converted to strings
- Empty items removed
- Min item requirements enforced:
  - `top_keywords`: min 3 items
  - `key_pain_points`: min 2 items

### String Fields
```python
# Must be strings
budget_insights, key_insights, recommendations
```
**Validation**:
- Converted to string if not
- Trimmed of whitespace
- Length requirements for insights/recommendations:
  - Min: 50 characters
  - Max: 500 characters

## Response Format

### Success with Valid Schema
```json
{
  "success": true,
  "data": {
    "survey_uuid": "abc-123",
    "survey_title": "B2B Research",
    "company": "TechCorp",
    "analysis_date": null,
    "summary": {
      // ... all fields validated
    },
    "schema_validated": true,
    "validation_errors": null
  }
}
```

### Success with Validation Warnings
```json
{
  "success": true,
  "data": {
    "survey_uuid": "abc-123",
    "survey_title": "B2B Research",
    "company": "TechCorp",
    "summary": {
      // ... sanitized data with defaults filled
    },
    "schema_validated": false,
    "validation_errors": [
      "top_keywords should have at least 3 items",
      "key_insights should be at least 50 characters"
    ]
  }
}
```

### Fallback on AI Failure
```json
{
  "success": true,
  "data": {
    "survey_uuid": "abc-123",
    "survey_title": "B2B Research",
    "company": "TechCorp",
    "summary": {
      // ... default summary structure
      "key_insights": "Not enough survey responses...",
      "recommendations": "Collect more survey responses..."
    },
    "error": "AI service error: ...",
    "fallback": true
  }
}
```

## Frontend Integration

### TypeScript Interface
```typescript
interface AISummary {
  total_participants: number;
  completed_surveys: number;
  in_progress_surveys: number;
  completion_rate_percentage: number;
  positive_indicators: number;
  negative_indicators: number;
  top_keywords: string[];
  key_pain_points: string[];
  common_workflows: string[];
  technology_trends: string[];
  main_bottlenecks: string[];
  budget_insights: string;
  security_concerns: string[];
  deployment_preferences: string[];
  key_insights: string;
  recommendations: string;
}

interface SummaryResponse {
  success: boolean;
  data: {
    survey_uuid: string;
    survey_title: string;
    company: string;
    summary: AISummary;
    schema_validated: boolean;
    validation_errors?: string[];
  };
}
```

### React Component Example
```jsx
import { useState, useEffect } from 'react';

function SurveySummaryDashboard({ surveyId }) {
  const [summary, setSummary] = useState<AISummary | null>(null);
  const [validated, setValidated] = useState(true);
  
  useEffect(() => {
    fetch(`/api/surveys/${surveyId}/ai-summary`)
      .then(res => res.json())
      .then(data => {
        setSummary(data.data.summary);
        setValidated(data.data.schema_validated);
        
        // Show warning if validation failed
        if (!data.data.schema_validated) {
          console.warn('Schema validation warnings:', data.data.validation_errors);
        }
      });
  }, [surveyId]);
  
  if (!summary) return <div>Loading...</div>;
  
  return (
    <div className="dashboard">
      {!validated && (
        <div className="warning">
          ⚠️ Some data may be incomplete or estimated
        </div>
      )}
      
      <MetricsCard
        participants={summary.total_participants}
        completionRate={summary.completion_rate_percentage}
      />
      
      <KeywordCloud keywords={summary.top_keywords} />
      
      <PainPointsList points={summary.key_pain_points} />
      
      <InsightsPanel 
        insights={summary.key_insights}
        recommendations={summary.recommendations}
      />
    </div>
  );
}
```

### Safe Data Access
```javascript
// Always safe to access these fields - guaranteed to exist
const summary = response.data.summary;

// Numbers (always integers or floats)
const participants = summary.total_participants; // guaranteed integer
const rate = summary.completion_rate_percentage; // guaranteed 0-100

// Arrays (always arrays, may be empty)
const keywords = summary.top_keywords; // guaranteed array
keywords.forEach(kw => console.log(kw)); // safe iteration

// Strings (always strings, may be empty or default message)
const insights = summary.key_insights; // guaranteed string
```

## Testing

### Test Valid Response
```python
from ai_summary_schema import validate_summary_response

response = {
    "total_participants": 10,
    "completed_surveys": 8,
    "in_progress_surveys": 2,
    "completion_rate_percentage": 80.0,
    "positive_indicators": 25,
    "negative_indicators": 10,
    "top_keywords": ["automation", "cloud", "security"],
    "key_pain_points": ["Manual processes", "Integration issues"],
    "common_workflows": ["Sales", "Support"],
    "technology_trends": ["AI/ML"],
    "main_bottlenecks": ["Data sync"],
    "budget_insights": "Budget range $50K-$100K",
    "security_concerns": ["SOC2", "GDPR"],
    "deployment_preferences": ["Cloud"],
    "key_insights": "Most respondents prefer cloud-based solutions with strong security.",
    "recommendations": "Focus on cloud deployment and automated workflows with compliance."
}

is_valid, errors, sanitized = validate_summary_response(response)
print(f"Valid: {is_valid}")
print(f"Errors: {errors}")
```

### Test Invalid Response (Auto-Fixed)
```python
response = {
    "total_participants": "10",  # string instead of int
    "completed_surveys": 8,
    "top_keywords": "automation",  # string instead of array
    "key_insights": "Too short"  # less than 50 chars
    # missing fields
}

is_valid, errors, sanitized = validate_summary_response(response)
print(f"Valid: {is_valid}")  # False
print(f"Errors: {errors}")    # List of validation errors
print(f"Sanitized: {sanitized}")  # Corrected data with defaults
```

## Benefits for Frontend

### 1. Type Safety
```typescript
// TypeScript knows exact structure
summary.total_participants // number
summary.top_keywords // string[]
summary.key_insights // string
```

### 2. No Undefined Checks
```javascript
// Never undefined - always has a value
summary.top_keywords.map(k => <Keyword key={k} text={k} />)
```

### 3. Consistent UI
```jsx
// Same layout always works
<div className="metrics">
  <Metric label="Participants" value={summary.total_participants} />
  <Metric label="Completion" value={`${summary.completion_rate_percentage}%`} />
  <Metric label="Positive" value={summary.positive_indicators} />
</div>
```

### 4. Error Resilience
```javascript
// Even if AI fails, you get valid structure
if (response.data.fallback) {
  showNotification("Using default analysis - need more data");
}
// Still render UI with default values
```

## Configuration

### Adjust Validation Rules
Edit `ai_summary_schema.py`:

```python
# Change minimum keywords
if field == "top_keywords" and len(sanitized[field]) < 5:  # changed from 3
    errors.append(f"{field} should have at least 5 items")

# Change insights length
if len(sanitized[field]) < 100:  # changed from 50
    errors.append(f"{field} should be at least 100 characters")
```

### Adjust AI Temperature
Edit `routes/surveys.py`:

```python
temperature=0.1  # More strict (default: 0.2)
# or
temperature=0.4  # More creative
```

## Troubleshooting

### Issue: AI Returns Wrong Types
**Solution**: Already handled by sanitization. Check `validation_errors` field.

### Issue: Fields Missing
**Solution**: Defaults automatically filled. Check `schema_validated: false`.

### Issue: Inconsistent Results
**Solution**: Lower temperature (0.1) for more consistent output.

### Issue: Array Too Short
**Solution**: Check `validation_errors` - may need more survey data.

## Schema Updates

To add new fields:

1. **Update schema definition** in `ai_summary_schema.py`:
```python
AI_SUMMARY_SCHEMA["required"].append("new_field")
AI_SUMMARY_SCHEMA["properties"]["new_field"] = {
    "type": "string",
    "description": "Description"
}
```

2. **Update template** in `get_schema_template()`:
```python
"new_field": "default value"
```

3. **Update validation** in `validate_summary_response()`:
```python
if "new_field" in data:
    sanitized["new_field"] = str(data["new_field"])
else:
    sanitized["new_field"] = "default"
```

4. **Update frontend types**:
```typescript
interface AISummary {
  // ... existing fields
  new_field: string;
}
```

## Summary

✅ **Consistent** - Same structure every time  
✅ **Type-Safe** - Validated data types  
✅ **Resilient** - Graceful error handling  
✅ **Frontend-Ready** - No undefined checks needed  
✅ **Production-Ready** - Battle-tested validation  

The schema validation ensures your frontend can **always** safely render AI summaries without worrying about missing fields or wrong types! 🎉

