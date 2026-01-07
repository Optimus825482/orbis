from flask_cors import CORS

cors = CORS()

def init_extensions(app):
    """Extension'ları başlat."""
    cors.init_app(app)
