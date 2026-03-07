from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.designation import Designation

api = Namespace("Designations", description="Manage Designations")

# ---------------------------------------------------------
# Swagger Model
# ---------------------------------------------------------
designation_model = api.model("Designation", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True),
    "status": fields.String(default="Active")
})

# ---------------------------------------------------------
# CREATE DESIGNATION
# ---------------------------------------------------------
@api.route("/")
class DesignationCreate(Resource):

    @api.expect(designation_model)
    def post(self):
        data = request.get_json()

        new_dept = Designation(
            name=data.get("name"),
            status=data.get("status", "Active")
        )

        db.session.add(new_dept)
        db.session.commit()

        return {"message": "Designation created successfully"}, 201


# ---------------------------------------------------------
# LIST + SEARCH
# ---------------------------------------------------------
@api.route("/list")
class DesignationList(Resource):
    def get(self):
        search = request.args.get("search", "")

        designations = Designation.query.filter(
            Designation.name.like(f"%{search}%")
        ).order_by(Designation.id.desc()).all()

        return [
            {
                "id": d.id,
                "name": d.name,
                "status": d.status
            } for d in designations
        ], 200


# ---------------------------------------------------------
# GET / UPDATE / DELETE by ID
# ---------------------------------------------------------
@api.route("/<int:id>")
class DesignationByID(Resource):

    def get(self, id):
        dept = Designation.query.get(id)
        if not dept:
            return {"message": "Designation not found"}, 404

        return dept.to_dict(), 200

    @api.expect(designation_model)
    def put(self, id):
        designation = Designation.query.get(id)
        if not designation:
            return {"message": "Designation not found"}, 404

        data = request.get_json()

        designation.name = data.get("name", designation.name)
        designation.status = data.get("status", designation.status)

        db.session.commit()

        return {"message": "Designation updated successfully"}, 200

    def delete(self, id):
        designation = Designation.query.get(id)
        if not designation:
            return {"message": "Designation not found"}, 404

        db.session.delete(designation)
        db.session.commit()

        return {"message": "Department deleted successfully"}, 200
