def success(message="", data=None):
    return {"status": "success", "message": message, "data": data}, 200


def created(message="", data=None):
    return {"status": "success", "message": message, "data": data}, 201


def error(message="", code=400):
    return {"status": "error", "message": message}, code
