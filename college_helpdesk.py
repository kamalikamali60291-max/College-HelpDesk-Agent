"""
Rule-Based College FAQ Bot -> Ontology-Driven Campus Help-Desk Agent
Run: python college_helpdesk.py
No external libraries required.
"""

import re
from datetime import datetime

# -------------------- KNOWLEDGE BASE / EDITABLE RULES --------------------
FAQ_RULES = [
    (["fee", "fees", "tuition", "payment"], "Fees", "The tuition fee depends on the course. Contact the accounts office for the official fee structure and payment deadlines."),
    (["college time", "timing", "timings", "working hours", "college hours"], "Timings", "Regular college hours are typically 9:00 AM to 4:00 PM. Check your department notice for changes."),
    (["hostel", "accommodation", "room"], "Hostel", "Hostel accommodation is managed by the hostel office. Contact the warden for room availability, rules, and fees."),
    (["exam", "exams", "semester", "internal", "timetable"], "Exams", "Exam timetables and hall-ticket updates are published by the examination cell."),
    (["placement", "placements", "job", "campus interview"], "Placements", "The placement cell shares company drives, eligibility rules, training schedules, and interview updates."),
    (["attendance", "absent", "percentage"], "Attendance", "Check your attendance percentage in the student portal. Contact your class advisor if any entry is incorrect."),
    (["library", "book", "borrow"], "Library", "The library provides books and study resources. Ask the librarian about borrowing limits and return dates."),
    (["scholarship", "financial aid"], "Scholarship", "Contact the scholarship section for eligibility, required documents, and application deadlines."),
    (["bus", "transport", "college bus"], "Transport", "Contact the transport office for bus routes, fees, and pickup timings."),
    (["leave", "permission"], "Leave", "Submit a leave request through the process approved by your class advisor or department."),
    (["hod", "head of department"], "Department", "Your Head of Department can help with academic and department-related issues."),
    (["faculty", "teacher", "professor", "staff"], "Faculty", "Contact your department office for faculty contact details and consultation hours."),
    (["course", "courses", "branch", "department"], "Courses", "The college offers programs through its departments. Contact admissions for the current approved course list."),
    (["admission", "apply", "joining"], "Admissions", "Contact the admissions office for eligibility, application steps, required documents, and deadlines."),
    (["id card", "identity card"], "ID Card", "Contact the student section to request a new or replacement college ID card."),
    (["wifi", "internet"], "Wi-Fi", "Use the student Wi-Fi credentials provided by the IT support team. Report connection issues to IT support."),
    (["lab", "laboratory", "lab hours"], "Laboratory", "Lab schedules are shared by the department. Follow the lab safety instructions and faculty guidance."),
    (["result", "results", "marks", "grade"], "Results", "Semester results are published by the examination cell or student portal."),
    (["certificate", "bonafide", "transcript"], "Certificates", "Apply through the student section and provide the required details and supporting documents."),
    (["canteen", "food", "lunch"], "Canteen", "The campus canteen serves meals and snacks during its announced operating hours."),
    (["wifi password", "password reset", "login"], "IT Support", "Contact IT support or use the official password-reset process. Never share your password."),
    (["ragging", "harassment", "complaint"], "Student Support", "Report concerns to the college's designated anti-ragging or student grievance committee."),
    (["sports", "gym", "playground"], "Sports", "Contact the physical education or sports office for facilities, timings, and team registration."),
    (["holiday", "holidays", "working day"], "Calendar", "Refer to the official academic calendar and department announcements for holidays."),
]

# Simple college ontology: entities and relationships.
ONTOLOGY = {
    "Department": {"has": ["Faculty", "Course", "Lab"], "office": "Department office"},
    "Course": {"belongs_to": "Department", "related_to": ["Exam", "Faculty", "Placement"]},
    "Faculty": {"works_in": "Department", "can_help_with": ["Course", "Exam", "Appointment"]},
    "Hostel": {"managed_by": "Warden", "related_to": ["Fee", "Accommodation"]},
    "Fee": {"handled_by": "Accounts office", "related_to": ["Course", "Hostel"]},
    "Exam": {"handled_by": "Examination cell", "related_to": ["Course", "Result", "Timetable"]},
    "Placement": {"handled_by": "Placement cell", "related_to": ["Course", "Job"]},
    "Appointment": {"requires": ["Faculty", "Date", "Time slot"]},
}

