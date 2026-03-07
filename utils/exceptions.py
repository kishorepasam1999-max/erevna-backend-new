from flask import jsonify

class APIError(Exception):
    def __init__(self, message, code=400):
        super().__init__(message)
        self.message = message
        self.code = code


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_custom_error(error):
        return jsonify({"status": "error", "message": error.message}), error.code

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"status": "error", "message": "Server error"}), 500
