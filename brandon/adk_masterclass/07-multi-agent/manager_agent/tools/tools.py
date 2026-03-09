from datetime import datetime


def get_current_time() -> dict:
    """
    Get the current time in the format DD-MM-YYYY HH:MM:SS
    """
    return {
        "current_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }
