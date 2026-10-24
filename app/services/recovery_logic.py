from datetime import datetime, timedelta

def check_threshold_met(approvals: list, threshold: int) -> bool:
    """Checks if the number of guardian approvals meets or exceeds the required threshold."""
    active_approvals = [a for a in approvals if a.get("approved") == True]
    return len(active_approvals) >= threshold

def calculate_recovery_expiry(hours: int = 48) -> datetime:
    """Calculates the expiration time for the safety recovery window."""
    return datetime.utcnow() + timedelta(hours=hours)