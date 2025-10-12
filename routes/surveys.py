from flask import Blueprint, request
from database import get_db
from utils import handle_errors, success_response, error_response, validate_uuid
import json
from groq import Groq
from config import Config
from ai_summary_schema import (
    get_schema_template,
    validate_summary_response,
    create_default_summary
)

surveys_bp = Blueprint('surveys', __name__, url_prefix='/api')


@surveys_bp.route('/companies/<uuid:company_uuid>/surveys', methods=['POST', 'OPTIONS'])
@handle_errors
def create_survey(company_uuid):
    """Create a new survey under a company with UUID provided by frontend"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['uuid', 'title']
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing required field: {field}", 'validation_error', 400)
    
    # Validate UUID format
    if not validate_uuid(data['uuid']):
        return error_response('Invalid survey UUID format', 'validation_error', 400)
    
    db = get_db()
    
    # Check if company exists
    company = db.table('companies').select('uuid').eq('uuid', str(company_uuid)).execute()
    if not company.data:
        return error_response('Company not found', 'not_found', 404)
    
    # Check if survey UUID already exists
    existing = db.table('surveys').select('uuid').eq('uuid', data['uuid']).execute()
    if existing.data:
        return error_response('Survey with this UUID already exists', 'duplicate_error', 409)
    
    # Insert survey
    result = db.table('surveys').insert({
        'uuid': data['uuid'],
        'company_uuid': str(company_uuid),
        'title': data['title'],
        'description': data.get('description'),
        'status': data.get('status', 'active')
    }).execute()
    
    if not result.data:
        return error_response('Failed to create survey', 'database_error', 500)
    
    survey = result.data[0]
    
    return success_response(
        data=survey,
        message='Survey created successfully',
        status=201
    )


@surveys_bp.route('/companies/<uuid:company_uuid>/surveys', methods=['GET', 'OPTIONS'])
@handle_errors
def list_company_surveys(company_uuid):
    """List all surveys for a company"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Check if company exists
    company = db.table('companies').select('uuid').eq('uuid', str(company_uuid)).execute()
    if not company.data:
        return error_response('Company not found', 'not_found', 404)
    
    # Get surveys
    result = db.table('surveys').select('*').eq('company_uuid', str(company_uuid)).order('created_at', desc=True).execute()
    
    return success_response(
        data={
            'company_uuid': str(company_uuid),
            'surveys': result.data,
            'count': len(result.data)
        }
    )


@surveys_bp.route('/surveys/<uuid:survey_uuid>', methods=['GET', 'OPTIONS'])
@handle_errors
def get_survey(survey_uuid):
    """Get survey details by UUID"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    result = db.table('surveys').select('*').eq('uuid', str(survey_uuid)).execute()
    
    if not result.data:
        return error_response('Survey not found', 'not_found', 404)
    
    survey = result.data[0]
    
    # Get company details
    company = db.table('companies').select('name, sector').eq('uuid', survey['company_uuid']).execute()
    
    if company.data:
        survey['company'] = company.data[0]
    
    return success_response(data=survey)


@surveys_bp.route('/surveys/<uuid:survey_uuid>', methods=['PUT', 'OPTIONS'])
@handle_errors
def update_survey(survey_uuid):
    """Update survey details"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    
    # Build update object with only provided fields
    update_data = {}
    allowed_fields = ['title', 'description', 'status']
    
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    if not update_data:
        return error_response('No valid fields to update', 'validation_error', 400)
    
    db = get_db()
    
    # Check if survey exists
    existing = db.table('surveys').select('uuid').eq('uuid', str(survey_uuid)).execute()
    if not existing.data:
        return error_response('Survey not found', 'not_found', 404)
    
    # Update survey
    result = db.table('surveys').update(update_data).eq('uuid', str(survey_uuid)).execute()
    
    if not result.data:
        return error_response('Failed to update survey', 'database_error', 500)
    
    return success_response(
        data=result.data[0],
        message='Survey updated successfully'
    )


@surveys_bp.route('/surveys/<uuid:survey_uuid>', methods=['DELETE', 'OPTIONS'])
@handle_errors
def delete_survey(survey_uuid):
    """Delete a survey (and cascade delete customers and messages)"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Check if survey exists
    existing = db.table('surveys').select('uuid').eq('uuid', str(survey_uuid)).execute()
    if not existing.data:
        return error_response('Survey not found', 'not_found', 404)
    
    # Delete survey
    db.table('surveys').delete().eq('uuid', str(survey_uuid)).execute()
    
    return success_response(
        data={'uuid': str(survey_uuid)},
        message='Survey deleted successfully'
    )


@surveys_bp.route('/surveys/<uuid:survey_uuid>/stats', methods=['GET', 'OPTIONS'])
@handle_errors
def get_survey_stats(survey_uuid):
    """Get statistics for a survey"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Check if survey exists
    survey = db.table('surveys').select('*').eq('uuid', str(survey_uuid)).execute()
    if not survey.data:
        return error_response('Survey not found', 'not_found', 404)
    
    # Get customer count
    customers = db.table('customers').select('uuid', count='exact').eq('survey_uuid', str(survey_uuid)).execute()
    
    # Get message count
    messages = db.table('chat_messages').select('uuid', count='exact').eq('survey_uuid', str(survey_uuid)).execute()
    
    stats = {
        'survey_uuid': str(survey_uuid),
        'total_customers': customers.count if hasattr(customers, 'count') else len(customers.data),
        'total_messages': messages.count if hasattr(messages, 'count') else len(messages.data),
        'status': survey.data[0]['status']
    }
    
    return success_response(data=stats)


