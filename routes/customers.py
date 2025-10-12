from flask import Blueprint, request
from database import get_db
from utils import handle_errors, success_response, error_response, call_ai_microservice, call_ai_start_session, call_ai_chat, validate_uuid

customers_bp = Blueprint('customers', __name__, url_prefix='/api/surveys')


@customers_bp.route('/<uuid:survey_uuid>/customers', methods=['POST', 'OPTIONS'])
@handle_errors
def register_customer(survey_uuid):
    """Register a new customer for a survey with UUID provided by frontend"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['uuid', 'name', 'age', 'gender']
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing required field: {field}", 'validation_error', 400)
    
    # Validate UUID format
    if not validate_uuid(data['uuid']):
        return error_response('Invalid customer UUID format', 'validation_error', 400)
    
    # Validate age
    try:
        age = int(data['age'])
        if age < 1 or age > 150:
            return error_response('Age must be between 1 and 150', 'validation_error', 400)
    except (ValueError, TypeError):
        return error_response('Age must be a valid number', 'validation_error', 400)
    
    db = get_db()
    
    # Check if survey exists
    survey = db.table('surveys').select('*').eq('uuid', str(survey_uuid)).execute()
    if not survey.data:
        return error_response('Survey not found', 'not_found', 404)
    
    survey_data = survey.data[0]
    
    # Check if survey is active
    if survey_data.get('status') != 'active':
        return error_response('Survey is not active', 'validation_error', 400)
    
    # Check if customer UUID already exists
    existing = db.table('customers').select('uuid').eq('uuid', data['uuid']).execute()
    if existing.data:
        return error_response('Customer with this UUID already exists', 'duplicate_error', 409)
    
    # Get company details for context
    company = db.table('companies').select('name, sector, products, details').eq('uuid', survey_data['company_uuid']).execute()
    company_data = company.data[0] if company.data else {}
    
    # Build context string for AI microservice
    context_parts = []
    if company_data:
        context_parts.append(f"Company: {company_data.get('name', 'Unknown')}")
        if company_data.get('sector'):
            context_parts.append(f"Sector: {company_data.get('sector')}")
        if company_data.get('products'):
            context_parts.append(f"Products: {company_data.get('products')}")
        if company_data.get('details'):
            context_parts.append(f"Details: {company_data.get('details')}")
    
    context_parts.append(f"Customer: {data['name']}")
    context_parts.append(f"Age: {age}")
    context_parts.append(f"Gender: {data['gender']}")
    context_parts.append(f"Survey: {survey_data.get('title')}")
    if survey_data.get('description'):
        context_parts.append(f"Survey Description: {survey_data.get('description')}")
    
    context_string = " | ".join(context_parts)
    
    # Call AI microservice to start session
    try:
        ai_session = call_ai_start_session(context_string)
        session_id = ai_session.get('session_id')
    except Exception as e:
        return error_response(f'Failed to start AI session: {str(e)}', 'ai_service_error', 503)
    
    # Insert customer with session_id
    result = db.table('customers').insert({
        'uuid': data['uuid'],
        'survey_uuid': str(survey_uuid),
        'name': data['name'],
        'age': age,
        'gender': data['gender'],
        'session_id': session_id,
        'metadata': [],
        'survey_status': 'in_progress'
    }).execute()
    
    if not result.data:
        return error_response('Failed to register customer', 'database_error', 500)
    
    customer = result.data[0]
    
    response_data = {
        'customer': customer,
        'survey': {
            'uuid': survey_data['uuid'],
            'title': survey_data['title'],
            'description': survey_data['description']
        },
        'ai_session': {
            'session_id': session_id,
            'initial_response': ai_session.get('response'),
            'status': ai_session.get('status')
        }
    }
    
    if company_data:
        response_data['company'] = company_data
    
    return success_response(
        data=response_data,
        message='Customer registered successfully. Chat can now begin.',
        status=201
    )


@customers_bp.route('/<uuid:survey_uuid>/customers/<uuid:customer_uuid>', methods=['GET', 'OPTIONS'])
@handle_errors
def get_customer(survey_uuid, customer_uuid):
    """Get customer details"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    result = db.table('customers').select('*').eq('uuid', str(customer_uuid)).eq('survey_uuid', str(survey_uuid)).execute()
    
    if not result.data:
        return error_response('Customer not found', 'not_found', 404)
    
    return success_response(data=result.data[0])


