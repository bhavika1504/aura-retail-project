import sys
import os

# Add the aura_retail_os directory to the path so its modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), 'aura_retail_os'))

from api import app

# This entry point is required for Vercel to find and run the Flask application
if __name__ == "__main__":
    app.run()
