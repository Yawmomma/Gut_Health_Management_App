# File utilities for Gut Health Management App

from flask import current_app


def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed

    Args:
        filename: The filename to check
        allowed_extensions: Optional set of extensions. If None, uses app config.
    """
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
