from flask import Blueprint, request
from database import get_db
from utils import handle_errors, success_response, error_response, validate_uuid

companies_bp = Blueprint('companies', __name__, url_prefix='/api/companies')


@companies_bp.route('', methods=['POST', 'OPTIONS'])
@handle_errors
def create_company():
    """Create a new company with UUID provided by frontend"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['uuid', 'name']
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing required field: {field}", 'validation_error', 400)
    
    # Validate UUID format
    if not validate_uuid(data['uuid']):
        return error_response('Invalid UUID format', 'validation_error', 400)
    
    db = get_db()
    
    # Check if UUID already exists
    existing = db.table('companies').select('uuid').eq('uuid', data['uuid']).execute()
    if existing.data:
        return error_response('Company with this UUID already exists', 'duplicate_error', 409)
    
    # Insert company
    result = db.table('companies').insert({
        'uuid': data['uuid'],
        'name': data['name'],
        'sector': data.get('sector'),
        'products': data.get('products'),
        'details': data.get('details')
    }).execute()
    
    if not result.data:
        return error_response('Failed to create company', 'database_error', 500)
    
    company = result.data[0]
    
    return success_response(
        data=company,
        message='Company created successfully',
        status=201
    )


@companies_bp.route('/<uuid:company_uuid>', methods=['GET', 'OPTIONS'])
@handle_errors
def get_company(company_uuid):
    """Get company details by UUID"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    result = db.table('companies').select('*').eq('uuid', str(company_uuid)).execute()
    
    if not result.data:
        return error_response('Company not found', 'not_found', 404)
    
    return success_response(data=result.data[0])


@companies_bp.route('/<uuid:company_uuid>', methods=['PUT', 'OPTIONS'])
@handle_errors
def update_company(company_uuid):
    """Update company details"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    
    # Build update object with only provided fields
    update_data = {}
    allowed_fields = ['name', 'sector', 'products', 'details']
    
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    if not update_data:
        return error_response('No valid fields to update', 'validation_error', 400)
    
    db = get_db()
    
    # Check if company exists
    existing = db.table('companies').select('uuid').eq('uuid', str(company_uuid)).execute()
    if not existing.data:
        return error_response('Company not found', 'not_found', 404)
    
    # Update company
    result = db.table('companies').update(update_data).eq('uuid', str(company_uuid)).execute()
    
    if not result.data:
        return error_response('Failed to update company', 'database_error', 500)
    
    return success_response(
        data=result.data[0],
        message='Company updated successfully'
    )


@companies_bp.route('/<uuid:company_uuid>', methods=['DELETE', 'OPTIONS'])
@handle_errors
def delete_company(company_uuid):
    """Delete a company (and cascade delete surveys, customers, messages)"""
    if request.method == 'OPTIONS':
        return '', 204
    
    db = get_db()
    
    # Check if company exists
    existing = db.table('companies').select('uuid').eq('uuid', str(company_uuid)).execute()
    if not existing.data:
        return error_response('Company not found', 'not_found', 404)
    
    # Delete company (cascade will handle related records)
    db.table('companies').delete().eq('uuid', str(company_uuid)).execute()
    
    return success_response(
        data={'uuid': str(company_uuid)},
        message='Company deleted successfully'
    )


@companies_bp.route('', methods=['GET', 'OPTIONS'])
@handle_errors
def list_companies():
    """List all companies with pagination"""
    if request.method == 'OPTIONS':
        return '', 204
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # Limit max results
    limit = min(limit, 100)
    
    db = get_db()
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get companies
    result = db.table('companies').select('*').range(offset, offset + limit - 1).execute()
    
    return success_response(
        data={
            'companies': result.data,
            'page': page,
            'limit': limit,
            'count': len(result.data)
        }
    )