# Appointment slots are sample data for a demonstration, not live college availability.
SLOTS = {
    "Monday": ["10:00", "11:00", "14:00"],
    "Tuesday": ["09:00", "11:00", "15:00"],
    "Wednesday": ["10:00", "13:00", "14:00"],
    "Thursday": ["09:00", "12:00", "15:00"],
    "Friday": ["10:00", "11:00", "14:00"],
}
BOOKED = {("Monday", "10:00"), ("Tuesday", "11:00")}
BOOKINGS = []


def normalize(text):
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()


def keyword_answer(question):
    """Baseline: choose the FAQ rule with the largest keyword match."""
    q = normalize(question)
    best_rule, best_score = None, 0
    for keywords, topic, answer in FAQ_RULES:
        score = sum(1 for word in keywords if normalize(word) in q)
        if score > best_score:
            best_rule, best_score = (topic, answer), score
    if best_rule:
        return best_rule[1], min(0.98, 0.55 + 0.12 * best_score), best_rule[0]
    return ("I don't know the exact answer. I'll refer this question to the college help desk.",
            0.20, "Human escalation")


def ontology_answer(question):
    """Ontology-enhanced reasoning: infer related topics and use keyword rules."""
    q = normalize(question)
    expanded = q
    # Relationship-based expansion: e.g. 'marks' implies Result, related to Exam.
    relation_terms = {
        "result": " exam marks grade timetable",
        "marks": " result exam grade",
        "teacher": " faculty department appointment",
        "professor": " faculty department appointment",
        "hostel": " accommodation warden fee",
        "job": " placement course interview",
        "interview": " placement job",
        "course": " department faculty exam placement",
        "appointment": " faculty meeting counsellor office",
        "counsellor": " appointment faculty meeting",
    }
    for trigger, related in relation_terms.items():
        if trigger in q:
            expanded += " " + related
    answer, confidence, topic = keyword_answer(expanded)
    if topic != "Human escalation":
        confidence = min(0.99, confidence + 0.08)
        explanation = f"Ontology inference: matched '{topic}' and checked related college concepts."
    else:
        explanation = "No matching ontology concept or FAQ rule; escalate to a human."
    return answer, confidence, topic, explanation


def book_appointment():
    print("\n--- FACULTY APPOINTMENT BOOKING (CSP + BACKTRACKING) ---")
    faculty = input("Faculty / office / counsellor name: ").strip() or "Faculty advisor"
    day = input("Day (Monday-Friday): ").strip().title()
    if day not in SLOTS:
        print("Invalid day. Please use Monday, Tuesday, Wednesday, Thursday, or Friday.")
        return
    preferred = input("Preferred time (e.g. 10:00), or press Enter for any: ").strip()
    # CSP constraints: valid day/time, one appointment per slot, 3 slots/day.
    candidates = ([preferred] if preferred else []) + [t for t in SLOTS[day] if t != preferred]
    print("CSP constraints: valid slot, slot not already booked, maximum 3 listed slots per day.")
    for slot in candidates:  # backtracking-style search through candidate assignments
        if slot in SLOTS[day] and (day, slot) not in BOOKED:
            BOOKED.add((day, slot))
            booking = {"faculty": faculty, "day": day, "time": slot}
            BOOKINGS.append(booking)
            print(f"BOOKING CONFIRMED: {faculty} on {day} at {slot}.")
            print("Reasoning: first candidate satisfying all CSP constraints was selected.")
            return
        print(f"Backtracking: {slot} is invalid or already booked; trying next slot...")
    print("No available slot on that day. Please choose another day.")


def show_ontology():
    print("\n--- COLLEGE ONTOLOGY (ENTITIES + RELATIONSHIPS) ---")
    for entity, relations in ONTOLOGY.items():
        print(f"{entity}: {relations}")
    print("\nReasoning example: 'marks' -> Result -> related to Exam -> examination cell.")


def run_tests():
    tests = [
        ("What are the college timings?", True),
        ("Tell me about tuition fees", True),
        ("How can I apply for hostel accommodation?", True),
        ("When is the semester exam timetable?", True),
        ("Where do I get placement updates?", True),
        ("How do I check attendance?", True),
        ("Can I borrow a book from the library?", True),
        ("How can I apply for scholarship?", True),
        ("Where can I find the college bus route?", True),
        ("How do I apply for leave?", True),
        ("Who is the HOD?", True),
        ("How can I contact my professor?", True),
        ("Which courses are available?", True),
        ("What is the admission process?", True),
        ("I lost my ID card", True),
        ("College WiFi is not working", True),
        ("When are lab hours?", True),
        ("When will results be announced?", True),
        ("How to get a bonafide certificate?", True),
        ("What are canteen timings?", True),
        ("I need to reset my password", True),
        ("How do I report ragging?", True),
        ("Where is the sports ground?", True),
        ("Is tomorrow a holiday?", True),
        ("How can I meet a counsellor?", True),
        ("I want to book a faculty appointment", True),
        ("Who handles hostel fees?", True),
        ("Who handles semester results?", True),
        ("Where can I ask about job interviews?", True),
        ("What is the process for transcript certificate?", True),
    ]
    keyword_correct = ontology_correct = 0
    print("\n--- 30-QUESTION TEST: KEYWORD MATCHING VS ONTOLOGY ---")
    for i, (question, expected_known) in enumerate(tests, 1):
        _, _, k_topic = keyword_answer(question)
        _, _, o_topic, _ = ontology_answer(question)
        k_ok = (k_topic != "Human escalation") == expected_known
        o_ok = (o_topic != "Human escalation") == expected_known
        keyword_correct += int(k_ok)
        ontology_correct += int(o_ok)
        print(f"{i:02}. {question}")
        print(f"    Keyword: {'PASS' if k_ok else 'MISS'} ({k_topic}) | Ontology: {'PASS' if o_ok else 'MISS'} ({o_topic})")
    print(f"\nKeyword matching coverage: {keyword_correct}/30 = {keyword_correct / 30 * 100:.1f}%")
    print(f"Ontology-enhanced coverage: {ontology_correct}/30 = {ontology_correct / 30 * 100:.1f}%")
    print("Note: this is a small built-in demonstration test set, not an independent benchmark.")


def chatbot():
    print("\n--- COLLEGE FAQ CHATBOT ---")
    print("Ask about fees, timings, hostel, exams, placements, attendance, etc.")
    print("Type 'ontology', 'book', 'tests', or 'exit'.")
    while True:
        question = input("\nYou: ").strip()
        if not question:
            continue
        command = question.lower().strip()
        if command in ("exit", "quit", "bye"):
            print("Bot: Thank you! Goodbye.")
            break
        if command == "ontology":
            show_ontology()
            continue
        if command == "book":
            book_appointment()
            continue
        if command == "tests":
            run_tests()
            continue
        answer, confidence, topic, explanation = ontology_answer(question)
        print(f"Bot [{topic} | confidence {confidence:.0%}]: {answer}")
        print(f"Reason: {explanation}")
        if confidence < 0.45:
            print("Escalation: Please contact the college help desk for verified information.")


if __name__ == "__main__":
    print("=" * 68)
    print(" RULE-BASED COLLEGE FAQ BOT")
    print(" Ontology-Driven Campus Help-Desk Agent | Symbolic AI")
    print("=" * 68)
    print("Features: 20+ FAQs | Ontology | CSP booking | Backtracking | 30 tests")
    chatbot()
