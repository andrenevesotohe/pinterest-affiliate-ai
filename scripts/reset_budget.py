from modules.budget_tracker import DalleBudgetTracker
import datetime

def reset_budget():
    tracker = DalleBudgetTracker()
    tracker.used_today = 0
    tracker.reset_time = datetime.datetime.now()
    print(f"Budget reset to ${tracker.daily_limit - tracker.used_today:.2f} remaining")

if __name__ == "__main__":
    reset_budget() 