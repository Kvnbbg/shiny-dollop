# This Python script serves as the entry point for a Flask application. Here's a breakdown of what it
# does:
# This Python script is the entry point for a Flask application. Here's a breakdown of what it does:
from app import create_app
from app import db  # Import the database instance

app = create_app()

if __name__ == "__main__":
    db.create_all()
    app.run()
