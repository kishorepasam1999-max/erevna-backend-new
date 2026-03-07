from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
from extensions import db
from models.project import (
    Project, ProjectUser, ProjectTask, ProjectLocation, ProjectKiosk, 
    ProjectGame, ProjectSchedule, ProjectQuota, 
    ProjectMetric
)
from models.project_version import ProjectVersion
from models.client import Client
from models.user import User
from models.location import Location
from models.device import Device as Kiosk
from models.device import Device as DeviceModel
from models.games import Game
from models.registration import Registration
from datetime import datetime
from models.employee import Employee
from sqlalchemy import JSON, text
from flask import jsonify

import json
import traceback

api = Namespace("projects", description="Project endpoints")

proj_in = api.model("ProjectIn", {
    "project_name": fields.String(required=True, description="Name of the project"),
    "client_name": fields.String(required=True, description="Name of the client"),
    "request_type": fields.String(
        required=True, 
        
        description="Type of request"
    ),
    "client_id":fields.String(required=False, description="Client_id"),
    "description": fields.String(description="Project description"),
    "status": fields.String(
        required=False,
        default='draft',
        enum=['draft', 'active', 'on_hold', 'completed', 'cancelled'],
        description="Current status of the project"
    )
})


project_user_model = api.model('ProjectUser', {
    'id': fields.Integer(readonly=True, description='Project User ID'),
    'project_id': fields.String(required=True, description='Project ID'),
    'employee_id': fields.Integer(required=True, description='Employee ID'),
    'department': fields.String(description='Department for this project'),
    'designation': fields.String(description='Designation for this project'),
    'stage': fields.String(description='Stage/Phase in the project'),
    
    'is_active': fields.Boolean(description='Whether the user is active in the project')
})

task_model = api.model('Task', {
    'project_id': fields.String(required=True, description='Project ID'),
    'stage': fields.String(required=True, description='Task stage'),
    'process': fields.String(description='Process name'),
    'title': fields.String(required=True, description='Task title'),
    'step': fields.String(description='Task step'),
    'type': fields.String(description='Task type'),
    'description': fields.String(description='Task description'),
    'start_date': fields.Date(description='Start date (YYYY-MM-DD)'),
    'end_date': fields.Date(description='End date (YYYY-MM-DD)'),
    'is_mandatory': fields.Boolean(description='Is task mandatory?'),
    'assigned_to': fields.Integer(description='Assigned user ID'),
    'priority': fields.String(description='Task priority (low/medium/high)'),
    'status': fields.String(description='Task status')
})

project_location_model = api.model('ProjectLocation', {
    'project_id': fields.String(required=True, description='The project ID'),
    'location_id': fields.String(required=True, description='The location ID'),
    'store_name': fields.String(required=True, description='The store name'),
    'address': fields.String(required=True, description='The full address'),
    'city': fields.String(required=True, description='The city'),
    'state': fields.String(description='The state/province'),
    'country': fields.String(required=True, description='The country'),
    'status': fields.String(required=True, enum=['Active', 'Inactive'], description='Location status'),
    'is_primary': fields.Boolean(default=False, description='Whether this is the primary location'),
    'notes': fields.String(description='Additional notes')
})

kiosk_in = api.model("ProjectKioskIn", {
    "location_id": fields.String(
        required=True,
        description="Project location ID"
    ),
    "kiosk_id": fields.String(
        required=True,
        description="Kiosk ID"
    ),
    "status": fields.String(
        required=False,
        description="Kiosk status",
        default="Active",
        enum=["Active", "Maintenance", "Inactive"]
    ),
    "installation_date": fields.Date(
        required=False,
        description="Date when the kiosk was installed"
    ),
    "notes": fields.String(
        required=False,
        description="Additional notes for the kiosk"
    )
})


game_in = api.model("ProjectGameIn", {
    "game_uuid": fields.String(required=True, description="UUID of the game"),
    "kiosk_ids": fields.List(fields.String),
    "configuration": fields.Raw,
    "is_active": fields.Boolean
})

schedule_in = api.model("ProjectScheduleIn", {
    # New fields
    "start_date": fields.DateTime(required=True, description='Project start date (ISO8601)'),
    "end_date": fields.DateTime(required=True, description='Project end date (ISO8601)'),
    "time_limit_seconds": fields.Integer(
        required=True,
        description='Session duration in seconds (30-1800)',
        min=30,
        max=1800
    ),
})

quota_model = api.model('Quota', {
    'total_samples_needed': fields.Integer(required=True, 
                                         description='Total number of samples needed',
                                         example=1000),
    'screening_criteria': fields.Raw(required=False,
                                   description='Screening criteria as key-value pairs',
                                   example={"age": {"min": 18, "max": 65}, 
                                           "location": "US"})
})

# Update the metric models
metric_model = api.model('ProjectMetric', {
    'id': fields.String(readonly=True, description='Metric ID'),
    'project_id': fields.String(description='Project ID'),
    'name': fields.String(description='Name of the metric'),
    'created_at': fields.DateTime(readonly=True, description='When the metric was created')
})

# New model for bulk operations
bulk_metrics_input = api.model('BulkMetricsInput', {
    'metrics': fields.List(fields.String(required=True, description='Metric name'), 
                          required=True,
                          description='List of metric names to add')
})

