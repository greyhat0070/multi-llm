from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load env FIRST
load_dotenv()

from routes.chat import chat_bp

def create_app():
    app = Flask(__name__)

    # ✅ CORS only here (after app is created)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    app.register_blueprint(chat_bp, url_prefix='/api')

    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "SynapseX AI Backend Running", "version": "1.0"}

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    # ✅ threaded=True is REQUIRED for streaming
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)