@surveys_bp.route('/surveys/<uuid:survey_uuid>/ai-summary', methods=['GET', 'OPTIONS'])
@handle_errors
def get_survey_ai_summary(survey_uuid):
    """
    Get AI-generated summary of all customer responses for a survey.
    Analyzes all customer metadata and generates insights.
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Check if survey exists
    survey = db.table('surveys').select('*').eq('uuid', str(survey_uuid)).execute()
    if not survey.data:
        return error_response('Survey not found', 'not_found', 404)
    
    survey_data = survey.data[0]
    
    # Get all customers with their metadata for this survey
    customers = db.table('customers').select('uuid, name, age, gender, metadata, survey_status').eq('survey_uuid', str(survey_uuid)).execute()
    
    if not customers.data or len(customers.data) == 0:
        return error_response('No customer data found for this survey', 'not_found', 404)
    
    # Get company info for context
    company = db.table('companies').select('name, sector, products, details').eq('uuid', survey_data['company_uuid']).execute()
    company_data = company.data[0] if company.data else {}
    
    # Prepare data for AI analysis
    total_customers = len(customers.data)
    completed_customers = [c for c in customers.data if c.get('survey_status') == 'completed']
    in_progress_customers = [c for c in customers.data if c.get('survey_status') == 'in_progress']
    
    # Extract all metadata
    all_metadata = []
    for customer in customers.data:
        metadata = customer.get('metadata', [])
        if metadata:
            all_metadata.append({
                'customer_name': customer.get('name'),
                'age': customer.get('age'),
                'gender': customer.get('gender'),
                'status': customer.get('survey_status'),
                'responses': metadata
            })
    
    # Get the schema template
    schema_template = get_schema_template()
    
    # Build prompt for Groq AI with strict schema
    analysis_prompt = f"""You are an expert market research analyst. Analyze the following survey data and provide a comprehensive summary.

**Survey Context:**
- Survey Title: {survey_data.get('title', 'N/A')}
- Company: {company_data.get('name', 'N/A')}
- Sector: {company_data.get('sector', 'N/A')}
- Products: {company_data.get('products', 'N/A')}

**Survey Data:**
Total Participants: {total_customers}
Completed Surveys: {len(completed_customers)}
In Progress: {len(in_progress_customers)}

**All Customer Responses:**
{json.dumps(all_metadata, indent=2)}

**CRITICAL: You MUST return a JSON object with this EXACT structure (no additions, no omissions):**
{json.dumps(schema_template, indent=2)}

**Field Requirements:**
- total_participants, completed_surveys, in_progress_surveys: integers (exact counts from data)
- completion_rate_percentage: number 0-100 (percentage with decimals)
- positive_indicators, negative_indicators: integers (count sentiment in responses)
- top_keywords: array of 5-10 strings (most frequent themes)
- key_pain_points: array of 3-5 strings (main challenges identified)
- common_workflows, technology_trends, main_bottlenecks, security_concerns, deployment_preferences: arrays of strings
- budget_insights: string (brief summary)
- key_insights: string 50-500 chars (2-3 sentences on findings)
- recommendations: string 50-500 chars (2-3 sentences actionable advice)

**IMPORTANT:** 
1. Return ONLY valid JSON matching the structure above
2. No markdown, no code fences, no extra text
3. All fields must be present
4. Use exact field names
5. Respect data types (numbers, strings, arrays)"""

    # Call Groq API for analysis
    try:
        groq_client = Groq(api_key=Config.GROQ_API_KEY)
        
        response = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert market research analyst. You MUST respond with valid JSON only that exactly matches the provided schema. No markdown formatting, no code blocks, just pure JSON."
                },
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.2,  # Lower temperature for more consistent structured output
            max_tokens=2000,
            response_format={"type": "json_object"}  # Force JSON mode
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse the AI response
        try:
            summary = json.loads(ai_response)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"AI response: {ai_response}")
            # Return default summary if parsing fails
            summary = create_default_summary(total_customers, len(completed_customers))
            
            return success_response(
                data={
                    'survey_uuid': str(survey_uuid),
                    'survey_title': survey_data.get('title'),
                    'company': company_data.get('name'),
                    'analysis_date': None,
                    'summary': summary,
                    'validation_error': 'AI response was not valid JSON',
                    'ai_raw_response': ai_response[:500]  # First 500 chars for debugging
                }
            )
        
        # Validate the response against schema
        is_valid, errors, sanitized_summary = validate_summary_response(summary)
        
        if not is_valid:
            print(f"Schema validation errors: {errors}")
            # Use sanitized version with default values filled in
            summary = sanitized_summary
        
        return success_response(
            data={
                'survey_uuid': str(survey_uuid),
                'survey_title': survey_data.get('title'),
                'company': company_data.get('name'),
                'analysis_date': None,
                'summary': summary,
                'schema_validated': is_valid,
                'validation_errors': errors if not is_valid else None
            }
        )
        
    except Exception as e:
        print(f"AI service error: {str(e)}")
        # Return default summary on error
        default_summary = create_default_summary(total_customers, len(completed_customers))
        
        return success_response(
            data={
                'survey_uuid': str(survey_uuid),
                'survey_title': survey_data.get('title'),
                'company': company_data.get('name'),
                'analysis_date': None,
                'summary': default_summary,
                'error': f'AI service error: {str(e)}',
                'fallback': True
            }
        )

