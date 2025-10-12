"""
JSON Schema for AI Survey Summary Response
This defines the exact structure that AI must return
"""

# Expected response schema from AI
AI_SUMMARY_SCHEMA = {
    "type": "object",
    "required": [
        "total_participants",
        "completed_surveys",
        "in_progress_surveys",
        "completion_rate_percentage",
        "positive_indicators",
        "negative_indicators",
        "top_keywords",
        "key_pain_points",
        "common_workflows",
        "technology_trends",
        "main_bottlenecks",
        "budget_insights",
        "security_concerns",
        "deployment_preferences",
        "key_insights",
        "recommendations"
    ],
    "properties": {
        "total_participants": {
            "type": "integer",
            "description": "Total number of survey participants"
        },
        "completed_surveys": {
            "type": "integer",
            "description": "Number of completed surveys"
        },
        "in_progress_surveys": {
            "type": "integer",
            "description": "Number of surveys still in progress"
        },
        "completion_rate_percentage": {
            "type": "number",
            "description": "Completion rate as percentage (0-100)"
        },
        "positive_indicators": {
            "type": "integer",
            "description": "Count of positive sentiment responses"
        },
        "negative_indicators": {
            "type": "integer",
            "description": "Count of negative sentiment/challenge responses"
        },
        "top_keywords": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 10,
            "description": "5-10 most frequently mentioned keywords or themes"
        },
        "key_pain_points": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 5,
            "description": "3-5 main pain points identified"
        },
        "common_workflows": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Most mentioned workflows or processes"
        },
        "technology_trends": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Emerging technologies or trends mentioned"
        },
        "main_bottlenecks": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Frequently mentioned bottlenecks or friction points"
        },
        "budget_insights": {
            "type": "string",
            "description": "Brief summary of budget-related responses"
        },
        "security_concerns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Security and compliance requirements mentioned"
        },
        "deployment_preferences": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Most common deployment environments mentioned"
        },
        "key_insights": {
            "type": "string",
            "minLength": 50,
            "maxLength": 500,
            "description": "2-3 sentence summary of most important findings"
        },
        "recommendations": {
            "type": "string",
            "minLength": 50,
            "maxLength": 500,
            "description": "2-3 sentence actionable recommendations"
        }
    }
}


def get_schema_template():
    """
    Returns a template JSON object showing the expected structure
    This is sent to the AI as an example
    """
    return {
        "total_participants": 0,
        "completed_surveys": 0,
        "in_progress_surveys": 0,
        "completion_rate_percentage": 0.0,
        "positive_indicators": 0,
        "negative_indicators": 0,
        "top_keywords": ["keyword1", "keyword2", "keyword3"],
        "key_pain_points": ["pain point 1", "pain point 2", "pain point 3"],
        "common_workflows": ["workflow1", "workflow2"],
        "technology_trends": ["trend1", "trend2"],
        "main_bottlenecks": ["bottleneck1", "bottleneck2"],
        "budget_insights": "Summary of budget discussions...",
        "security_concerns": ["concern1", "concern2"],
        "deployment_preferences": ["preference1", "preference2"],
        "key_insights": "2-3 sentence summary of the most important findings...",
        "recommendations": "2-3 sentence actionable recommendations based on the data..."
    }


def validate_summary_response(data):
    """
    Validates that AI response matches the expected schema
    
    Args:
        data: The AI response to validate
        
    Returns:
        tuple: (is_valid: bool, errors: list, sanitized_data: dict)
    """
    errors = []
    sanitized = {}
    
    # Check all required fields exist
    for field in AI_SUMMARY_SCHEMA["required"]:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate each field type and constraints
    # Integers
    int_fields = ["total_participants", "completed_surveys", "in_progress_surveys", 
                  "positive_indicators", "negative_indicators"]
    for field in int_fields:
        if field in data:
            try:
                sanitized[field] = int(data[field])
            except (ValueError, TypeError):
                errors.append(f"{field} must be an integer")
                sanitized[field] = 0
        else:
            sanitized[field] = 0
    
    # Float (completion rate)
    if "completion_rate_percentage" in data:
        try:
            rate = float(data["completion_rate_percentage"])
            if 0 <= rate <= 100:
                sanitized["completion_rate_percentage"] = round(rate, 2)
            else:
                errors.append("completion_rate_percentage must be between 0 and 100")
                sanitized["completion_rate_percentage"] = 0.0
        except (ValueError, TypeError):
            errors.append("completion_rate_percentage must be a number")
            sanitized["completion_rate_percentage"] = 0.0
    else:
        sanitized["completion_rate_percentage"] = 0.0
    
    # Arrays
    array_fields = ["top_keywords", "key_pain_points", "common_workflows", 
                    "technology_trends", "main_bottlenecks", "security_concerns", 
                    "deployment_preferences"]
    
    for field in array_fields:
        if field in data:
            if isinstance(data[field], list):
                # Ensure all items are strings
                sanitized[field] = [str(item) for item in data[field] if item]
                
                # Enforce min/max constraints
                if field == "top_keywords" and len(sanitized[field]) < 3:
                    errors.append(f"{field} should have at least 3 items")
                if field == "key_pain_points" and len(sanitized[field]) < 2:
                    errors.append(f"{field} should have at least 2 items")
            else:
                errors.append(f"{field} must be an array")
                sanitized[field] = []
        else:
            sanitized[field] = []
    
    # Strings
    string_fields = ["budget_insights", "key_insights", "recommendations"]
    for field in string_fields:
        if field in data:
            if isinstance(data[field], str):
                sanitized[field] = data[field].strip()
                
                # Enforce length constraints for insights/recommendations
                if field in ["key_insights", "recommendations"]:
                    if len(sanitized[field]) < 50:
                        errors.append(f"{field} should be at least 50 characters")
                    elif len(sanitized[field]) > 500:
                        errors.append(f"{field} should be at most 500 characters")
            else:
                errors.append(f"{field} must be a string")
                sanitized[field] = ""
        else:
            sanitized[field] = ""
    
    is_valid = len(errors) == 0
    return is_valid, errors, sanitized


def create_default_summary(total_participants=0, completed=0):
    """
    Create a default summary when AI fails or returns invalid data
    
    Args:
        total_participants: Number of total participants
        completed: Number of completed surveys
        
    Returns:
        dict: Default summary structure
    """
    completion_rate = (completed / total_participants * 100) if total_participants > 0 else 0
    
    return {
        "total_participants": total_participants,
        "completed_surveys": completed,
        "in_progress_surveys": total_participants - completed,
        "completion_rate_percentage": round(completion_rate, 2),
        "positive_indicators": 0,
        "negative_indicators": 0,
        "top_keywords": ["No data available"],
        "key_pain_points": ["Insufficient data for analysis"],
        "common_workflows": [],
        "technology_trends": [],
        "main_bottlenecks": [],
        "budget_insights": "Insufficient data to provide budget insights.",
        "security_concerns": [],
        "deployment_preferences": [],
        "key_insights": "Not enough survey responses to generate meaningful insights. Please wait for more participants to complete the survey.",
        "recommendations": "Collect more survey responses before analyzing trends and making recommendations. Aim for at least 5-10 completed surveys."
    }

