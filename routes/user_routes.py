# user_routes.py
from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.user import User
from sqlalchemy import text

api = Namespace('users', description='User related operations')

@api.route('/')
class UserList(Resource):
    def get(self):
        """Get all users"""
        users = User.query.all()
        return [{
            'id': user.id,
            'email': user.email,
            'role': user.role
        } for user in users]

@api.route('/<string:email>/role')
class UserRole(Resource):
    def put(self, email):
        """Update user role"""
        data = request.get_json()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404
        
        user.role = data.get('role', 'user')
        db.session.commit()
        return {'message': 'Role updated successfully'}

@api.route('/admin-employees')
class AdminEmployees(Resource):
    def get(self):
        result = db.session.execute(
            text("""
                SELECT e.id AS employee_id, e.email
                FROM users u
                JOIN employees e
                  ON LOWER(u.email) = LOWER(e.email)
                WHERE u.role = 'admin'
            """)
        ).fetchall()

        return [
            {
                "employee_id": row.employee_id,
                "email": row.email
            }
            for row in result
        ]
