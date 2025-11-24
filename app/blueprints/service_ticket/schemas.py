from app.extensions import ma
from app.models import ServiceTicket
from ..mechanic.schemas import MechanicSchema
from ..inventory.schemas import InventorySchema
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True

    mechanics = fields.List(fields.Nested(MechanicSchema))
    parts = fields.List(fields.Nested(InventorySchema))
    status = fields.String()

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)