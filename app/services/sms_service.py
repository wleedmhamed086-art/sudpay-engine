import os
import httpx

class SudaneseSMSGateway:
    def __init__(self):
        self.api_key = os.getenv("SMS_API_KEY", "DEMO_SUDAN_SMS_KEY")
        self.sender_id = os.getenv("SMS_SENDER_ID", "SudPay")
        self.api_url = os.getenv("SMS_API_URL", "https://api.smspoh.com/v1/send")

    async def send_escrow_otp(self, phone_number: str, otp_code: str, order_code: str):
        message = f"رمز تأكيد استلام طلبك ({order_code}) لدى SudPay هو: {otp_code}\nلا تشارك هذا الرمز إلا عند معاينة واستلام البضاعة من مندوب الشحن."
        payload = {
            "to": phone_number,
            "message": message,
            "sender": self.sender_id
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            try:
                if os.getenv("NODE_ENV", "development") == "development":
                    print(f"📱 [SMS SIMULATION to {phone_number}]: {message}")
                    return True
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=10.0)
                return response.status_code == 200
            except Exception as e:
                print(f"❌ SMS Error: {str(e)}")
                return False

sms_gateway = SudaneseSMSGateway()
