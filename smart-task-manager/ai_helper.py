from datetime import datetime, date


def suggest_breakdown(title, description=""):
    text = (title + " " + description).lower()

    steps = ["Plan / research what's needed", "Do the main work"]

    if any(w in text for w in ["report", "document", "write", "essay"]):
        steps = ["Outline the structure", "Write first draft", "Review and edit", "Finalize and submit"]
    elif any(w in text for w in ["design", "ui", "app", "website", "build"]):
        steps = ["Sketch/plan the design", "Build core functionality", "Test", "Polish and review"]
    elif any(w in text for w in ["meeting", "call", "presentation"]):
        steps = ["Prepare agenda/slides", "Share with attendees", "Hold the meeting", "Send follow-up notes"]
    else:
        steps = ["Break the task into smaller steps", "Work on step 1", "Review progress", "Complete and close out"]

    return steps


def suggest_priority(title, due_date_str, description=""):
    score = 0
    text = (title + " " + description).lower()

    urgent_words = ["urgent", "asap", "important", "critical", "deadline"]
    if any(w in text for w in urgent_words):
        score += 2

    if due_date_str:
        try:
            due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            days_left = (due - date.today()).days
            if days_left <= 1:
                score += 3
            elif days_left <= 3:
                score += 2
            elif days_left <= 7:
                score += 1
        except ValueError:
            pass

    if score >= 3:
        return "High"
    elif score >= 1:
        return "Medium"
    return "Low"

