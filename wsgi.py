from flask_app import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_RUN_PORT", 5005))
    app.run(debug=True, port=port)
