from flask_restx import Namespace, Resource, fields
from flask import request
from models.location import Location
from extensions import db
from datetime import datetime

api = Namespace('locations', description='Location related operations')

# Model for API documentation
location_model = api.model('Location', {
    'location_id': fields.String(readOnly=True, description='The location unique identifier'),
    'client_id': fields.String(readOnly=True, description='The client id for locations'),
    'partner_name': fields.String(required=True, description='Partner name'),
    'store_name': fields.String(required=True, description='Store name'),
    'address_line1': fields.String(required=True, description='Address line 1'),
    'address_line2': fields.String(description='Address line 2'),
    'city': fields.String(required=True, description='City'),
    'state': fields.String(description='State/Province'),
    'zip_code': fields.String(description='ZIP/Postal code'),
    'country': fields.String(required=True, description='Country'),
    'region': fields.String(description='Region'),
    'phone_number': fields.String(description='Phone number'),
    'email': fields.String(description='Email address'),
    'store_manager_name': fields.String(description='Store manager name'),
    'store_manager_contact': fields.String(description='Store manager contact'),
    'latitude': fields.Float(description='Latitude coordinate'),
    'longitude': fields.Float(description='Longitude coordinate'),
    'opening_date': fields.Date(description='Store opening date (YYYY-MM-DD)'),
    'store_size_sqft': fields.Float(description='Store size in square feet'),
    'number_of_employees': fields.Integer(description='Number of employees'),
    'hours_of_operation': fields.String(description='Business hours'),
    'partner_type': fields.String(description='Type of partner'),
    'location_status': fields.String(description='Current status of the location', default='Active'),
    'notes': fields.String(description='Additional notes')
})

@api.route('/')
class LocationList(Resource):
    @api.doc('list_locations')
    @api.param('status', 'Filter by status (e.g., Active, Inactive)')
    @api.param('search', 'Search term for store name or city')
    def get(self):
        """List all locations with optional filtering"""
        query = Location.query
        
        # Apply filters if provided
        status = request.args.get('status')
        if status:
            query = query.filter(Location.location_status == status)
            
        search = request.args.get('search')
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Location.store_name.ilike(search_term)) | 
                (Location.city.ilike(search_term))
            )
            
        locations = query.order_by(Location.store_name).all()
        return [location.serialize() for location in locations]
    
    @api.doc('create_location')
    @api.expect(location_model, validate=True)
    def post(self):
        """Create a new location"""
        data = request.get_json()
        
        # Check if location with same store_name already exists
        existing = Location.query.filter_by(
            store_name=data['store_name']
        ).first()
        
        if existing:
            return {'message': 'Location with this store name already exists'}, 400
            
        location = Location(**data)
        db.session.add(location)
        db.session.commit()
        
        return location.serialize(), 201

@api.route('/<string:location_id>')
@api.param('location_id', 'The location identifier')
@api.response(404, 'Location not found')
class LocationResource(Resource):
    @api.doc('get_location')
    def get(self, location_id):
        """Fetch a location given its identifier"""
        location = Location.query.get_or_404(location_id)
        return location.serialize()
    
    @api.doc('update_location')
    @api.expect(location_model, validate=False)
    def put(self, location_id):
        """Update a location"""
        location = Location.query.get_or_404(location_id)
        data = request.get_json()
        
        # Update fields from request data
        for key, value in data.items():
            if hasattr(location, key):
                setattr(location, key, value)
        
        location.updated_at = datetime.utcnow()
        db.session.commit()
        
        return location.serialize()
    
    @api.doc('delete_location')
    @api.response(204, 'Location deleted')
    def delete(self, location_id):
        """Delete a location"""
        location = Location.query.get_or_404(location_id)
        db.session.delete(location)
        db.session.commit()
        return '', 204