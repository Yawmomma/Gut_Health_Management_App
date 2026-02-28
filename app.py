from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_socketio import SocketIO, emit
from flask_migrate import Migrate
from flasgger import Swagger
from config import Config
from database import db
from utils.swagger_config import swagger_template, swagger_config
import os
import sys
import signal
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize SocketIO with session support
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

# Initialize database
db.init_app(app)

# Initialize Flask-Migrate for database migrations
migrate_ext = Migrate(app, db)

# Initialize Swagger/OpenAPI documentation
swagger = Swagger(app, template=swagger_template, config=swagger_config)

# Context processor to make admin_mode available to all templates
@app.context_processor
def inject_admin_mode():
    """Make admin_mode available to all templates"""
    return dict(admin_mode=app.config.get('ADMIN_MODE', False))

# Custom Jinja filter to format numbers (remove trailing .0)
@app.template_filter('format_num')
def format_num(value):
    """Format number to remove trailing .0 for whole numbers"""
    if value is None:
        return None
    try:
        num = float(value)
        # If it's a whole number, display without decimal
        if num == int(num):
            return str(int(num))
        # Otherwise, remove trailing zeros but keep meaningful decimals
        return f'{num:g}'
    except (ValueError, TypeError):
        return value

# Custom Jinja filter to add ordinal suffix to numbers (1st, 2nd, 3rd, etc.)
@app.template_filter('ordinal')
def ordinal(value):
    """Add ordinal suffix to a number (1st, 2nd, 3rd, etc.)"""
    try:
        num = int(value)
        if 10 <= num % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
        return f"{num}{suffix}"
    except (ValueError, TypeError):
        return value

# Import models (after db is initialized)
from models import food, diary, user, education, recipe, chat, usda, ausnut, webhooks
from models import reintroduction, gamification, security

# Import routes
from routes import main, compendium, diary as diary_routes, recipes, education as education_routes, settings
from routes import recipe_builder, usda_foods, ausnut_foods
from routes import api_v1

# Register blueprints
app.register_blueprint(main.bp)
app.register_blueprint(compendium.bp)
app.register_blueprint(diary_routes.bp)
app.register_blueprint(recipes.bp)
app.register_blueprint(recipe_builder.bp)
app.register_blueprint(education_routes.bp)
app.register_blueprint(api_v1.bp)  # API v1 - Versioned API structure
app.register_blueprint(settings.bp)
app.register_blueprint(usda_foods.bp)
app.register_blueprint(ausnut_foods.bp)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    print("[OK] Database tables created successfully")

@app.route('/')
def index():
    """Redirect to dashboard"""
    return redirect(url_for('main.dashboard'))

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the Flask server"""
    def shutdown_server():
        time.sleep(0.5)  # Give time for response to be sent
        print("\n" + "="*60)
        print("SHUTTING DOWN SERVER...")
        print("="*60)
        os._exit(0)  # Force exit all threads

    # Start shutdown in background thread so response can be sent
    threading.Thread(target=shutdown_server, daemon=True).start()
    return jsonify({'status': 'shutting_down', 'message': 'Server is shutting down...'})

# File change handler for live reload
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.last_reload = 0
        self.debounce_seconds = 1  # Wait 1 second before reloading

    def on_modified(self, event):
        if event.is_directory:
            return

        # Only reload for Python and HTML files
        if event.src_path.endswith(('.py', '.html', '.css', '.js')):
            current_time = time.time()
            if current_time - self.last_reload > self.debounce_seconds:
                self.last_reload = current_time
                # Emit reload event to all connected clients
                self.socketio.emit('reload', {'data': 'reload'})
                print(f"[Live Reload] File changed: {event.src_path}")

def start_file_watcher():
    """Start watching for file changes"""
    event_handler = FileChangeHandler(socketio)
    observer = Observer()

    # Watch templates, static, routes, models, and utils directories
    paths_to_watch = ['templates', 'static', 'routes', 'models', 'utils']
    for path in paths_to_watch:
        if os.path.exists(path):
            observer.schedule(event_handler, path, recursive=True)

    observer.start()
    print("[Live Reload] File watcher started - browser will auto-refresh on changes")

if __name__ == '__main__':
    print("=" * 60)
    print("GUT HEALTH MANAGEMENT APP")
    print("=" * 60)
    print("Access the application at: http://localhost:5000")
    print(f"Admin Mode: {'ENABLED' if app.config.get('ADMIN_MODE', False) else 'DISABLED'}")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Start file watcher in development mode
    start_file_watcher()

    # Run with SocketIO
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
