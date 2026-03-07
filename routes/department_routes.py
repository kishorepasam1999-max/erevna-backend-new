from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.department import Department

api = Namespace("Departments", description="Manage Departments")

# ---------------------------------------------------------
# Swagger Model
# ---------------------------------------------------------
department_model = api.model("Department", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True),
    "status": fields.String(default="Active")
})

# ---------------------------------------------------------
# CREATE DEPARTMENT
# ---------------------------------------------------------
@api.route("/")
class DepartmentCreate(Resource):

    @api.expect(department_model)
    def post(self):
        data = request.get_json()

        new_dept = Department(
            name=data.get("name"),
            status=data.get("status", "Active")
        )

        db.session.add(new_dept)
        db.session.commit()

        return {"message": "Department created successfully"}, 201


# ---------------------------------------------------------
# LIST + SEARCH
# ---------------------------------------------------------
@api.route("/list")
class DepartmentList(Resource):
    def get(self):
        search = request.args.get("search", "")

        departments = Department.query.filter(
            Department.name.like(f"%{search}%")
        ).order_by(Department.id.desc()).all()

        return [
            {
                "id": d.id,
                "name": d.name,
                "status": d.status
            } for d in departments
        ], 200


# ---------------------------------------------------------
# GET / UPDATE / DELETE by ID
# ---------------------------------------------------------
@api.route("/<int:id>")
class DepartmentByID(Resource):

    def get(self, id):
        dept = Department.query.get(id)
        if not dept:
            return {"message": "Department not found"}, 404

        return dept.to_dict(), 200

    @api.expect(department_model)
    def put(self, id):
        dept = Department.query.get(id)
        if not dept:
            return {"message": "Department not found"}, 404

        data = request.get_json()

        dept.name = data.get("name", dept.name)
        dept.status = data.get("status", dept.status)

        db.session.commit()

        return {"message": "Department updated successfully"}, 200

    def delete(self, id):
        dept = Department.query.get(id)
        if not dept:
            return {"message": "Department not found"}, 404

        db.session.delete(dept)
        db.session.commit()

        return {"message": "Department deleted successfully"}, 200
