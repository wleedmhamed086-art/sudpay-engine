import random
import string
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.config import get_db, Base, engine
from app.database.models import Order, Customer, EscrowStatus
from app.services.sms_service import sms_gateway

app = FastAPI(title="SudPay Core API", version="6.0")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Welcome to SudPay FinTech Engine v6.0"}

@app.get("/api/v1/shipping/offers")
async def get_shipping_offers(origin_state: str, destination_state: str):
    return [
        {"carrier_id": 101, "carrier_name": "شركة دلافين للشحن السريع", "cost_sdg": 2500, "estimated_hours": 24},
        {"carrier_id": 102, "carrier_name": "البريد السريع السوداني", "cost_sdg": 2000, "estimated_hours": 48},
        {"carrier_id": 103, "carrier_name": "ترحال لخدمات الشحن", "cost_sdg": 3000, "estimated_hours": 12}
    ]

@app.post("/api/v1/checkout/escrow-initiate")
async def escrow_initiate(customer_phone: str, vendor_id: int, carrier_id: int, products_amount_sdg: float, shipping_cost_sdg: float, db: AsyncSession = Depends(get_db)):
    otp_code = "".join(random.choices(string.digits, k=6))
    order_code = "SD_" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    grand_total = products_amount_sdg + shipping_cost_sdg

    stmt = select(Customer).where(Customer.phone_number == customer_phone)
    res = await db.execute(stmt)
    customer = res.scalars().first()
    if not customer:
        customer = Customer(phone_number=customer_phone)
        db.add(customer)
        await db.commit()
        await db.refresh(customer)

    order = Order(
        order_code=order_code,
        customer_id=customer.id,
        vendor_id=vendor_id,
        carrier_id=carrier_id,
        products_amount_sdg=products_amount_sdg,
        shipping_amount_sdg=shipping_cost_sdg,
        grand_total_sdg=grand_total,
        delivery_otp=otp_code,
        escrow_status=EscrowStatus.HELD_IN_ESCROW
    )
    db.add(order)
    await db.commit()

    await sms_gateway.send_escrow_otp(customer_phone, otp_code, order_code)

    return {
        "success": True,
        "order_code": order_code,
        "grand_total_sdg": grand_total,
        "escrow_status": "HELD_IN_ESCROW",
        "delivery_otp": otp_code,
        "message": "تم حجز المبلغ بنجاح لحين الاستلام والتحقق بالرمز."
    }

class OTPVerificationRequest(BaseModel):
    order_code: str
    otp_code: str

@app.post("/api/v1/escrow/verify-and-release")
async def verify_otp_and_release(payload: OTPVerificationRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Order).where(Order.order_code == payload.order_code)
    res = await db.execute(stmt)
    order = res.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="المعاملة غير موجودة")
    if order.escrow_status != EscrowStatus.HELD_IN_ESCROW and order.escrow_status != EscrowStatus.PENDING:
        raise HTTPException(status_code=400, detail="المعاملة غير صالحة للإفراج")
    if order.delivery_otp != payload.otp_code:
        raise HTTPException(status_code=400, detail="رمز الـ OTP غير صحيح")

    order.escrow_status = EscrowStatus.RELEASED
    await db.commit()

    return {
        "success": True,
        "status": "RELEASED",
        "vendor_payout_sdg": order.products_amount_sdg,
        "carrier_payout_sdg": order.shipping_amount_sdg,
        "message": "تم تأكيد التسليم وإفراج المبالغ بنجاح."
    }

@app.get("/api/v1/admin/analytics")
async def get_admin_analytics(db: AsyncSession = Depends(get_db)):
    stmt = select(Order)
    res = await db.execute(stmt)
    orders = res.scalars().all()

    total_volume = sum(o.grand_total_sdg for o in orders)
    escrow_held = sum(o.grand_total_sdg for o in orders if o.escrow_status in [EscrowStatus.PENDING, EscrowStatus.HELD_IN_ESCROW])
    platform_revenue = sum(o.products_amount_sdg * 0.025 for o in orders if o.escrow_status == EscrowStatus.RELEASED)

    recent_orders = []
    for o in orders[:10]:
        recent_orders.append({
            "order_code": o.order_code,
            "customer_phone": "0912345678",
            "vendor_name": "متجر التقنية",
            "carrier_name": "شركة دلافين للشحن",
            "grand_total": o.grand_total_sdg,
            "platform_commission": o.products_amount_sdg * 0.025,
            "status": o.escrow_status.value
        })

    return {
        "total_volume": total_volume,
        "escrow_held": escrow_held,
        "platform_revenue": platform_revenue,
        "total_orders": len(orders),
        "recent_orders": recent_orders
    }
