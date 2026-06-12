"""Flask application factory for html2docx.

Usage::

    from html2docx.app import create_app
    app = create_app()
    app.run()
"""

from __future__ import annotations

import logging
import os

from flask import Flask

from html2docx.api.routes import create_blueprint


def create_app() -> Flask:
    """Create and configure the Flask application.

    Configuration is read from environment variables:
    - ``HTML2DOCX_MAX_CONTENT_MB``: Max request body size in MB (default: 16).
    - ``HTML2DOCX_DEBUG``: Set to "1" or "true" for debug mode (default: off).

    Returns:
        A configured Flask application instance.
    """
    app = Flask(__name__)

    # --- Configuration from environment ---
    max_content_mb = int(os.environ.get("HTML2DOCX_MAX_CONTENT_MB", "16"))
    app.config["MAX_CONTENT_LENGTH"] = max_content_mb * 1024 * 1024

    # --- Logging ---
    logging.basicConfig(
        level=logging.DEBUG if _is_debug() else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # --- Register blueprints ---
    app.register_blueprint(create_blueprint())

    return app


def _is_debug() -> bool:
    """Check if debug mode is enabled via environment variable."""
    return os.environ.get("HTML2DOCX_DEBUG", "").lower() in ("1", "true", "yes")


# Allow running with: python -m html2docx.app
if __name__ == "__main__":
    application = create_app()
    application.run(debug=_is_debug(), host="0.0.0.0", port=5000)
