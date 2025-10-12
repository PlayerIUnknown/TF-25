from functools import wraps
from flask import jsonify, request
import requests
from datetime import datetime


def handle_errors(f):
    """Decorator to handle errors and return consistent JSON responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'validation_error'
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'server_error'
            }), 500
    return decorated_function


def validate_uuid(uuid_str):
    """Validate UUID format"""
    import uuid
    try:
        uuid.UUID(str(uuid_str))
        return True
    except (ValueError, AttributeError):
        return False


def serialize_datetime(obj):
    """Serialize datetime objects to ISO format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def call_ai_start_session(context):
    """
    Call the AI microservice to start a new session
    
    Args:
        context: String containing company and customer context
    
    Returns:
        dict with session_id, response, status, and comments
    """
    from config import Config
    
    # Extract base URL from AI_MICROSERVICE_URL
    base_url = Config.AI_MICROSERVICE_URL.replace('/api/chat', '')
    start_session_url = f"{base_url}/api/start_session"
    
    payload = {
        'context': context
    }
    
    try:
        response = requests.post(
            start_session_url,
            json=payload,
            timeout=30,
            verify=Config.VERIFY_SSL
        )
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"AI microservice start_session error: {str(e)}")


def call_ai_chat(session_id, user_input):
    """
    Call the AI microservice chat endpoint
    
    Args:
        session_id: Session ID from start_session
        user_input: User's message
    
    Returns:
        dict with response, status, comments, and session_id
    """
    from config import Config
    
    payload = {
        'session_id': session_id,
        'user_input': user_input
    }
    
    try:
        response = requests.post(
            Config.AI_MICROSERVICE_URL,
            json=payload,
            timeout=30,
            verify=Config.VERIFY_SSL
        )
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"AI microservice chat error: {str(e)}")


def call_ai_microservice(messages, survey_context=None):
    """
    Call the AI microservice with chat messages (Legacy method - kept for compatibility)
    
    Args:
        messages: List of message objects with 'role' and 'content'
        survey_context: Optional survey context information
    
    Returns:
        AI response text
    """
    from config import Config
    
    payload = {
        'messages': messages,
        'context': survey_context or {}
    }
    
    try:
        response = requests.post(
            Config.AI_MICROSERVICE_URL,
            json=payload,
            timeout=30,
            verify=Config.VERIFY_SSL  # Use SSL verification from config
        )
        response.raise_for_status()
        data = response.json()
        return data.get('response', '')
    except requests.exceptions.RequestException as e:
        raise Exception(f"AI microservice error: {str(e)}")


def success_response(data, message=None, status=200):
    """Create a success response"""
    response = {
        'success': True,
        'data': data
    }
    if message:
        response['message'] = message
    return jsonify(response), status


def error_response(error, error_type='error', status=400):
    """Create an error response"""
    return jsonify({
        'success': False,
        'error': error,
        'error_type': error_type
    }), status