review_in = api.model("ProjectReviewIn", {
    "review_notes": fields.String,
    "review_rating": fields.Integer,
    "review_feedback": fields.String
})


def safe_json_loads(value, default=None):
    if value in (None, ''):
        return default if default is not None else {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default if default is not None else {}

# In routes/project_routes.py, update the ProjectList class:

@api.route('')
class ProjectList(Resource):
    @api.doc('create_project')
    @api.expect(proj_in, validate=True)
    def post(self):
        """Create a new project"""
        data = api.payload
        
        try:
            # Create new project
            project = Project(
                project_name=data.get('project_name'),
                client_name=data.get('client_name'),
                request_type=data.get('request_type'),
                client_id=data.get('client_id'),
                status='draft',  # Default status
                  # Assuming you're using JWT auth
            )
            
            db.session.add(project)
            db.session.commit()
            
            return {
                'message': 'Project created successfully',
                'project_id': project.project_id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

@api.route('/<string:project_id>')
@api.param('project_id', 'The project identifier')
@api.response(404, 'Project not found')
class ProjectResource(Resource):
    @api.doc('get_project')
    def get(self, project_id):
        """Get a specific project by ID"""
        project = Project.query.get_or_404(project_id)
        return project.serialize()

    @api.doc('update_project')
    @api.expect(proj_in)
    def put(self, project_id):
        """Update a project"""
        project = Project.query.get_or_404(project_id)
        data = api.payload
        
        try:
            # Update project fields
            project.project_name = data.get('project_name', project.project_name)
            project.client_name = data.get('client_name', project.client_name)
            project.request_type = data.get('request_type', project.request_type)
            
            db.session.commit()
            return {'message': 'Project updated successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    @api.doc('delete_project')
    def delete(self, project_id):
        """Delete a project"""
        project = Project.query.get_or_404(project_id)
        
        try:
            db.session.delete(project)
            db.session.commit()
            return {'message': 'Project deleted successfully'}
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

@api.route("/by-client/<string:client_id>")
class ProjectsByClient(Resource):
    def get(self, client_id):
        """Get all projects for a specific client"""
        projects = Project.query.filter_by(client_id=client_id).order_by(Project.created_at.desc()).all()
        
        if not projects:
            return {"message": f"No projects found for client {client_id}"}, 404
            
        return [{
            "project_id": p.project_id,
            "project_name": p.project_name,
            "client_id": p.client_id,
            "client_name": p.client_name,
            "status": p.status, 
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        } for p in projects]


@api.route('/<string:project_id>/users/batch')
class ProjectUsersBatch(Resource):
    @api.marshal_list_with(project_user_model)
    def get(self, project_id):

        parser = reqparse.RequestParser()
        parser.add_argument('department')
        parser.add_argument('designation')
        parser.add_argument('stage')
        parser.add_argument('is_active')

        args = parser.parse_args()

        query = ProjectUser.query.filter_by(project_id=project_id)

        if args['department']:
            query = query.filter(ProjectUser.department == args['department'])

        if args['designation']:
            query = query.filter(ProjectUser.designation == args['designation'])

        if args['stage']:
            query = query.filter(ProjectUser.stage == args['stage'])

        if args['is_active'] is not None:
            query = query.filter(ProjectUser.is_active == (args['is_active'].lower() == "true"))

        return query.all()

    @api.expect([project_user_model])
    def post(self, project_id):

        data = request.json
        if not isinstance(data, list):
            api.abort(400, "Expected a list of users")

        results = []
        added_count = 0

        for user_data in data:
            if "employee_id" not in user_data:
                results.append({
                "employee_id": None,
                "status": "error",
                "message": "Missing employee_id",
            })
            continue

        try:
            project_user = ProjectUser(
                project_id=project_id,
                employee_id=user_data["employee_id"],
                department=user_data.get("department"),
                designation=user_data.get("designation"),
                stage=user_data.get("stage"),
                is_active=user_data.get("is_active", True),
            )

            db.session.add(project_user)

            results.append({
                "employee_id": user_data["employee_id"],
                "status": "added",
                "message": "User added successfully",
            })
            added_count += 1

        except Exception as e:
            db.session.rollback()
            results.append({
                "employee_id": user_data.get("employee_id"),
                "status": "error",
                "message": str(e),
            })

        if added_count:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                api.abort(500, f"Commit failed: {str(e)}")

        return {
            "success": True,
            "message": f"{added_count} inserted",
            "results": results,
        }, 201

    @api.expect([project_user_model])
    def put(self, project_id):
        """Update multiple users in a project"""
        data = request.json
        if not isinstance(data, list):
            api.abort(400, "Expected a list of users")
            
        results = []
        updated_count = 0
        
        for user_data in data:
            if 'employee_id' not in user_data:
                results.append({
                    'employee_id': None,
                    'status': 'error',
                    'message': 'Missing required field: employee_id'
                })
                continue
                
            try:
                project_user = ProjectUser.query.filter_by(
                    project_id=project_id,
                    employee_id=user_data['employee_id']
                ).first()
                
                if not project_user:
                    results.append({
                        'employee_id': user_data['employee_id'],
                        'status': 'not_found',
                        'message': 'User not found in project'
                    })
                    continue
                
                # Update fields if provided
                if 'department' in user_data:
                    project_user.department = user_data['department']
                if 'designation' in user_data:
                    project_user.designation = user_data['designation']
                if 'stage' in user_data:
                    project_user.stage = user_data['stage']
                if 'is_active' in user_data:
                    project_user.is_active = user_data['is_active']
                
                results.append({
                    'employee_id': user_data['employee_id'],
                    'status': 'updated',
                    'message': 'User updated successfully'
                })
                updated_count += 1
                
            except Exception as e:
                db.session.rollback()
                results.append({
                    'employee_id': user_data.get('employee_id', 'unknown'),
                    'status': 'error',
                    'message': str(e)
                })
        
        if updated_count > 0:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                api.abort(500, f"Failed to save changes: {str(e)}")
                
        return {
            'success': True,
            'message': f'Processed {len(data)} users, {updated_count} updated successfully',
            'results': results
        }

    @api.expect([api.model('UserIds', {
        'employee_id': fields.Integer(required=True, description='Employee ID')
    })])
    def delete(self, project_id):
        """Remove multiple users from a project"""
        data = request.json
        if not isinstance(data, list):
            api.abort(400, "Expected a list of user IDs")
            
        results = []
        deleted_count = 0
        
        for user_data in data:
            if 'employee_id' not in user_data:
                results.append({
                    'employee_id': None,
                    'status': 'error',
                    'message': 'Missing required field: employee_id'
                })
                continue
                
            try:
                project_user = ProjectUser.query.filter_by(
                    project_id=project_id,
                    employee_id=user_data['employee_id']
                ).first()
                
                if not project_user:
                    results.append({
                        'employee_id': user_data['employee_id'],
                        'status': 'not_found',
                        'message': 'User not found in project'
                    })
                    continue
                
                db.session.delete(project_user)
                results.append({
                    'employee_id': user_data['employee_id'],
                    'status': 'deleted',
                    'message': 'User removed from project'
                })
                deleted_count += 1
                
            except Exception as e:
                db.session.rollback()
                results.append({
                    'employee_id': user_data.get('employee_id', 'unknown'),
                    'status': 'error',
                    'message': str(e)
                })
        
        if deleted_count > 0:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                api.abort(500, f"Failed to delete users: {str(e)}")
                
        return {
            'success': True,
            'message': f'Processed {len(data)} users, {deleted_count} removed successfully',
            'results': results
        }



@api.route("/<string:project_id>/tasks")
class ProjectTasks(Resource):
    @api.expect(task_model)
    def post(self, project_id):
        """Add a task to a project"""
        project = Project.query.get_or_404(project_id)
        data = api.payload
        
        try:
            task = ProjectTask(
                project_id=data['project_id'],
                stage=data['stage'],
                process=data.get('process'),
                title=data['title'],
                step=data.get('step'),
                type=data.get('type'),
                description=data.get('description'),
                start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
                end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
                is_mandatory=data.get('is_mandatory', False),
                assigned_to=data.get('assigned_to'),
                priority=data.get('priority'),
                status=data.get('status', 'pending')
            )
            
            db.session.add(task)
            db.session.commit()

            return task.serialize(), 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400
            
@api.route('/by-client-locations-project/<string:client_id>')
class ClientLocations(Resource):
    @api.doc('get_locations_by_client',
             description='Get all locations for a specific client')
    def get(self, client_id):
        """Get all locations for a specific client"""
        # Get all locations for the client
        locations = Location.query.filter_by(client_id=client_id).all()
        
        if not locations:
            return {"message": f"No locations found for client {client_id}"}, 404

        # Prepare the response
        response = []
        for location in locations:
            location_data = {
                "location_id": location.location_id,
                "store_name": location.store_name,
                "address": f"{location.address_line1 or ''}, {location.city or ''}, {location.state or ''}",
                "status": location.location_status or "active",
                "city": location.city,
                "state": location.state,
                "country": location.country
            }
            
            # Add timezone if available
            if hasattr(location, 'details') and isinstance(location.details, dict):
                location_data["timezone"] = location.details.get("timezone", "UTC")
            else:
                location_data["timezone"] = "UTC"
                
            response.append(location_data)

        return response

@api.route('/by-client-locations/<string:client_id>')
class ClientLocations(Resource):
    @api.doc('get_locations_by_client', description='Get all locations for a specific client')
    def get(self, client_id):
        """Get all locations for a specific client"""

        # Join project_locations with projects to filter by client_id
        locations = (
            db.session.query(ProjectLocation)
            .join(Project, ProjectLocation.project_id == Project.project_id)
            .filter(Project.client_id == client_id)
            .all()
        )
        
        if not locations:
            return {"message": f"No locations found for client {client_id}"}, 404

        response = []
        for loc in locations:
            loc_data = {
                "project_id": loc.project_id,
                "project_name": loc.project.project_name,
                "location_id": loc.location_id,
                "store_name": loc.store_name,
                "address": f"{loc.address or ''}, {loc.city or ''}, {loc.state or ''}",
                "status": loc.status or "Active",
                "city": loc.city,
                "state": loc.state,
                "country": loc.country,
                "is_primary": loc.is_primary,
                "created_at": loc.created_at.isoformat() if loc.created_at else None
            }

            # Add kiosks for this location
            kiosks = [
                {
                    "kiosk_id": k.device_id,
                    "status": k.status,
                    "last_active": k.last_active.isoformat() if k.last_active else None
                }
                for k in loc.kiosks
            ]
            loc_data["kiosks"] = kiosks

            # Add timezone if available
            loc_data["timezone"] = getattr(loc, "timezone", "UTC")

            response.append(loc_data)

        return {"data": response}, 200


@api.route('/<string:project_id>/locations')
class ProjectLocations(Resource):
    @api.doc('add_project_locations')
    @api.expect([project_location_model])
    def post(self, project_id):
        """Add multiple locations to a project with full location details"""
        locations_data = request.get_json()
        if not isinstance(locations_data, list):
            locations_data = [locations_data]
            
        try:
            added_locations = []
            
            for loc_data in locations_data:
                # Create project location with all details
                project_location = ProjectLocation(
                    project_id=project_id,
                    location_id=loc_data.get('location_id') or str(uuid.uuid4()),
                    store_name=loc_data['store_name'],
                    address=loc_data['address'],
                    city=loc_data['city'],
                    state=loc_data.get('state', ''),
                    country=loc_data['country'],
                    status=loc_data.get('status', 'Active'),
                    
                    is_primary=loc_data.get('is_primary', False),
                    notes=loc_data.get('notes', '')
                )
                
                db.session.add(project_location)
                added_locations.append(project_location.to_dict())
            
            db.session.commit()
            
            return {
                'message': f'Successfully added {len(added_locations)} locations to project',
                'added_locations': added_locations
            }, 201
            
        except KeyError as e:
            db.session.rollback()
            return {'message': f'Missing required field: {str(e)}'}, 400
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
    @api.doc('get_project_locations')
    @api.marshal_list_with(project_location_model)
    def get(self, project_id):
        """Get all locations for a project"""
        locations = ProjectLocation.query.filter_by(project_id=project_id).all()
        return locations





@api.route('/<string:project_id>/kiosks')
class ProjectKiosksList(Resource):
       def get(self, project_id):
        """
        Get all kiosks for a project based on its locations
        """
        try:
            # 1️⃣ Get all project kiosks with device details
            query = text("""
                SELECT 
                    d.device_id,
                    pk.location_id,
                    d.device_type,
                    d.device_model,
                    d.firmware_version,
                    d.status,
                    d.last_active
                FROM project_kiosks pk
                JOIN devices d ON pk.device_id COLLATE utf8mb4_unicode_ci = d.device_id COLLATE utf8mb4_unicode_ci
                WHERE pk.project_id = :project_id
            """)
            
            results = db.session.execute(query, {'project_id': project_id})
            
            # Prepare response
            kiosk_list = [{
                'device_id': row.device_id,
                'location_id': row.location_id,
                'device_name': f"{row.device_type} {row.device_model}",
                'device_type': row.device_type,
                'firmware_version': row.firmware_version,
                'status': row.status,
                'last_active': row.last_active.isoformat() if row.last_active else None
            } for row in results]
            
            return {"kiosks": kiosk_list}, 200
            
        except Exception as e:
            print(f"Error fetching kiosks for project {project_id}: {str(e)}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}, 500
    # def get(self, project_id):
    #     """
    #     Get all kiosks for a project based on its locations
    #     """
    #     try:
    #         # 1️⃣ Get location_ids for this project
    #         location_ids = [
    #             loc.location_id
    #             for loc in ProjectLocation.query.with_entities(ProjectLocation.location_id)
    #             .filter_by(project_id=project_id)
    #             .all()
    #         ]

    #         if not location_ids:
    #             return {"kiosks": []}, 200

    #         # 2️⃣ Get all devices in these locations
    #         kiosks = DeviceModel.query.filter(DeviceModel.location_id.in_(location_ids)).all()

    #         # 3️⃣ Prepare simplified response
    #         kiosk_list = [{
    #             'device_id': k.device_id,
    #             'location_id': k.location_id,
    #             'device_name': f"{k.device_type} {k.device_model}",
    #             'device_type': k.device_type,
    #             'firmware_version': k.firmware_version,
    #             'status': k.status,
    #             'last_active': k.last_active.isoformat() if k.last_active else None
    #         } for k in kiosks]

    #         return {"kiosks": kiosk_list}, 200

    #     except Exception as e:
    #         return {"success": False, "error": str(e)}, 500


@api.route('/<string:project_id>/devices')
class ProjectDevices(Resource):
    def post(self, project_id):
        """
        Save multiple kiosks for a project.
        Expected payload:
        {
            "kiosks": [
                {
                    "device_id": "uuid",
                    "location_id": "uuid",
                    "device_name": "string",
                    "device_type": "string",
                    "firmware_version": "string",
                    "status": "Active",
                    "last_active": "ISO datetime string"
                },
                ...
            ]
        }
        """
        try:
            data = request.get_json()
            if not data or "kiosks" not in data:
                return {"success": False, "message": "kiosks array is required"}, 400

            kiosks_data = data["kiosks"]
            if not kiosks_data:
                return {"success": False, "message": "kiosks array cannot be empty"}, 400

            # Optional: delete existing kiosks for this project to replace selection
            ProjectKiosk.query.filter_by(project_id=project_id).delete()

            # Prepare ProjectKiosk objects
            kiosks_to_insert = []
            for k in kiosks_data:
                # Basic validation
                if "device_id" not in k or "location_id" not in k:
                    continue  # skip invalid entries

                kiosks_to_insert.append(ProjectKiosk(
                    project_id=project_id,
                    device_id=k["device_id"],
                    location_id=k["location_id"]
                ))

            if not kiosks_to_insert:
                return {"success": False, "message": "No valid kiosks to save"}, 400

            # Bulk insert
            db.session.bulk_save_objects(kiosks_to_insert)
            db.session.commit()

            return {
                "success": True,
                "message": f"{len(kiosks_to_insert)} kiosks assigned to project"
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}, 500



@api.route('/games')
class GamesList(Resource):
    @api.doc('list_games',
             params={
                 'status': 'Filter by status (e.g., active, inactive)',
                 'game_type': 'Filter by game type',
                 'limit': 'Number of results per page',
                 'page': 'Page number'
             })
    def get(self):
        """Get a list of all games with pagination and filtering"""
        # Get query parameters
        status = request.args.get('status')
        game_type = request.args.get('game_type')
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 per page
        page = int(request.args.get('page', 1))
        
        # Build query
        query = Game.query
        
        # Apply filters
        if status:
            query = query.filter(Game.status == status)
        if game_type:
            query = query.filter(Game.game_type == game_type)
        
        # Get paginated results
        pagination = query.order_by(Game.game_name).paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        # Prepare response
        games = [{
            "game_id": game.uuid,
            "name": game.game_name,
            "type": game.game_type,
            "version": game.version,
            "status": game.status,
            "max_players": game.max_players,
            "average_duration": game.average_duration,
            "developer": game.developer,
            "description": game.description,
            "created_at": game.created_at.isoformat() if game.created_at else None,
            "updated_at": game.updated_at.isoformat() if game.updated_at else None
        } for game in pagination.items]
        
        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": limit,
            "games": games
        }
    


@api.route("/<string:project_id>/games")
class ProjectGames(Resource):

    # @api.doc('get_project_games')
    # def get(self, project_id):
    #     """Get all games for a project"""
    #     project = Project.query.get_or_404(project_id)
    #     project_games = ProjectGame.query.filter_by(project_id=project_id).all()
        
    #     games = []
    #     for pg in project_games:
    #         game = Game.query.filter_by(uuid=pg.game_id).first()
    #         if not game:
    #             continue  # skip invalid/missing games

    #         # Safely parse JSON fields
    #         try:
    #             kiosk_ids = json.loads(pg.kiosk_ids) if pg.kiosk_ids else []
    #         except json.JSONDecodeError:
    #             kiosk_ids = []
    #         try:
    #             configuration = json.loads(pg.configuration) if pg.configuration else {}
    #         except json.JSONDecodeError:
    #             configuration = {}

    #         games.append({
    #             "game_id": game.uuid,
    #             "name": game.game_name,
    #             "type": game.game_type,
    #             "version": game.version,
    #             "status": game.status,
    #             "configuration": configuration,
    #             "is_active": bool(pg.is_active),
    #             "kiosk_ids": kiosk_ids,
    #             "created_at": game.created_at.isoformat() if game.created_at else None,
    #             "updated_at": game.updated_at.isoformat() if getattr(game, 'updated_at', None) else None
    #         })
            
    #     return {
    #         "project_id": project_id,
    #         "total_games": len(games),
    #         "games": games
    #     }, 200


    @api.doc('get_project_games')
    def get(self, project_id):
        """Get all games for a project"""
        try:
            # First, verify the project exists
            project = Project.query.get_or_404(project_id)
            
            # Get all project games with a direct query to avoid relationship loading issues
            query = text("""
                SELECT pg.*, g.* 
                FROM project_games pg
                LEFT JOIN games g ON pg.game_id = g.uuid
                WHERE pg.project_id = :project_id
            """)
            
            results = db.session.execute(query, {'project_id': project_id})
            
            def safe_json_parse(value, default=None):
                if value is None or value == '':
                    return default
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except (json.JSONDecodeError, TypeError):
                    return default

            games = []
            for row in results:
                pg = dict(row._mapping)  # Convert to dict for easier access
                
                # Skip if game data is missing
                if not pg.get('game_id'):
                    print(f"Warning: Missing game data for project_game {pg.get('id')}")
                    continue
                    
                games.append({
                    "game_id": pg.get('game_id'),
                    "name": pg.get('game_name'),
                    "type": pg.get('game_type'),
                    "version": pg.get('version'),
                    "status": pg.get('status'),
                    "configuration": safe_json_parse(pg.get('configuration'), {}),
                    "is_active": bool(pg.get('is_active', False)),
                    "kiosk_ids": safe_json_parse(pg.get('kiosk_ids'), []),
                    "created_at": pg.get('created_at').isoformat() if pg.get('created_at') else None,
                    "updated_at": pg.get('updated_at').isoformat() if pg.get('updated_at') else None
                })
                
            return {
                "project_id": project_id,
                "total_games": len(games),
                "games": games
            }, 200

        except Exception as e:
            print(f"Unexpected error in get_project_games: {str(e)}")
            traceback.print_exc()  # This will print the full traceback
            return {"error": "An error occurred while fetching games"}, 500

    @api.expect(game_in)
    @api.response(201, "Game added to project")
    def post(self, project_id):

        Project.query.get_or_404(project_id)
        data = api.payload

        # ✅ 1. Validate game_id
        game_id = data.get("game_id")
        if not game_id:
            return {"error": "game_id is required"}, 400

        game = Game.query.filter_by(uuid=game_id).first()
        if not game:
            return {"error": "Game not found"}, 404

        # ✅ 2. Prevent duplicate
        existing = ProjectGame.query.filter_by(
            project_id=project_id,
            game_id=game_id
        ).first()
        if existing:
            return {"error": "Game already exists in project"}, 400

        # ✅ 3. Fetch kiosk_ids automatically
        kiosks = ProjectKiosk.query.filter_by(project_id=project_id).all()
        kiosk_ids = [k.device_id for k in kiosks]

        # ✅ 4. Save mapping
        project_game = ProjectGame(
            project_id=project_id,
            game_id=game_id,
            kiosk_ids=kiosk_ids,                # 👈 auto-mapped
            configuration=data.get("configuration", {}),
            is_active=data.get("is_active", True)
        )

        db.session.add(project_game)
        db.session.commit()

        return project_game.serialize(), 201

@api.route("/<string:project_id>/schedule")
@api.param('project_id', 'The project identifier')
class ProjectScheduleResource(Resource):
    @api.doc('update_project_schedule')
    @api.expect(schedule_in)
    def post(self, project_id):
        """Update project schedule with timeline and session settings"""
        data = api.payload

        # Validate required fields
        if not all(key in data for key in ['start_date', 'end_date', 'time_limit_seconds']):
            return {"error": "start_date, end_date, and time_limit_seconds are required"}, 400

        # Convert string dates to datetime objects
        try:
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return {"error": "Invalid date format. Use ISO 8601 format (e.g., 2025-01-01T00:00:00Z)"}, 400

        # Validate dates
        if start_date >= end_date:
            return {"error": "start_date must be before end_date"}, 400

        # Validate time limit
        if not (30 <= data['time_limit_seconds'] <= 1800):
            return {"error": "time_limit_seconds must be between 30 and 1800"}, 400

        try:
            # Get or create schedule
            schedule = ProjectSchedule.query.filter_by(project_id=project_id).first()
            if not schedule:
                schedule = ProjectSchedule(project_id=project_id)

            # Update fields
            schedule.start_date = start_date
            schedule.end_date = end_date
            schedule.time_limit_seconds = data['time_limit_seconds']

            db.session.add(schedule)
            db.session.commit()

            return {
                "message": "Project schedule updated successfully",
                "schedule": schedule.serialize()
            }

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

    @api.doc('get_project_schedule')
    def get(self, project_id):
        """Get project schedule"""
        schedule = ProjectSchedule.query.filter_by(project_id=project_id).first()
        if not schedule:
            return {"message": "No schedule found for this project"}, 404
        return schedule.serialize()

@api.route('/<string:project_id>/quota')
class ProjectQuotaResource(Resource):
    @api.doc('create_or_update_quota')
    @api.expect(quota_model)
    def post(self, project_id):
        """Create or update project quota"""
        data = request.get_json()
        
        # Get existing quota or create new one
        quota = ProjectQuota.query.filter_by(project_id=project_id).first()
        if not quota:
            quota = ProjectQuota(project_id=project_id)
            db.session.add(quota)
        
        # Update fields
        quota.total_samples_needed = data.get('total_samples_needed', 0)
        quota.screening_criteria = data.get('screening_criteria', {})
        quota.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return quota.serialize(), 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

@api.route('/<string:project_id>/metrics')
class ProjectMetrics(Resource):
    @api.doc('list_project_metrics')
    @api.marshal_list_with(metric_model)
    def get(self, project_id):
        """Get all metrics for a project"""
        project = Project.query.get_or_404(project_id)
        return project.metrics

    @api.doc('add_project_metrics')
    @api.expect(bulk_metrics_input)
    @api.marshal_list_with(metric_model, code=201)
    def post(self, project_id):
        """Add multiple metrics to a project at once"""
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        if 'metrics' not in data or not isinstance(data['metrics'], list):
            api.abort(400, "A list of metrics is required")
        
        # Get existing metric names (case-insensitive)
        existing_metrics = {m.name.lower() for m in project.metrics}
        new_metrics = []
        
        try:
            for metric_name in data['metrics']:
                if not metric_name or not metric_name.strip():
                    continue
                    
                name = metric_name.strip()
                if name.lower() not in existing_metrics:
                    metric = ProjectMetric(
                        project_id=project_id,
                        name=name
                    )
                    db.session.add(metric)
                    new_metrics.append(metric)
                    existing_metrics.add(name.lower())  # Prevent duplicates in the same request
            
            db.session.commit()
            return new_metrics, 201
            
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))

@api.route('/<string:project_id>/metrics/batch')
class ProjectMetricsBatch(Resource):
    @api.doc('delete_project_metrics')
    @api.expect(api.model('DeleteMetricsInput', {
        'metric_ids': fields.List(fields.String, required=True, description='List of metric IDs to delete')
    }))
    def delete(self, project_id):
        """Delete multiple metrics from a project"""
        data = request.get_json()
        
        if 'metric_ids' not in data or not isinstance(data['metric_ids'], list):
            api.abort(400, "A list of metric IDs is required")
            
        try:
            # Delete all specified metrics that belong to this project
            deleted = ProjectMetric.query.filter(
                ProjectMetric.id.in_(data['metric_ids']),
                ProjectMetric.project_id == project_id
            ).delete(synchronize_session=False)
            
            db.session.commit()
            return {"message": f"Successfully deleted {deleted} metrics"}, 200
            
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))



