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

        return (end_date - start_date).days + 1

    except Exception:
        return 0


def sort_projects(projects, method="duration"):
    """
    Sort projects using different strategies.

    method options:
    - "duration"
    - "skills"
    - "combined"
    """

    if method == "duration":
        return sorted(
            projects,
            key=lambda p: get_project_duration_days(p),
            reverse=True
        )

    elif method == "skills":
        return sorted(
            projects,
            key=lambda p: len(p.get_skills()),
            reverse=True
        )

    elif method == "combined":
        return sorted(
            projects,
            key=lambda p: get_project_duration_days(p) + len(p.get_skills()) * 10,
            reverse=True
        )

    return projects


def get_top_projects(projects, limit=3, method="combined"):
    """Return top N projects based on sorting method."""
    sorted_projects = sort_projects(projects, method)
    return sorted_projects[:limit]