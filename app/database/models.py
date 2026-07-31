import enum
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime, func
from app.database.config import Base

class EscrowStatus(str, enum.Enum):
    PENDING = "PENDING"
    HELD_IN_ESCROW = "HELD_IN_ESCROW"
    RELEASED = "RELEASED"
    DISPUTED = "DISPUTED"
    REFUNDED = "REFUNDED"

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    completed_orders_count = Column(Integer, default=0)
    tier = Column(String, default="BRONZE")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    vendor_id = Column(Integer)
    carrier_id = Column(Integer)
    products_amount_sdg = Column(Float)
    shipping_amount_sdg = Column(Float)
    grand_total_sdg = Column(Float)
    delivery_otp = Column(String)
    escrow_status = Column(Enum(EscrowStatus), default=EscrowStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
