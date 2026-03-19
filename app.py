from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from extensions import db, bcrypt, jwt, mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Namespaces
from routes.auth import api as auth_ns
from routes.password_reset import api as password_ns
from routes.request_routes import api as requests_ns
from routes.department_routes import api as department_ns
from routes.designation_routes import api as designation_ns
from routes.employee_routes import api as employee_ns
from routes.client_routes import api as clients_ns
from routes.title_routes import api as titles_ns
from routes.industry_routes import api as industry_ns
from routes.location_routes import api as location_ns
from routes.kiosk_routes import api as kiosk_ns
from routes.game_routes import api as game_ns
from routes.game_mapping_routes import api as game_mapping_ns
from routes.project_routes import api as project_ns
from routes.metric_routes import api as metric_ns
from routes.game_questions_routes import api as game_questions_ns
from routes.registration_routes import registration_ns
from routes.login_routes import login_ns
from routes.gamemove_routes import gamemoves_ns
from routes.survey_question_routes import surveys_ns
from routes.response_routes import responses_ns
from routes.ai_analytics_routes import api as ai_analytics_ns
from routes.client_report_routes import api as client_report_ns
from routes.user_routes import api as user_ns
from routes.game_center_routes import api as game_center_ns
from routes.game_apk_routes import api as game_apk_ns
from models.game_apk import GameAPK, APKInstallation


from flask_cors import CORS


app = Flask(__name__)

# -------------------------------
# CORS Configuration
# -------------------------------
CORS(app, resources={r"/*": {"origins": ["*"]}}, supports_credentials=True)
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Malli$12@localhost/erevna"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Kishore%4015@localhost/erevna?charset=utf8mb4&collation=utf8mb4_unicode_ci"
# Neon PostgreSQL configuration - use environment variable or fallback
neon_url = os.getenv('NEON_DATABASE_URL')
if neon_url and neon_url != "postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/erevna?sslmode=require":
    app.config["SQLALCHEMY_DATABASE_URI"] = neon_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 30
    }
    print(f"🐘 Connected to Neon PostgreSQL")
else:
    # Fallback for development - use local SQLite for stability
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///erevna_local.db"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 30
    }
    print(f"🗄️ Using local SQLite database")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# -------------------------------
# JWT Configuration
# -------------------------------
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecret")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_ALGORITHM"] = "HS256"

# -------------------------------
# Email / SMTP Configuration
# -------------------------------
# Using Resend API instead of SMTP (cloud-friendly)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Remove fallback for security
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Remove fallback for security
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', '21bq1a0569@gmail.com')
app.config['MAIL_DEBUG'] = os.getenv('MAIL_DEBUG', 'true').lower() == 'true'
app.config['MAIL_SUPPRESS_SEND'] = False  # ChatGPT recommended

# Initialize Flask-Mail with app
mail.init_app(app)
print(f"🔧 Flask-Mail initialized with app")

# Check if Resend API key is available
resend_api_key = os.getenv('RESEND_API_KEY')
if resend_api_key:
    print(f"📧 Using Resend API for email delivery")
    print(f"🔧 Resend API Key Set: {'Yes' if resend_api_key else 'No'}")
else:
    print(f"📧 Using Gmail SMTP for email delivery")
    print(f"🔧 Gmail Config - Server: {app.config['MAIL_SERVER']}")
    print(f"🔧 Gmail Config - Username: {app.config['MAIL_USERNAME']}")
    print(f"🔧 Gmail Config - Password Set: {'Yes' if app.config['MAIL_PASSWORD'] else 'No'}")
    print(f"🔧 Gmail Config - Port: {app.config['MAIL_PORT']}")
    print(f"🔧 Gmail Config - TLS: {app.config['MAIL_USE_TLS']}")
    print(f"🔧 Gmail Config - SSL: {app.config['MAIL_USE_SSL']}")
    print(f"🔧 Gmail Config - Debug: {app.config['MAIL_DEBUG']}")
    print(f"🔧 Gmail Config - Suppress Send: {app.config['MAIL_SUPPRESS_SEND']}")

# -------------------------------
# Static Files for Unity WebGL Games
# -------------------------------
import os
from flask import send_from_directory, Response
import urllib.parse

