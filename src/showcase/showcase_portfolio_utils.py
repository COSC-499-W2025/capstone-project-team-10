from datetime import datetime


from datetime import datetime


def get_project_duration_days(project):
    """Return project duration in days."""

    start = project.get_start_date()
    end = project.get_end_date()

    if not start or not end or start == "N/A":
        return 0

    try:
        start_date = datetime.fromisoformat(start).date()

        if end == "Current":
            end_date = datetime.now().date()
        else:
            end_date = datetime.fromisoformat(end).date()

        return (end_date - start_date).days

    except Exception as e:
        print("Duration parse error:", start, end)
        return 0


def score_project(project):
    """
    Score project based on:
    - duration
    - number of skills
    """
    duration = get_project_duration_days(project)
    skill_count = len(project.get_skills())

    return duration + (skill_count * 10)


def get_top_projects(projects, limit=3):
    """Return top N ranked projects."""
    ranked = sorted(projects, key=score_project, reverse=True)
    return ranked[:limit]