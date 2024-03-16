from app import create_app
from app import db  # Import the database instance


app = create_app()

if __name__ == "__main__":
    db.create_all()
    app.run()