# Create public/games directory if it doesn't exist
GAMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'games')
if not os.path.exists(GAMES_DIR):
    os.makedirs(GAMES_DIR, exist_ok=True)
    print(f"📁 Created games directory: {GAMES_DIR}")

# Debug: Print current files
print(f"🔍 Unity files in snakes-ladder Build folder:")
if os.path.exists(os.path.join(GAMES_DIR, 'snakes-ladder', 'Build')):
    for f in os.listdir(os.path.join(GAMES_DIR, 'snakes-ladder', 'Build')):
        print(f"   📄 {f}")
else:
    print("❌ Build folder not found!")

print("🚀 Render deployment triggered - Unity files should be available")

# Debug endpoint to check game folders
@app.route('/debug-all')
def debug_all():
    import os
    
    base = os.path.join(GAMES_DIR)
    result = {}

    for game in os.listdir(base):
        game_path = os.path.join(base, game)
        if os.path.isdir(game_path):
            result[game] = os.listdir(game_path)

    return str(result)

# Serve Unity WebGL games with proper URL encoding and MIME types
@app.route('/games/<path:game_name>/<path:filename>')
def serve_game_files(game_name, filename):
    """Serve Unity WebGL game files with proper MIME types and compression handling"""
    # Remove query parameters from filename (like ?v=2)
    if '?' in filename:
        filename = filename.split('?')[0]
    
    # URL decode the filename to handle spaces and special characters properly
    filename = urllib.parse.unquote(filename)
    # Handle double encoding for special characters like &
    filename = urllib.parse.unquote(filename)
    game_path = os.path.join(GAMES_DIR, game_name)
    file_path = os.path.join(game_path, filename)
    
    print(f"🎮 Serving file: {filename} from {game_path}")
    print(f"🔍 Full path: {file_path}")
    
    # Check if file exists before trying to serve
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        # List available files for debugging
        if os.path.exists(game_path):
            print(f"📁 Available files in {game_path}:")
            for f in os.listdir(game_path):
                print(f"   - {f}")
        return f"File not found: {filename}", 404
    
    # Set proper MIME types for Unity files
    mimetype = 'application/octet-stream'
    if filename.endswith('.wasm'):
        mimetype = 'application/wasm'
    elif filename.endswith('.js'):
        mimetype = 'application/javascript'
    elif filename.endswith('.data'):
        mimetype = 'application/octet-stream'
    elif filename.endswith('.css'):
        mimetype = 'text/css'
    elif filename.endswith('.png'):
        mimetype = 'image/png'
    elif filename.endswith('.ico'):
        mimetype = 'image/x-icon'
    elif filename.endswith('.html'):
        mimetype = 'text/html'
    
    # Handle compressed files
    is_compressed = filename.endswith('.gz') or filename.endswith('.gzip')
    actual_filename = filename
    
    # For compressed files, determine the original filename and MIME type
    if is_compressed:
        if filename.endswith('.js.gz') or filename.endswith('.js.gzip'):
            actual_filename = filename.replace('.gz', '').replace('.gzip', '')
            mimetype = 'application/javascript'
        elif filename.endswith('.wasm.gz') or filename.endswith('.wasm.gzip'):
            actual_filename = filename.replace('.gz', '').replace('.gzip', '')
            mimetype = 'application/wasm'
        elif filename.endswith('.data.gz') or filename.endswith('.data.gzip'):
            actual_filename = filename.replace('.gz', '').replace('.gzip', '')
            mimetype = 'application/octet-stream'
    
    print(f"📄 Serving file: {actual_filename} with MIME: {mimetype}")
    
    try:
        # If the file is compressed but the request is for uncompressed version
        if not filename.endswith('.gz') and not filename.endswith('.gzip'):
            # Check if compressed version exists
            compressed_path = file_path + '.gz'
            if os.path.exists(compressed_path):
                print(f"🗜️ Found compressed version: {compressed_path}")
                # Serve the compressed file with proper headers
                response = send_from_directory(game_path, filename + '.gz', mimetype=mimetype)
                response.headers['Content-Encoding'] = 'gzip'
                print(f"🗜️ Serving compressed file: {filename}.gz with Content-Encoding: gzip")
            else:
                # Serve uncompressed file
                response = send_from_directory(game_path, filename, mimetype=mimetype)
                print(f"📄 Serving uncompressed file: {filename}")
        else:
            # Serve the file as requested
            response = send_from_directory(game_path, filename, mimetype=mimetype)
        
        # Add special headers for Unity WebGL files
        if filename.endswith('.wasm') or actual_filename.endswith('.wasm'):
            response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
            response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        elif filename.endswith('.js') or actual_filename.endswith('.js'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        elif filename.endswith('.data') or actual_filename.endswith('.data'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # Add CORS headers for Unity WebGL
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        print(f"✅ Successfully served: {filename} with MIME: {mimetype}")
        return response
    except Exception as e:
        print(f"❌ Error serving file {filename}: {e}")
        return f"File not found: {filename}", 404

# Fix compression headers for Unity WebGL files
@app.after_request
def remove_encoding(response):
    """Remove compression headers to fix Unity WebGL corruption"""
    # Remove Content-Encoding header to prevent corruption
    response.headers.pop('Content-Encoding', None)
    response.headers.pop('Content-Length', None)
    return response

# Serve game index.html
@app.route('/games/<path:game_name>/')
def serve_game_index(game_name):
    """Serve Unity WebGL game index.html"""
    game_path = os.path.join(GAMES_DIR, game_name)
    try:
        response = send_from_directory(game_path, 'index.html', mimetype='text/html')
        # Add CORS headers for Unity WebGL
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    except Exception as e:
        print(f"Error serving index.html for {game_name}: {e}")
        return f"Game not found: {game_name}", 404

# Debug endpoint to check files
@app.route('/debug-files')
def debug_files():
    """Debug endpoint to list all Unity files"""
    try:
        build_path = os.path.join(GAMES_DIR, 'snakes-ladder', 'Build')
        if os.path.exists(build_path):
            files = os.listdir(build_path)
            return f"<h1>Unity Files in Build Folder:</h1><pre>{files}</pre>"
        else:
            return "<h1>❌ Build folder not found!</h1>"
    except Exception as e:
        return f"<h1>❌ Error: {e}</h1>"

# -------------------------------
# Initialize Extensions
# -------------------------------
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
mail.init_app(app)

# -------------------------------
# Swagger API Setup
# -------------------------------
api = Api(
    app,
    title="Erevna API Documentation",
    version="1.0",
    description="All API endpoints for Erevna Platform",
    doc="/swagger"
)

# -------------------------------
# Register Namespaces
# -------------------------------
api.add_namespace(auth_ns, path="/auth")
api.add_namespace(password_ns, path="/auth/password")
api.add_namespace(requests_ns, path="/requests")
api.add_namespace(department_ns, path="/departments")
api.add_namespace(designation_ns, path="/designations")
api.add_namespace(employee_ns, path="/employees")
api.add_namespace(clients_ns, path="/clients")
api.add_namespace(titles_ns, path="/titles")
api.add_namespace(industry_ns, path="/industries")
api.add_namespace(location_ns, path="/locations")
api.add_namespace(kiosk_ns, path="/kiosks")
api.add_namespace(game_ns, path="/games")
api.add_namespace(game_mapping_ns, path="/game_mapping")
api.add_namespace(project_ns, path="/projects")
api.add_namespace(metric_ns, path="/metrics")
api.add_namespace(game_questions_ns, path="/game-questions")
api.add_namespace(registration_ns, path="/registration")
api.add_namespace(login_ns, path="/login")
api.add_namespace(gamemoves_ns, path="/game-moves")
api.add_namespace(surveys_ns, path="/surveys")
api.add_namespace(responses_ns, path="/responses")
api.add_namespace(ai_analytics_ns, path="/ai-analytics")
api.add_namespace(client_report_ns, path="/client-report")
api.add_namespace(user_ns, path="/users")
api.add_namespace(game_center_ns, path="/game-center")
api.add_namespace(game_apk_ns, path="/game-apk")

# -------------------------------
# Create Tables if Not Exists
# -------------------------------
try:
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️ Database connection issue: {e}")
    print("📄 Swagger will still work without database")

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    # Production-ready configuration
    debug_mode = os.getenv('FLASK_ENV', 'development') != 'production'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 10000))  # Render uses PORT env var
    
    print(f"🚀 Starting server on {host}:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    app.run(debug=debug_mode, host=host, port=port)
