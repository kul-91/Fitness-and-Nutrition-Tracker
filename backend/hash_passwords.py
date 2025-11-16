# scripts/hash_passwords.py
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
import re

def needs_hash(pw):
    # quick heuristic: Werkzeug hash starts with "pbkdf2:sha256:"
    return not (isinstance(pw, str) and pw.startswith("pbkdf2:"))

def main():
    users = User.query.all()
    changed = 0
    for u in users:
        if u.password and needs_hash(u.password):
            u.password = generate_password_hash(u.password)
            changed += 1
            print(f"Hashed user {u.email}")
    if changed:
        db.session.commit()
    print("Done. Users updated:", changed)

if __name__ == "__main__":
    # Run inside flask app context
    from app import app
    with app.app_context():
        main()
