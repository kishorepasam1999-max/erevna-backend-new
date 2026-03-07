import uuid  # Add this import
from flask import request
from flask_restx import Resource, fields, Namespace
from extensions import db

# Initialize namespace
api = Namespace('metrics', description='Metrics operations')

# API Model
metric_model = api.model('Metric', {
    'id': fields.String(readonly=True, description='Metric ID'),
    'name': fields.String(required=True, description='Metric name (e.g., response_time)')
})

class Metric(db.Model):
    """Simple metrics master table"""
    __tablename__ = "metrics"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }
@api.route('/')
class MetricList(Resource):

    @api.doc('get_all_metrics')
    def get(self):
        metrics = Metric.query.all()

        return {
            "success": True,
            "count": len(metrics),
            "metrics": [
                {
                    "id": m.id,
                    "name": m.name
                } for m in metrics
            ]
        }, 200

