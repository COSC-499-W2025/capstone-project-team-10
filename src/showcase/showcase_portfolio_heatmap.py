# src/showcase/heatmap.py

from collections import defaultdict
from datetime import datetime, timedelta

class ActivityHeatmap:
    def __init__(self):
        # Use datetime.date as keys
        self.activity = defaultdict(int)

    def add_activity(self, date_str):
        """Register activity for a specific date."""
        if not date_str or date_str == "N/A":
            return

        # Convert 'Current' to today
        if date_str == "Current":
            date = datetime.now().date()
        else:
            try:
                date = datetime.fromisoformat(date_str).date()
            except Exception:
                print("Invalid date:", date_str)
                return

        self.activity[date] += 1
        print("Added activity:", date)

    def get_range(self):
        """Return min and max activity dates for the heatmap."""
        if not self.activity:
            today = datetime.now().date()
            return today - timedelta(days=365), today

        dates = sorted(self.activity.keys())
        print("Heatmap range from", dates[0], "to", dates[-1])
        return dates[0], dates[-1]

    def generate_html(self):
        """Generate HTML heatmap."""
        start, end = self.get_range()

        # Align start to Sunday
        start -= timedelta(days=(start.weekday() + 1) % 7)

        # Extend end to Saturday
        end += timedelta(days=(5 - end.weekday()) % 7)

        current = start
        days = []
        week_index = 0
        month_labels = []
        seen_months = set()

        while current <= end:
            count = self.activity.get(current, 0)

            if count == 0:
                level = 0
            elif count == 1:
                level = 1
            elif count <= 3:
                level = 2
            elif count <= 6:
                level = 3
            else:
                level = 4

            days.append(
                f'<div class="heatmap-day level-{level}" title="{current} ({count})"></div>'
            )

            # Detect first day of a month
            if current.day == 1 and current.month not in seen_months:
                seen_months.add(current.month)

                # calculate week column
                week_index = (current - start).days // 7

                month_name = current.strftime("%b")

                month_labels.append(
                    f'<div class="month-label" style="grid-column:{week_index + 1};">{month_name}</div>'
                )

            current += timedelta(days=1)

        return f"""
        <div class="heatmap">
            <div class="heatmap-months">
                {''.join(month_labels)}
            </div>

            <div class="heatmap-container">
                {''.join(days)}
            </div>
        </div>
        """