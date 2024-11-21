import requests

LINE_NOTIFY_API = "https://notify-api.line.me/api/notify"

class LineNotifier:
    def __init__(self, token: str) -> None:
        self.token = token

    def send_message(self, message: str) -> None:
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "message": message
        }
        try:
            response = requests.post(LINE_NOTIFY_API, headers=headers, data=data)
            if response.status_code == 200:
                print("Notification sent successfully.")
            else:
                print(f"Failed to send notification. Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error sending notification: {e}")