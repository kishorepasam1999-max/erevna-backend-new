from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from models.client import Client
from services.email_service import send_credentials_email, generate_random_password
from models.user import User

api = Namespace("Clients", description="Client management API")

# Swagger Model
client_model = api.model("Client", {
    "id": fields.Integer(readonly=True),
    "uuid": fields.String,
    "title": fields.String,
    "first_name": fields.String(required=True),
    "last_name": fields.String,
    "company_name": fields.String,
    "contact_name": fields.String,
    "primary_email": fields.String(required=True),
    "secondary_email": fields.String,
    "industry": fields.String,
    "client_admin": fields.String,
    "primary_contact_number": fields.String,
    "secondary_contact_number": fields.String,
    "company_team_size": fields.Integer,
    "pincode": fields.String,
    "city": fields.String,
    "state": fields.String,
    "country": fields.String,
    "additional_notes": fields.String,
})

@api.route("")
class ClientList(Resource):

    @api.marshal_list_with(client_model)
    def get(self):
        """List all clients"""
        clients = Client.query.all()
        return clients

    # @api.expect(client_model)
    # @api.marshal_with(client_model, code=201)
    # def post(self):
    #     """Create a new client"""
    #     # data = request.json
    #     data = api.payload
    #     print("Received data:", data)  # Debug log
    #     print("Available keys in data:", data.keys())
    #     print("primary_email value:", data.get('primary_email'))
    #     print("primary-email value:", data.get('primary-email'))
        
    #     username = data.get('primary-email') or data.get('primary_email')

    #     if username:
    #         username = str(username).split('@')[0]
    #     else:
    #         username = "user"
    #         print("Warning: No email found in data")
    #     password = generate_random_password()
    #     print("Generated username:", username)

    #     client = Client(**data)
    #     db.session.add(client)
    #     db.session.commit()

    #     try:

    #         send_credentials_email(
    #             email = client.primary_email,
    #             username= username,
    #             password = password
    #         )
    #     except Exception as e:
    #         print(f"Failed to send login email: {str(e)}")
    #         # Don't fail the request if email sending fails
    #         pass

    #     return client, 201
    @api.expect(client_model)
    def post(self):
        try:
            data = request.json
            print("RAW REQUEST:", data)

            if not data.get("first_name"):
                return {"message": "first_name is required"}, 400

            email = data.get("primary_email") or data.get("primary-email")
            if not email:
                return {"message": "primary_email is required"}, 400

            # Generate credentials
            display_name = f"{data.get('first_name')} {data.get('last_name', '')}".strip()
            password = generate_random_password()

            # Check duplicate user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {"message": "User already exists"}, 409

            # Create client
            client = Client(
                title=data.get("title"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                company_name=data.get("company_name"),
                contact_name=data.get("contact_name"),
                primary_email=email,
                secondary_email=data.get("secondary_email"),
                industry=data.get("industry"),
                client_admin=data.get("client_admin"),
                primary_contact_number=data.get("primary_contact_number"),
                secondary_contact_number=data.get("secondary_contact_number"),
                company_team_size=data.get("company_team_size"),
                pincode=data.get("pincode"),
                city=data.get("city"),
                state=data.get("state"),
                country=data.get("country"),
                additional_notes=data.get("additional_notes"),
            )

            db.session.add(client)

            # Create user
            user = User(
                name=f"{data.get('first_name')} {data.get('last_name', '')}".strip(),
                email=email,
                
                role='client',
                
            )

            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Send credentials
            send_credentials_email(email, display_name, password)

            return {"message": "Client and User created successfully"}, 201

        except Exception as e:
            db.session.rollback()
            import traceback
            error_details = traceback.format_exc()
            print(error_details)
            return {"error": str(e), "trace": error_details}, 500



@api.route("/<int:id>")
@api.param("id", "Client ID")
class ClientDetail(Resource):

    @api.marshal_with(client_model)
    def get(self, id):
        """Get client by ID"""
        client = Client.query.get_or_404(id)
        return client

    @api.expect(client_model)
    @api.marshal_with(client_model)
    def put(self, id):
        """Update client by ID"""
        client = Client.query.get_or_404(id)
        data = request.json

        for key, value in data.items():
            setattr(client, key, value)

        db.session.commit()
        return client

    def delete(self, id):
        """Delete client by ID"""
        client = Client.query.get_or_404(id)
        db.session.delete(client)
        db.session.commit()
        return {"message": "Client deleted"}, 200
