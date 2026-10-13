# College-HelpDesk-Agent

## 1. Project Description
College HelpDesk Agent is a Python-based, rule-based chatbot that helps students get answers to common college-related questions. It uses predefined rules and ontology-based relationships to provide relevant responses.

## 2. Objectives
- To provide quick answers to college FAQs.
- To reduce the effort required to find college information.
- To demonstrate symbolic AI and rule-based reasoning.
- To support faculty appointment booking using CSP and backtracking.

## 3. Technologies Used
- **Programming Language:** Python
- **Concepts:** Rule-Based System, Symbolic AI, Ontology
- **Algorithms:** Keyword Matching, Constraint Satisfaction Problem (CSP), Backtracking
- **Tools:** VS Code, Git, GitHub

## 4. Features
- Answers 20+ categories of college-related FAQs.
- Uses ontology to connect related concepts.
- Provides a fallback response for unknown questions.
- Supports faculty appointment booking using predefined time slots.
- Includes 30 built-in test questions to compare keyword matching and ontology-enhanced matching.

## 5. How It Works
1. The user enters a question.
2. The chatbot processes the question and matches keywords with predefined rules.
3. Ontology-based relationships expand related concepts.
4. The chatbot displays the answer, topic, confidence score, and reasoning.
5. Unknown questions receive a fallback response.

## 6. Installation and Execution

**Prerequisite:** Python 3 installed.

Clone the repository:

```bash
git clone https://github.com/kamalikamali60291-max/College-HelpDesk-Agent.git
```

Open the project folder:

```bash
cd College-HelpDesk-Agent
```

Run the program:

```bash
python college_helpdesk.py
```

## 7. Available Commands
- `ontology` – Displays college entities and relationships.
- `book` – Starts faculty appointment booking.
- `tests` – Runs the 30-question demonstration test.
- `exit` – Exits the chatbot.

## 8. Testing
The project includes 30 predefined questions to compare basic keyword matching with ontology-enhanced matching. The test output reports topic-recognition coverage for both approaches.

## 9. Future Enhancements
- Add a graphical or web-based interface.
- Connect a database for college information.
- Improve natural-language understanding.
- Integrate verified, real-time college information.

## 10. Conclusion
College HelpDesk Agent demonstrates how Python, rule-based reasoning, ontology, and constraint-based appointment booking can be combined to build a simple campus assistance system.
