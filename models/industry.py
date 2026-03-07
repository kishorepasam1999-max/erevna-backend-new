# models/title.py

from extensions import db
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Industry(db.Model):
    __tablename__ = "industry"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Industry {self.name}>"
