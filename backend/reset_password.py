from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

def reset():
    with app.app_context():
        users = User.query.all()

        # Reset specific users with new passwords
        for u in users:
            if u.email == "chanu@123":
                u.password = generate_password_hash("ch234")

            if u.email == "annu@930":
                u.password = generate_password_hash("anu234")

        db.session.commit()
        print("Passwords reset successfully!")

if __name__ == "__main__":
    reset()
