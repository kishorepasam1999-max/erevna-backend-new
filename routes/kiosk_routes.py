from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.device import Device
from datetime import datetime

api = Namespace("Devices", description="Device (Kiosk) Management API")

# Swagger / API Model
device_model = api.model("Device", {
    "device_id": fields.String(readonly=True),
    "device_type": fields.String(required=True),
    "device_model": fields.String(required=True),
    "serial_number": fields.String,
    "location_id": fields.String(required=True),
    "status": fields.String,
    "installed_on": fields.DateTime,
    "last_active": fields.DateTime,
    "os_version": fields.String,
    "ip_address": fields.String,
    "firmware_version": fields.String,
    "notes": fields.String,
})


@api.route("")
class DeviceList(Resource):

    @api.marshal_list_with(device_model)
    def get(self):
        """Get all devices"""
        devices = Device.query.all()
        return devices

    @api.expect(device_model)
    def post(self):
        """Create a new device"""
        try:
            data = request.json
            print("RAW DATA:", data)

            if not data.get("device_type"):
                return {"message": "device_type is required"}, 400

            if not data.get("device_model"):
                return {"message": "device_model is required"}, 400

            if not data.get("location_id"):
                return {"message": "location_id is required"}, 400

            # Check serial number uniqueness if provided
            if data.get("serial_number"):
                existing = Device.query.filter_by(
                    serial_number=data.get("serial_number")
                ).first()
                if existing:
                    return {"message": "Device with this serial number already exists"}, 409

            device = Device(
                device_type=data.get("device_type"),
                device_model=data.get("device_model"),
                serial_number=data.get("serial_number"),
                location_id=data.get("location_id"),
                status=data.get("status", "Active"),
                installed_on=datetime.fromisoformat(data["installed_on"]) if data.get("installed_on") else None,
                last_active=datetime.fromisoformat(data["last_active"]) if data.get("last_active") else None,
                os_version=data.get("os_version"),
                ip_address=data.get("ip_address"),
                firmware_version=data.get("firmware_version"),
                notes=data.get("notes"),
            )

            db.session.add(device)
            db.session.commit()

            return {
                "message": "Device created successfully",
                "device_id": device.device_id
            }, 201

        except Exception as e:
            db.session.rollback()
            import traceback
            return {
                "error": str(e),
                "trace": traceback.format_exc()
            }, 500


@api.route("/<string:device_id>")
@api.param("device_id", "Device UUID")
class DeviceDetail(Resource):

    @api.marshal_with(device_model)
    def get(self, device_id):
        """Get a device by device_id"""
        device = Device.query.filter_by(device_id=device_id).first_or_404()
        return device

    @api.expect(device_model)
    def put(self, device_id):
        """Update device"""
        try:
            device = Device.query.filter_by(device_id=device_id).first_or_404()
            data = request.json

            for key, value in data.items():
                if hasattr(device, key):
                    if key in ["installed_on", "last_active"] and value:
                        value = datetime.fromisoformat(value)
                    setattr(device, key, value)

            db.session.commit()
            return {"message": "Device updated successfully"}

        except Exception as e:
            db.session.rollback()
            import traceback
            return {
                "error": str(e),
                "trace": traceback.format_exc()
            }, 500


    def delete(self, device_id):
        """Delete device"""
        device = Device.query.filter_by(device_id=device_id).first_or_404()
        db.session.delete(device)
        db.session.commit()
        return {"message": "Device deleted successfully"}, 200
