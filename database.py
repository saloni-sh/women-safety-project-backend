from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy object
db = SQLAlchemy()

# Define the database model for alerts
class Alert(db.Model):
    __tablename__ = 'alerts'  # optional, gives a clear name to the table
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<Alert id={self.id}, lat={self.latitude}, lon={self.longitude}, notes={self.notes}>"
