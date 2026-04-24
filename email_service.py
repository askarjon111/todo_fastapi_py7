import asyncio


async def send_welcome_email(email: str):
    # Simulate sending an email (e.g., using an email service)
    print(f"Sending welcome email to {email}...")
    await asyncio.sleep(5)  # Simulate delay
    print(f"Welcome email sent to {email}!")
