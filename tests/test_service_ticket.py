import unittest
from datetime import date
from app import create_app
from app.models import ServiceTicket, Mechanic, Inventory, db

class TestServiceTicketRoutes(unittest.TestCase):

    def setUp(self):
        # Create app with default config name, then override for testing
        self.app = create_app("TestingConfig")
        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_service_ticket(self):
        resp = self.client.post("/service_tickets/", json={
            "customer_id": 1,
            "vehicle_info": "Toyota Camry",
            "service_date": str(date.today()),
            "status": "open"
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["vehicle_info"], "Toyota Camry")
        self.assertEqual(data["status"], "open")

    def test_get_service_tickets(self):
        with self.app.app_context():
            ticket = ServiceTicket(customer_id=1, vehicle_info="Honda Civic",
                                   service_date=date.today(), status="open")
            db.session.add(ticket)
            db.session.commit()

        resp = self.client.get("/service_tickets/")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(any(t["vehicle_info"] == "Honda Civic" for t in data))

    def test_get_service_ticket(self):
        with self.app.app_context():
            ticket = ServiceTicket(customer_id=1, vehicle_info="Ford Focus",
                                   service_date=date.today(), status="open")
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

        resp = self.client.get(f"/service_tickets/{ticket_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["vehicle_info"], "Ford Focus")

    def test_update_service_ticket(self):
        with self.app.app_context():
            ticket = ServiceTicket(customer_id=1, vehicle_info="Chevy Malibu",
                                   service_date=date.today(), status="open")
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

        resp = self.client.put(f"/service_tickets/{ticket_id}", json={"status": "closed"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "closed")

    def test_delete_service_ticket(self):
        with self.app.app_context():
            ticket = ServiceTicket(customer_id=1, vehicle_info="Nissan Altima",
                                   service_date=date.today(), status="open")
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

        resp = self.client.delete(f"/service_tickets/{ticket_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("successfully deleted", data["message"])

    def test_edit_mechanics(self):
        with self.app.app_context():
            ticket = ServiceTicket(customer_id=1, vehicle_info="Mazda 3",
                                   service_date=date.today(), status="open")
            mech = Mechanic(name="Tech1", email="tech1@example.com", phone="555-1111", salary=40000)
            db.session.add_all([ticket, mech])
            db.session.commit()
            ticket_id = ticket.id
            mech_id = mech.id

        resp = self.client.put(f"/service_tickets/{ticket_id}/edit", json={"add_ids": [mech_id]})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(any(m["id"] == mech_id for m in data["mechanics"]))

    def test_add_part_to_ticket(self):
        with self.app.app_context():
            ticket = ServiceTicket(customer_id=1, vehicle_info="Subaru Impreza",
                                   service_date=date.today(), status="open")
            part = Inventory(name="Brake Pads", price=49.99)
            db.session.add_all([ticket, part])
            db.session.commit()
            ticket_id = ticket.id
            part_id = part.id

        resp = self.client.put(f"/service_tickets/{ticket_id}/add-part/{part_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(any(p["id"] == part_id for p in data["parts"]))

if __name__ == "__main__":
    unittest.main()
