from datetime import datetime, timezone

class PlanStates:
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"          # Check-in overdue, warning notifications sent
    GRACE_PERIOD = "GRACE_PERIOD" # Intervention window active, guardians alerted
    TRIGGERED = "TRIGGERED"       # Fully executed, assets released

class BackendTriggerEngine:
    def __init__(self, check_in_interval_days: int = 30, grace_window_days: int = 14, warning_threshold_days: int = 5):
        self.check_in_interval_days = check_in_interval_days
        self.grace_window_days = grace_window_days
        self.warning_threshold_days = warning_threshold_days

    def evaluate_plan_state(self, last_check_in_iso: str) -> dict:
        """
        Evaluates a protection plan's lifecycle state based on UTC timestamps.
        """
        now = datetime.now(timezone.utc)
        
        # Parse last check-in and ensure timezone awareness
        last_check_in = datetime.fromisoformat(last_check_in_iso)
        if last_check_in.tzinfo is None:
            last_check_in = last_check_in.replace(tzinfo=timezone.utc)
            
        # Calculate full days elapsed
        diff_delta = now - last_check_in
        days_elapsed = max(0, diff_delta.days)

        deadline_days = self.check_in_interval_days
        total_grace_deadline = deadline_days + self.grace_window_days

        current_state = PlanStates.ACTIVE
        action_required = None

        if days_elapsed <= (deadline_days - self.warning_threshold_days):
            current_state = PlanStates.ACTIVE
        elif (deadline_days - self.warning_threshold_days) < days_elapsed <= deadline_days:
            current_state = PlanStates.WARNING
            action_required = "SEND_USER_WARNING_NOTIFICATION"
        elif deadline_days < days_elapsed <= total_grace_deadline:
            current_state = PlanStates.GRACE_PERIOD
            action_required = "ALERT_GUARDIANS_INTERVENTION_WINDOW"
        else:
            current_state = PlanStates.TRIGGERED
            action_required = "EXECUTE_PLAN_RELEASE_ASSETS"

        return {
            "current_state": current_state,
            "days_elapsed": days_elapsed,
            "days_remaining": max(0, total_grace_deadline - days_elapsed),
            "action_required": action_required
        }