from app import create_app, db
from flask_migrate import upgrade

# Create the Flask app instance
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # This ensures the DB schema is up-to-date
        upgrade()

    # Start the server
    app.run(host="0.0.0.0", port=5000, debug=True)