@api.route("/<string:project_id>/review-summary")
class ProjectReviewSummary(Resource):
    @api.doc("get_project_review_summary")
    def get(self, project_id):
        """Get full project summary for review page"""
        project = Project.query.get_or_404(project_id)

        # Project basic info
        project_data = {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "client_name": project.client_name,
            "request_type": project.request_type,
            "status": project.status,
            
            
        }

        # Locations
        locations = []
        for loc in project.locations:
            locations.append({
                "location_id": loc.location_id,
                "store_name": loc.store_name,
                "address": loc.address,
                "city": loc.city,
                "state": loc.state,
                "country": loc.country,
                "status": loc.status,
                "is_primary": loc.is_primary,
                "notes": loc.notes
            })

        # Kiosks
        kiosks = []
        for k in project.kiosks:
            device = DeviceModel.query.get(k.device_id)
            if device:
                kiosks.append({
                    "device_id": device.device_id,
                    "location_id": device.location_id,
                    "device_name": f"{device.device_type} {device.device_model}",
                    "device_type": device.device_type,
                    "firmware_version": device.firmware_version,
                    "status": device.status,
                    "last_active": device.last_active.isoformat() if device.last_active else None
                })

        # Games
        games = []
        for g in project.games:
            game = Game.query.get(g.game_id)
            if game:
                games.append({
                    "game_id": game.uuid,
                    "name": game.game_name,
                    "configuration": g.configuration,
                    "is_active": g.is_active,
                    "kiosk_ids": g.kiosk_ids
                })

        # Schedule
        schedule = None
        if project.schedule:
            schedule = {
                "start_date": project.schedule.start_date.isoformat() if project.schedule.start_date else None,
                "end_date": project.schedule.end_date.isoformat() if project.schedule.end_date else None,
                "time_limit_seconds": project.schedule.time_limit_seconds
            }

        # Quota
        quota = None
        if project.quotas:
            quota = project.quotas[0].serialize() if project.quotas else None

        # Metrics
        metrics = [{"id": m.id, "name": m.name, "created_at": m.created_at.isoformat() if m.created_at else None} 
                   for m in project.metrics]

        

        return {
            "project": project_data,
            "locations": locations,
            "kiosks": kiosks,
            "games": games,
            "schedule": schedule,
            "quota": quota,
            "metrics": metrics,
            
        }, 200

