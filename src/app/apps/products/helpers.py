import time


def log_after_response(message: str):
    time.sleep(3)
    print(f"[Background] {message}")
