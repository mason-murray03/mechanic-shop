from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class = Base)


class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    address: Mapped[str] = mapped_column(db.String(255), nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(back_populates='customer')

class ServiceTicket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'), nullable=False)
    vehicle_info: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(db.String(50), nullable=False)

    customer: Mapped["Customer"] = db.relationship(back_populates='service_tickets')
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary='service_mechanic', back_populates='service_tickets')


class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    salary: Mapped[int] = mapped_column(nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary='service_mechanic', back_populates='mechanics')

service_mechanic = db.Table(
    'service_mechanic',
    Base.metadata,
    db.Column('service_ticket_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)