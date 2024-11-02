# models/config.py

from database import db

class Config(db.Model):
    __tablename__ = 'configs'

    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value
        }
