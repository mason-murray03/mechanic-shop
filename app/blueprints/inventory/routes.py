from marshmallow import ValidationError
from flask import request, jsonify
from sqlalchemy import select
from .schemas import inventory_schema, inventories_schema
from app.models import db, Inventory
from . import inventory_bp
from app.extensions import limiter, cache
from ...utils.util import encode_token, token_required

@inventory_bp.route('/', methods=['POST'])
@limiter.limit("5 per hour")
def add_inventory():
    try:
        part_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(part_data)
    db.session.commit()
    return inventory_schema.jsonify(part_data), 201

#GET ALL INVENTORY ITEMS
@inventory_bp.route("/", methods=['GET'])
def get_inventory():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = select(Inventory)
        inventories = db.paginate(query, page=page, per_page=per_page)

        return inventories_schema.jsonify(inventories), 200
    except Exception as e:
        print(f'error fetching inventory: {e}')
        query = select(Inventory)
        parts = db.session.execute(query).scalars().all()

        return inventories_schema.jsonify(inventories)

#GET SPECIFIC INVENTORY ITEM
@inventory_bp.route("/<int:part_id>", methods=['GET'])
@cache.cached(timeout=60)
def get_part(part_id):
    part = db.session.get(Inventory, part_id)

    if part:
        return inventory_schema.jsonify(part), 200
    return jsonify({"error": "Part not found."}), 404

#UPDATE SPECIFIC INVENTORY ITEM
@inventory_bp.route("//<int:part_id>", methods=['PUT'])
def update_part(part_id):
    part = db.session.get(Inventory, part_id)

    if not part:
        return jsonify({"error": "Part not found."}), 404

    try:
        updated_data = inventory_schema.load(request.json, instance=part, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return inventory_schema.jsonify(part), 200

#DELETE SPECIFIC INVENTORY ITEM
@inventory_bp.route("/<int:part_id>", methods=['DELETE'])
def delete_part(part_id):
    try:
        part = db.session.get(Inventory, part_id)

        if not part:
            return jsonify({"error": "Part not found."}), 404

        db.session.delete(part)
        db.session.commit()
        return jsonify({"message": f'Part id: {part_id}, successfully deleted.'}), 200
    
    except Exception as e:
        print(f'error deleting part: {e}')
        return jsonify({"error": 'internal server error'}), 500