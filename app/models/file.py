# app/models/file.py
from app.config import db

class File(db.Model):
    __tablename__ = 'files'

    file_id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    processed = db.Column(db.Boolean, default=False, nullable=False)
    notified = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<File {self.filename}>'
