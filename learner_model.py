from database import get_mastery, save_mastery, get_connection

def update_learner_model(student_name, concept, is_correct):
    old_score = get_mastery(student_name, concept)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT attempts, correct FROM mastery WHERE student_name=? AND concept=?",
        (student_name, concept)
    )

    row = cur.fetchone()
    attempts = row[0] if row else 0
    correct = row[1] if row else 0

    attempts += 1
    if is_correct:
        correct += 1
        target = 100
    else:
        target = 0

    new_score = 0.7 * old_score + 0.3 * target
    new_score = max(0, min(100, new_score))

    save_mastery(
        student_name,
        concept,
        new_score,
        attempts,
        correct
    )

    conn.close()
    return new_score

def get_mastery_status(score):
    if score <= 40:
        return "Weak"
    elif score <= 70:
        return "Developing"
    elif score <= 90:
        return "Strong"
    return "Mastered"

def get_difficulty(score):
    if score < 40:
        return "Easy"
    elif score < 70:
        return "Medium"
    elif score < 90:
        return "Hard"
    return "Advanced"