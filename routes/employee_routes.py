from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.employee import Employee
from models.department import Department
from werkzeug.utils import secure_filename
import os

api = Namespace("Employees", description="Manage Employees")

UPLOAD_FOLDER = "uploads/employees"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Swagger model
employee_model = api.model("Employee", {
    "full_name": fields.String(required=True),
    "email": fields.String(required=True),
    "employment_type": fields.String(required=True),
    "department_name": fields.String(required=True),
    "designation": fields.String,
    "joining_date": fields.String(required=True),
    "status": fields.String,
})

upload_parser = api.parser()
upload_parser.add_argument(
    "file",
    location="files",
    type="file",
    required=True,
    help="Upload employee logo"
)


# ---------------------------------------------------------
# CREATE EMPLOYEE
# ---------------------------------------------------------
@api.route("/")
class CreateEmployee(Resource):

    @api.expect(employee_model)
    def post(self):
        data = request.get_json()

        new_emp = Employee(
            full_name=data["full_name"],
            email=data["email"],
            employment_type=data["employment_type"],
            department_name=data["department_name"],
            designation=data.get("designation"),
            joining_date=data["joining_date"],
            status=data.get("status", "Active")
        )

        db.session.add(new_emp)
        db.session.commit()

        return {"message": "Employee created successfully", "id": new_emp.id}, 201


# ---------------------------------------------------------
# GET ALL EMPLOYEES
# ---------------------------------------------------------
@api.route("/list")
class EmployeeList(Resource):
    def get(self):
        employees = Employee.query.order_by(Employee.id.desc()).all()
        return [emp.to_dict() for emp in employees], 200


# ---------------------------------------------------------
# GET / UPDATE / DELETE EMPLOYEE BY ID
# ---------------------------------------------------------
@api.route("/<int:id>")
class EmployeeByID(Resource):

    def get(self, id):
        emp = Employee.query.get(id)
        if not emp:
            return {"message": "Employee not found"}, 404
        return emp.to_dict(), 200

    @api.expect(employee_model)
    def put(self, id):
        emp = Employee.query.get(id)
        if not emp:
            return {"message": "Employee not found"}, 404

        data = request.json

        emp.full_name = data.get("full_name", emp.full_name)
        emp.email = data.get("email", emp.email)
        emp.employment_type = data.get("employment_type", emp.employment_type)
        emp.department_name = data.get("department_name", emp.department_name)
        emp.designation = data.get("designation", emp.designation)
        emp.joining_date = data.get("joining_date", emp.joining_date)
        emp.status = data.get("status", emp.status)

        db.session.commit()
        return {"message": "Employee updated successfully"}, 200

    def delete(self, id):
        emp = Employee.query.get(id)
        if not emp:
            return {"message": "Employee not found"}, 404

        db.session.delete(emp)
        db.session.commit()
        return {"message": "Employee deleted"}, 200


# ---------------------------------------------------------
# UPLOAD LOGO
# ---------------------------------------------------------
@api.route("/upload-logo/<int:id>")
class EmployeeLogoUpload(Resource):

    @api.expect(upload_parser)
    def post(self, id):
        emp = Employee.query.get(id)
        if not emp:
            return {"message": "Employee not found"}, 404

        file = request.files.get("file")
        if not file:
            return {"message": "No file uploaded"}, 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        emp.logo_path = filepath
        db.session.commit()

        return {"message": "Logo uploaded successfully", "path": filepath}, 200