@customers_bp.route('/<uuid:survey_uuid>/customers/<uuid:customer_uuid>/chat', methods=['POST', 'OPTIONS'])
@handle_errors
def send_chat_message(survey_uuid, customer_uuid):
    """
    Send a chat message from customer and get AI response
    This is the main chat endpoint that communicates with AI microservice
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    
    # Validate required fields
    if 'message' not in data:
        return error_response('Missing required field: message', 'validation_error', 400)
    
    user_message = data['message'].strip()
    if not user_message:
        return error_response('Message cannot be empty', 'validation_error', 400)
    
    db = get_db()
    
    # Verify customer exists and belongs to survey
    customer = db.table('customers').select('*').eq('uuid', str(customer_uuid)).eq('survey_uuid', str(survey_uuid)).execute()
    if not customer.data:
        return error_response('Customer not found for this survey', 'not_found', 404)
    
    customer_data = customer.data[0]
    session_id = customer_data.get('session_id')
    
    if not session_id:
        return error_response('No AI session found for this customer', 'validation_error', 400)
    
    # Store user message in database
    user_msg_result = db.table('chat_messages').insert({
        'customer_uuid': str(customer_uuid),
        'survey_uuid': str(survey_uuid),
        'message': user_message,
        'sender': 'user'
    }).execute()
    
    # Call AI microservice chat endpoint with session_id
    try:
        ai_result = call_ai_chat(session_id, user_message)
        ai_response = ai_result.get('response', '')
        status = ai_result.get('status', 0)
        comments = ai_result.get('comments')
    except Exception as e:
        return error_response(f'Failed to get AI response: {str(e)}', 'ai_service_error', 503)
    
    # Store AI response in database
    ai_msg_result = db.table('chat_messages').insert({
        'customer_uuid': str(customer_uuid),
        'survey_uuid': str(survey_uuid),
        'message': ai_response,
        'sender': 'ai'
    }).execute()
    
    # Handle metadata saving based on status
    schema_completed = False
    survey_completed = False
    
    if status == 1 and comments:
        # Block completed - save to metadata
        try:
            # Get current metadata
            current_metadata = customer_data.get('metadata', [])
            if current_metadata is None:
                current_metadata = []
            
            # Parse comments if it's a string
            import json
            if isinstance(comments, str):
                try:
                    comments = json.loads(comments)
                except json.JSONDecodeError:
                    pass
            
            # Validate structure: should have block_id and data
            if isinstance(comments, dict) and 'block_id' in comments and 'data' in comments:
                block_entry = {
                    'block_id': comments['block_id'],
                    'data': comments['data'],
                    'completed_at': None  # Will be set by DB timestamp
                }
                
                # Append the new schema data
                current_metadata.append(block_entry)
                
                # Update customer metadata in database
                db.table('customers').update({
                    'metadata': current_metadata
                }).eq('uuid', str(customer_uuid)).execute()
                
                schema_completed = True
            else:
                print(f"Invalid comments structure: missing block_id or data fields")
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error updating metadata: {str(e)}")
    
    elif status == -1 and comments == "Survey completed":
        # Survey completed - all 6 blocks have been saved already
        survey_completed = True
        # Optionally update a completion flag in the customer record
        try:
            db.table('customers').update({
                'survey_status': 'completed'
            }).eq('uuid', str(customer_uuid)).execute()
        except Exception as e:
            print(f"Error updating survey completion status: {str(e)}")
    
    response_data = {
        'user_message': user_msg_result.data[0] if user_msg_result.data else None,
        'ai_response': ai_msg_result.data[0] if ai_msg_result.data else None,
        'status': status,
        'schema_completed': schema_completed,
        'survey_completed': survey_completed,
        'session_id': session_id
    }
    
    if comments:
        response_data['comments'] = comments
    
    return success_response(data=response_data)


@customers_bp.route('/<uuid:survey_uuid>/customers/<uuid:customer_uuid>/history', methods=['GET', 'OPTIONS'])
@handle_errors
def get_chat_history(survey_uuid, customer_uuid):
    """Get complete chat history for a customer"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Verify customer exists
    customer = db.table('customers').select('*').eq('uuid', str(customer_uuid)).eq('survey_uuid', str(survey_uuid)).execute()
    if not customer.data:
        return error_response('Customer not found for this survey', 'not_found', 404)
    
    # Get all messages
    messages = db.table('chat_messages').select('*').eq('customer_uuid', str(customer_uuid)).order('created_at', desc=False).execute()
    
    return success_response(
        data={
            'customer_uuid': str(customer_uuid),
            'survey_uuid': str(survey_uuid),
            'messages': messages.data,
            'total_messages': len(messages.data)
        }
    )


@customers_bp.route('/<uuid:survey_uuid>/customers', methods=['GET', 'OPTIONS'])
@handle_errors
def list_survey_customers(survey_uuid):
    """List all customers for a survey"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Check if survey exists
    survey = db.table('surveys').select('uuid').eq('uuid', str(survey_uuid)).execute()
    if not survey.data:
        return error_response('Survey not found', 'not_found', 404)
    
    # Get all customers
    customers = db.table('customers').select('*').eq('survey_uuid', str(survey_uuid)).order('created_at', desc=True).execute()
    
    return success_response(
        data={
            'survey_uuid': str(survey_uuid),
            'customers': customers.data,
            'count': len(customers.data)
        }
    )


@customers_bp.route('/<uuid:survey_uuid>/customers/<uuid:customer_uuid>/metadata', methods=['GET', 'OPTIONS'])
@handle_errors
def get_customer_metadata(survey_uuid, customer_uuid):
    """Get customer's completed schema metadata"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Verify customer exists
    customer = db.table('customers').select('metadata, session_id, name').eq('uuid', str(customer_uuid)).eq('survey_uuid', str(survey_uuid)).execute()
    if not customer.data:
        return error_response('Customer not found for this survey', 'not_found', 404)
    
    customer_data = customer.data[0]
    metadata = customer_data.get('metadata', [])
    
    return success_response(
        data={
            'customer_uuid': str(customer_uuid),
            'customer_name': customer_data.get('name'),
            'session_id': customer_data.get('session_id'),
            'completed_schemas': metadata,
            'total_completed': len(metadata) if metadata else 0
        }
    )


@customers_bp.route('/<uuid:survey_uuid>/customers/<uuid:customer_uuid>', methods=['DELETE', 'OPTIONS'])
@handle_errors
def delete_customer(survey_uuid, customer_uuid):
    """Delete a customer and their chat history"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Check if customer exists
    customer = db.table('customers').select('uuid').eq('uuid', str(customer_uuid)).eq('survey_uuid', str(survey_uuid)).execute()
    if not customer.data:
        return error_response('Customer not found', 'not_found', 404)
    
    # Delete customer (cascade will handle messages)
    db.table('customers').delete().eq('uuid', str(customer_uuid)).execute()
    
    return success_response(
        data={'uuid': str(customer_uuid)},
        message='Customer and chat history deleted successfully'
    )

