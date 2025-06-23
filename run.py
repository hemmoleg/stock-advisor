from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == "__main__":
  # Get configuration from environment variables with defaults
  host = os.getenv('FLASK_HOST', 'localhost')
  port = int(os.getenv('FLASK_PORT', 5000))
  debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
  
  print(f"Starting Flask app on {host}:{port} (debug={debug})")
  print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
  app.run(host=host, port=port, debug=debug)