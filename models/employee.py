from extensions import db

class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    employment_type = db.Column(db.String(50), nullable=False)
    department_name = db.Column(db.String(200), nullable=False)  # TEXT INPUT
    designation = db.Column(db.String(200))
    joining_date = db.Column(db.String(50))   # DD-MM-YYYY
    status = db.Column(db.String(20), default="Active")
    logo_path = db.Column(db.String(300))

    project_users = db.relationship(
        "ProjectUser",
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    

    
    # project_assignments = db.relationship('ProjectUser', back_populates='employee', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "employment_type": self.employment_type,
            "department_name": self.department_name,  # DIRECT VALUE
            "designation": self.designation,
            "joining_date": self.joining_date,
            "status": self.status,
            "logo_path": self.logo_path
        }
