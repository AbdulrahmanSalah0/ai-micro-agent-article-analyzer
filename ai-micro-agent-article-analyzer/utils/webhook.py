# utils/webhook.py

import requests


def send_webhook(data: dict, url: str = None) -> None:
    """
    Simulate sending data to a webhook.

    Args:
        data (dict): The payload to send
        url (str): Webhook URL (optional)
    """

    if not url:
        print("📡 Mock Webhook Triggered:")
        print(data)
        return

    try:
        response = requests.post(url, json=data, timeout=5)

        if response.status_code == 200:
            print("✅ Webhook sent successfully")
        else:
            print(f"❌ Webhook failed with status: {response.status_code}")

    except Exception as e:
        print(f"❌ Webhook error: {e}")