@api.route("/<string:project_id>/submit")
class ProjectSubmit(Resource):
    def post(self, project_id):
        project = Project.query.filter_by(project_id=project_id).first()

        if not project:
            return {"success": False, "message": "Project not found"}, 404

        if project.status == "active":
            return {
                "success": True,
                "message": "Project already submitted",
                "status": project.status
            }, 200

        project.status = "active"
        project.updated_at = datetime.utcnow()

        db.session.commit()

        return {
            "success": True,
            "message": "Project submitted successfully",
            "project_id": project.project_id,
            "status": project.status
        }, 200


@api.route("")
class ProjectList(Resource):
    def get(self):
        status = request.args.get("status")

        query = Project.query

        if status:
            query = query.filter(Project.status == status)

        projects = query.order_by(Project.created_at.desc()).all()

        return [
            {
                "project_id": p.project_id,
                "project_name": p.project_name,
                "client_id": p.client_id,
                "client_name": p.client_name,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in projects
        ], 200

@api.route("")
class ProjectList(Resource):
    def get(self):
        """Get all projects with full details"""
        status_filter = request.args.get("status")

        query = Project.query

        if status_filter:
            query = query.filter(Project.status == status_filter)

        projects = query.order_by(Project.created_at.desc()).all()

        all_projects = []

        for project in projects:
            project_data = {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "client_name": project.client_name,
                "request_type": project.request_type,
                "status": project.status,
            }

            # Locations
            locations = []
            for loc in project.locations:
                locations.append({
                    "location_id": loc.location_id,
                    "store_name": loc.store_name,
                    "address": loc.address,
                    "city": loc.city,
                    "state": loc.state,
                    "country": loc.country,
                    "status": loc.status,
                    "is_primary": loc.is_primary,
                    "notes": loc.notes
                })

            # Kiosks
            kiosks = []
            for k in project.kiosks:
                device = DeviceModel.query.get(k.device_id)
                if device:
                    kiosks.append({
                        "device_id": device.device_id,
                        "location_id": device.location_id,
                        "device_name": f"{device.device_type} {device.device_model}",
                        "device_type": device.device_type,
                        "firmware_version": device.firmware_version,
                        "status": device.status,
                        "last_active": device.last_active.isoformat() if device.last_active else None
                    })

            # Games
            games = []
            for g in project.games:
                game = Game.query.get(g.game_id)
                if game:
                    games.append({
                        "game_id": game.uuid,
                        "name": game.game_name,
                        "configuration": g.configuration,
                        "is_active": g.is_active,
                        "kiosk_ids": g.kiosk_ids
                    })

            # Schedule
            schedule = None
            if project.schedule:
                schedule = {
                    "start_date": project.schedule.start_date.isoformat() if project.schedule.start_date else None,
                    "end_date": project.schedule.end_date.isoformat() if project.schedule.end_date else None,
                    "time_limit_seconds": project.schedule.time_limit_seconds
                }

            # Quota
            quota = project.quotas[0].serialize() if project.quotas else None

            # Metrics
            metrics = [{"id": m.id, "name": m.name, "created_at": m.created_at.isoformat() if m.created_at else None} 
                       for m in project.metrics]

            all_projects.append({
                "project": project_data,
                "locations": locations,
                "kiosks": kiosks,
                "games": games,
                "schedule": schedule,
                "quota": quota,
                "metrics": metrics
            })

        return {"projects": all_projects}, 200


# Add this to your project_routes.py


@api.route("/<string:project_id>/users")
class ProjectUsersList(Resource):
    def get(self, project_id):
        """Get all users for a project with employee details"""
        project = Project.query.get_or_404(project_id)
        
        # Get stage filter from query parameter (optional)
        stage = request.args.get('stage')
        
        # Start with base query joining ProjectUser with Employee
        query = db.session.query(
            ProjectUser,
            Employee
        ).join(
            Employee, 
            ProjectUser.employee_id == Employee.id
        ).filter(
            ProjectUser.project_id == project_id
        )
        
        # Apply stage filter if provided
        if stage:
            query = query.filter(ProjectUser.stage == stage)
        
        # Order by stage and then by employee name
        results = query.order_by(
            ProjectUser.stage,
            Employee.full_name
        ).all()
        
        users_list = []
        for project_user, employee in results:
            user_data = {
                'id': project_user.id,
                'project_id': project_user.project_id,
                'employee_id': project_user.employee_id,
                'full_name': employee.full_name,
                'email': employee.email,
                'department': project_user.department or employee.department_name,
                'designation': project_user.designation or employee.designation,
                'stage': project_user.stage,
                'is_active': project_user.is_active,
                'created_at': project_user.created_at.isoformat() if project_user.created_at else None,
                'updated_at': project_user.updated_at.isoformat() if project_user.updated_at else None
            }
            users_list.append(user_data)
        
        return {
            'project_id': project_id,
            'stage_filter': stage,
            'total_users': len(users_list),
            'users': users_list
        }, 200

@api.route("/<string:project_id>/users-by-stage")
class ProjectUsersByStageNew(Resource):
    def get(self, project_id):
        """Get users grouped by stage with employee details"""
        project = Project.query.get_or_404(project_id)
        
        # Get all unique stages for this project
        stages = db.session.query(ProjectUser.stage).filter_by(
            project_id=project_id
        ).distinct().all()
        
        stages_list = [stage[0] for stage in stages if stage[0]]
        
        # Sort stages in natural order (S1, S2, S3, etc.)
        def sort_stages(stage_name):
            import re
            match = re.match(r'S(\d+)', stage_name)
            return int(match.group(1)) if match else stage_name
        
        stages_list.sort(key=sort_stages)
        
        result = {}
        
        for stage in stages_list:
            # Get users for this stage with employee details
            query = db.session.query(
                ProjectUser,
                Employee
            ).join(
                Employee, 
                ProjectUser.employee_id == Employee.id
            ).filter(
                ProjectUser.project_id == project_id,
                ProjectUser.stage == stage,
                ProjectUser.is_active == True
            ).order_by(Employee.full_name)
            
            results = query.all()
            
            users_list = []
            for project_user, employee in results:
                user_data = {
                    'id': project_user.id,
                    'employee_id': project_user.employee_id,
                    'full_name': employee.full_name,
                    'email': employee.email,
                    'department': project_user.department or employee.department_name,
                    'designation': project_user.designation or employee.designation,
                    'is_active': project_user.is_active,
                    'created_at': project_user.created_at.isoformat() if project_user.created_at else None
                }
                users_list.append(user_data)
            
            result[stage] = {
                'total_users': len(users_list),
                'users': users_list
            }
        
        return {
            'project_id': project_id,
            'stages': result,
            'summary': {
                'total_stages': len(stages_list),
                'total_unique_users': len(set(
                    user_id for stage_data in result.values() 
                    for user in stage_data['users'] 
                    for user_id in [user['employee_id']]
                ))
            }
        }, 200

@api.route("/<string:project_id>/users-by-stage/<string:stage>")
class ProjectUsersBySpecificStage(Resource):
    def get(self, project_id, stage):
        """Get users for a specific stage with employee details"""
        project = Project.query.get_or_404(project_id)
        
        # Get users for the specific stage with employee details
        query = db.session.query(
            ProjectUser,
            Employee
        ).join(
            Employee, 
            ProjectUser.employee_id == Employee.id
        ).filter(
            ProjectUser.project_id == project_id,
            ProjectUser.stage == stage
        ).order_by(Employee.full_name)
        
        results = query.all()
        
        users_list = []
        for project_user, employee in results:
            user_data = {
                'id': project_user.id,
                'employee_id': project_user.employee_id,
                'full_name': employee.full_name,
                'email': employee.email,
                'department': project_user.department or employee.department_name,
                'designation': project_user.designation or employee.designation,
                'stage': project_user.stage,
                'is_active': project_user.is_active,
                'created_at': project_user.created_at.isoformat() if project_user.created_at else None,
                'updated_at': project_user.updated_at.isoformat() if project_user.updated_at else None
            }
            users_list.append(user_data)
        
        return {
            'project_id': project_id,
            'stage': stage,
            'total_users': len(users_list),
            'users': users_list
        }, 200