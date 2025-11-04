from marshmallow import ValidationError
from flask import request, jsonify
from sqlalchemy import select
from .schemas import mechanic_schema, mechanics_schema
from app.models import Mechanic, db
from . import mechanics_bp


@mechanics_bp.route('/', methods=['POST'])
def add_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().all()
    if existing_mechanic:
        return jsonify({'error': 'Email already associated with a mechanic'})

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

#GET ALL MECHANICS
@mechanics_bp.route("/", methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)

#GET SPECIFIC MECHANIC
@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404
#UPDATE SPECIFIC MECHANIC
@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#DELETE SPECIFIC MECHANIC
@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
def delete_mechanic(mechanic_id):
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)

        if not mechanic:
            return jsonify({"error": "Mechanic not found."}), 404

        db.session.delete(mechanic)
        db.session.commit()
        return jsonify({"message": f'Mechanic id: {mechanic_id}, successfully deleted.'}), 200
    
    except Exception as e:
        print(f'error deleting mechanic: {e}')
        return jsonify({"error": 'internal server error'}), 500