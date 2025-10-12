import ssl
import os
import warnings

# Disable SSL verification BEFORE any other imports
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context

# Disable SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Monkey patch requests to disable SSL verification
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Patch httpx (used by Supabase)
try:
    import httpx
    # Create a custom transport with SSL verification disabled
    original_init = httpx.Client.__init__
    def patched_init(self, *args, **kwargs):
        kwargs['verify'] = False
        original_init(self, *args, **kwargs)
    httpx.Client.__init__ = patched_init
    
    # Also patch AsyncClient
    original_async_init = httpx.AsyncClient.__init__
    def patched_async_init(self, *args, **kwargs):
        kwargs['verify'] = False
        original_async_init(self, *args, **kwargs)
    httpx.AsyncClient.__init__ = patched_async_init
except ImportError:
    pass

# Now import Flask and other modules
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import Database

# Import blueprints
from routes.companies import companies_bp
from routes.surveys import surveys_bp
from routes.customers import customers_bp


def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # Initialize database
    try:
        Database.init_app(app)
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Register blueprints
    app.register_blueprint(companies_bp)
    app.register_blueprint(surveys_bp)
    app.register_blueprint(customers_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'AI Survey Backend',
            'version': '1.0.0'
        })
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'AI-Enabled Survey Service API',
            'version': '1.0.0',
            'docs': '/api-docs (see API_DOCUMENTATION.md)',
            'endpoints': {
                'companies': '/api/companies',
                'surveys': '/api/surveys',
                'customers': '/api/surveys/<survey_uuid>/customers'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'error_type': 'not_found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'error_type': 'method_not_allowed'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_type': 'internal_error'
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    print(f"Starting Flask server on port {Config.FLASK_PORT}...")
    app.run(
        host='0.0.0.0',
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )

