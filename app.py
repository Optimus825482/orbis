import os
from flask import Flask
import config
from extensions import cors, init_extensions

def create_app(test_config=None):
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    
    # Config
    app_config = config.get_config()
    app.config.from_object(app_config)
    
    if test_config:
        app.config.from_mapping(test_config)
        
    # Extensions
    init_extensions(app)
    
    # Blueprints
    import routes
    app.register_blueprint(routes.bp)
    
    # Jinja Filters
    import utils
    app.jinja_env.filters["date"] = utils.format_date
    app.jinja_env.filters["time"] = utils.format_time
    app.jinja_env.filters["safe_round"] = utils.safe_round
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
