from marshmallow import ValidationError
from flask import request, jsonify
from sqlalchemy import select
from .schemas import service_ticket_schema, service_tickets_schema
from app.models import ServiceTicket, db
from . import service_tickets_bp


@service_tickets_bp.route('/', methods=['POST'])
def add_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_data.id)
    existing_service_ticket = db.session.execute(query).scalars().all()
    if existing_service_ticket:
        return jsonify({'error': 'Service ticket with this ID already exists'})

    new_service_ticket = service_ticket_data
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201

#GET ALL SERVICE TICKETS
@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets)

#GET SPECIFIC SERVICE TICKET
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['GET'])
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if service_ticket:
        return service_ticket_schema.jsonify(service_ticket), 200
    return jsonify({"error": "Service ticket not found."}), 404
#UPDATE SPECIFIC SERVICE TICKET
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['PUT'])
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in service_ticket_data.items():
        setattr(service_ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200

#DELETE SPECIFIC SERVICE TICKET
@service_tickets_bp.route("/<int:service_ticket_id>", methods=['DELETE'])
def delete_service_ticket(service_ticket_id):
    try:
        service_ticket = db.session.get(ServiceTicket, service_ticket_id)

        if not service_ticket:
            return jsonify({"error": "Service ticket not found."}), 404

        db.session.delete(service_ticket)
        db.session.commit()
        return jsonify({"message": f'Service ticket id: {service_ticket_id}, successfully deleted.'}), 200
    
    except Exception as e:
        print(f'error deleting service ticket: {e}')
        return jsonify({"error": 'internal server error'}), 500