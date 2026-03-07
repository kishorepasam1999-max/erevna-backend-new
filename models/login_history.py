class LoginHistory(db.Model):
    __tablename__ = "login_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    logged_in_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="logins")
