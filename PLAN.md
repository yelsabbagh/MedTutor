\## Recommended capstone idea 🧠



\### \*\*Project title\*\*



\*\*MedTutor Agent: A Multi-Agent Medical Exam Coach from Lecture PDFs\*\*



\### \*\*Best track\*\*



\*\*Agents for Good\*\* — because it supports education and helps medical students convert dense lecture material into interactive, exam-style study sessions.



Kaggle says the capstone should solve a real-world problem, automate or assist useful workflows, and demonstrate practical value through agent design. Your project fits that well because it turns static medical lectures into MCQs, OSCE cases, explanations, and revision plans. 



\---



\# 1. Core project idea



\## Problem



Medical students often have lecture PDFs but do not know:



\* what is exam-worthy

\* how to convert passive reading into active recall

\* how to practice OSCE-style clinical questions

\* whether generated questions are medically grounded in the lecture



\## Solution



Build an AI agent system that takes a \*\*medical lecture PDF or pasted lecture text\*\* and produces:



1\. \*\*High-yield topic extraction\*\*

2\. \*\*Exam blueprint\*\*

3\. \*\*MCQs with explanations\*\*

4\. \*\*OSCE case scenarios\*\*

5\. \*\*Interactive oral-question mode\*\*

6\. \*\*Safety/accuracy review\*\*

7\. \*\*Downloadable JSON/Markdown output\*\*



The agent should clearly show that it is not just “one chatbot,” but a structured multi-agent workflow.



\---



\# 2. Why this is a strong capstone idea



Kaggle requires submissions to demonstrate at least \*\*three key course concepts\*\*, such as ADK, MCP server, security features, deployability, and agent skills. 



This project can demonstrate \*\*five\*\*:



| Required concept             | How you demonstrate it                                                     |

| ---------------------------- | -------------------------------------------------------------------------- |

| \*\*Multi-agent system / ADK\*\* | Coordinator agent routes tasks to specialized agents                       |

| \*\*MCP server\*\*               | Local document server exposes lecture search, page retrieval, export tools |

| \*\*Agent skills\*\*             | Reusable skills: MCQ generation, OSCE generation, explanation validation   |

| \*\*Security features\*\*        | Prompt-injection defense, no PHI warning, source-grounded answers          |

| \*\*Deployability\*\*            | Public demo or GitHub repo with setup instructions                         |



This also aligns with the judging rubric: the project needs strong problem definition, clear architecture, implementation quality, useful agents, documentation, and a concise video demo. 



\---



\# 3. MVP version to build



Do \*\*not\*\* build a full medical platform. Build a focused demo.



\## MVP user flow



1\. User uploads or selects a sample lecture.

2\. User chooses output mode:



&#x20;  \* MCQ test

&#x20;  \* OSCE oral exam

&#x20;  \* High-yield summary

&#x20;  \* Study plan

3\. Coordinator agent analyzes the request.

4\. Retrieval agent extracts relevant lecture sections.

5\. Exam agent generates questions.

6\. Validator agent checks:



&#x20;  \* answer correctness

&#x20;  \* option quality

&#x20;  \* whether the explanation is grounded in the lecture

7\. Export agent returns:



&#x20;  \* Markdown

&#x20;  \* JSON

&#x20;  \* optional CSV



\---



\# 4. Agent architecture



\## Main agents



\### 1. \*\*Coordinator Agent\*\*



Controls the workflow.



Responsibilities:



\* receives user request

\* detects task type

\* calls the correct sub-agents

\* assembles final output



Example prompt role:



> “You are the coordinator. Decide whether the user needs MCQs, OSCE cases, summaries, or validation. Route the task to the correct agent.”



\---



\### 2. \*\*Lecture Retrieval Agent\*\*



Finds relevant content inside the uploaded lecture.



Responsibilities:



\* chunk lecture text

\* retrieve sections by topic

\* return citations/page references

\* prevent hallucinated topics outside the material



Tools:



\* `search\_lecture(query)`

\* `get\_chunk(chunk\_id)`

\* `list\_topics()`



\---



\### 3. \*\*Exam Blueprint Agent\*\*



Turns lecture content into an exam map.



Outputs:



```json

{

&#x20; "main\_topics": \[],

&#x20; "high\_yield\_facts": \[],

&#x20; "clinical\_conditions": \[],

&#x20; "possible\_exam\_angles": \[],

&#x20; "difficulty\_distribution": {

&#x20;   "easy": 20,

&#x20;   "moderate": 60,

&#x20;   "hard": 20

&#x20; }

}

```



\---



\### 4. \*\*MCQ Generator Agent\*\*



Creates clinical MCQs.



Rules:



\* 5 options

\* one best answer

\* close distractors

\* explanation for every option

\* exam-oriented wording



Output example:



```json

{

&#x20; "question": "A 62-year-old man presents with progressive dyspnea...",

&#x20; "a": "Bronchial asthma",

&#x20; "b": "COPD",

&#x20; "c": "Pulmonary embolism",

&#x20; "d": "Pneumonia",

&#x20; "e": "Heart failure",

&#x20; "correct\_answer": "B",

&#x20; "explanations": {

&#x20;   "a": "...",

&#x20;   "b": "...",

&#x20;   "c": "...",

&#x20;   "d": "...",

&#x20;   "e": "..."

&#x20; }

}

```



\---



\### 5. \*\*OSCE Examiner Agent\*\*



Creates interactive case-based oral exam stations.



Example output:



```markdown

\## OSCE Station: Acute Dyspnea



\### Stem

A 55-year-old smoker presents with progressive shortness of breath and cough.



\### Examiner Questions

1\. What is your most likely diagnosis?

2\. What history points support it?

3\. What investigations would you request?

4\. What is the initial management?



\### Expected Answers

...

```



\---



\### 6. \*\*Medical Safety Validator Agent\*\*



This is important for credibility.



Responsibilities:



\* checks if the MCQ has more than one possible correct answer

\* flags vague stems

\* flags unsupported claims

\* checks if answer explanation is grounded in the source lecture

\* adds disclaimer: educational use only, not medical advice



This agent gives the project a stronger “responsible AI” angle.



\---



\### 7. \*\*Export Agent\*\*



Creates final downloadable files:



\* `questions.json`

\* `mcqs.md`

\* `osce\_cases.md`

\* `study\_plan.md`



\---



\# 5. MCP server design



Create a simple local MCP-style tool server that exposes document and export tools.



\## Tools to expose



```python

search\_lecture(query: str) -> list

get\_lecture\_chunk(chunk\_id: str) -> str

generate\_output\_file(filename: str, content: str) -> str

validate\_no\_phi(text: str) -> dict

```



\## Why MCP matters here



The agent should not directly “know everything.” It uses tools to:



\* retrieve lecture content

\* validate user input

\* save outputs

\* keep the workflow auditable



This makes the agent architecture more judge-friendly than a basic chatbot.



\---



\# 6. Security features to include



Kaggle explicitly reminds participants not to include API keys or passwords in code. 



Add these features:



\## A. No secrets in repo



Use:



```bash

.env.example

```



Never upload:



```bash

.env

```



Example:



```env

GOOGLE\_API\_KEY=your\_key\_here

```



\---



\## B. Prompt-injection defense



When reading uploaded lecture text, add a guard:



```python

SUSPICIOUS\_PATTERNS = \[

&#x20;   "ignore previous instructions",

&#x20;   "reveal system prompt",

&#x20;   "send api key",

&#x20;   "disable safety",

&#x20;   "act as developer"

]

```



If detected, the validator warns:



```json

{

&#x20; "risk": "prompt\_injection",

&#x20; "action": "ignored suspicious instruction inside document"

}

```



\---



\## C. Medical safety boundary



Add a fixed disclaimer:



> This tool is for medical education and exam preparation only. It does not provide diagnosis, treatment, or patient-specific medical advice.



\---



\## D. PHI filter



Warn users not to upload real patient data.



Detect possible PHI:



\* names

\* phone numbers

\* addresses

\* national IDs

\* hospital numbers



\---



\# 7. Recommended tech stack



\## Backend



\* \*\*Python\*\*

\* \*\*Google Agent Development Kit / ADK\*\*

\* \*\*Gemini API\*\*

\* \*\*FastAPI\*\*

\* \*\*MCP-style tool server\*\*

\* \*\*PyMuPDF or pdfplumber\*\* for PDF parsing

\* \*\*FAISS or Chroma\*\* for simple retrieval



\## Frontend



Use the fastest option:



\* \*\*Streamlit\*\* for demo

&#x20; or

\* \*\*Gradio\*\* for interactive public app



For a capstone, Streamlit is enough.



\## Repo structure



```text

medtutor-agent/

│

├── app.py

├── README.md

├── requirements.txt

├── .env.example

│

├── agents/

│   ├── coordinator\_agent.py

│   ├── retrieval\_agent.py

│   ├── blueprint\_agent.py

│   ├── mcq\_agent.py

│   ├── osce\_agent.py

│   ├── validator\_agent.py

│   └── export\_agent.py

│

├── tools/

│   ├── lecture\_tools.py

│   ├── export\_tools.py

│   └── security\_tools.py

│

├── sample\_data/

│   └── sample\_respiratory\_lecture.txt

│

├── outputs/

│   ├── sample\_mcqs.json

│   ├── sample\_osce\_cases.md

│   └── sample\_study\_plan.md

│

└── assets/

&#x20;   └── architecture\_diagram.png

```



\---



\# 8. Implementation plan



\## Phase 1 — Build the basic document pipeline



\### Goal



Convert a lecture PDF or pasted text into structured chunks.



\### Tasks



\* Add upload box in Streamlit.

\* Extract text.

\* Split text into chunks.

\* Store chunks with IDs.

\* Add a simple search function.



Example chunk object:



```json

{

&#x20; "chunk\_id": "chunk\_001",

&#x20; "source": "lecture.pdf",

&#x20; "page": 3,

&#x20; "text": "COPD is characterized by persistent airflow limitation..."

}

```



\---



\## Phase 2 — Add the multi-agent workflow



\### Goal



Create specialized agents instead of one large prompt.



\### Agents to implement first



1\. Coordinator Agent

2\. Retrieval Agent

3\. MCQ Generator Agent

4\. Validator Agent

5\. Export Agent



\### Basic workflow



```text

User request

&#x20;  ↓

Coordinator Agent

&#x20;  ↓

Retrieval Agent

&#x20;  ↓

MCQ Generator Agent

&#x20;  ↓

Validator Agent

&#x20;  ↓

Export Agent

&#x20;  ↓

Final answer + downloadable file

```



\---



\## Phase 3 — Add OSCE mode



\### Goal



Make the project more differentiated.



Many people will build generic assistants. OSCE mode makes yours medically specific and more useful.



\### OSCE output



Each case should include:



\* station title

\* clinical stem

\* examiner questions

\* expected answers

\* common mistakes

\* scoring checklist



\---



\## Phase 4 — Add safety layer



\### Goal



Demonstrate responsible agent design.



\### Add checks for:



\* prompt injection

\* unsupported medical claims

\* multiple correct answers

\* PHI

\* missing explanation

\* weak distractors



Example validator output:



```json

{

&#x20; "valid": false,

&#x20; "issues": \[

&#x20;   "Option B and D may both be correct.",

&#x20;   "Explanation for option C is not grounded in the lecture."

&#x20; ],

&#x20; "suggested\_fix": "Make option D less clinically compatible."

}

```



\---



\## Phase 5 — Build the demo UI



\## Required screens



\### Screen 1 — Upload lecture



User uploads PDF or uses sample lecture.



\### Screen 2 — Choose task



Options:



\* Generate MCQs

\* Generate OSCE cases

\* Generate study blueprint

\* Validate existing MCQs



\### Screen 3 — Agent trace



Show something like:



```text

✅ Coordinator Agent selected MCQ workflow

✅ Retrieval Agent found 6 relevant chunks

✅ MCQ Agent generated 10 questions

✅ Validator Agent fixed 3 weak distractors

✅ Export Agent created questions.json

```



This is important because judges need to see the agent system working.



\### Screen 4 — Output



Show:



\* questions

\* explanations

\* source references

\* download buttons



\---



\# 9. Demo video structure



The video must be \*\*5 minutes or less\*\* and uploaded to YouTube. 



Use this structure:



| Segment   | Content                                                            |

| --------- | ------------------------------------------------------------------ |

| 0:00–0:30 | Problem: medical students have PDFs but need active exam practice  |

| 0:30–1:00 | Solution: MedTutor Agent                                           |

| 1:00–1:45 | Architecture diagram: coordinator + specialized agents + MCP tools |

| 1:45–3:30 | Live demo: upload lecture → generate MCQs → validate → export      |

| 3:30–4:20 | Security: prompt injection defense, PHI warning, grounded answers  |

| 4:20–5:00 | Impact and future work                                             |



\---



\# 10. Kaggle Writeup outline



Your Kaggle writeup must include title, subtitle, and detailed analysis, with a maximum of \*\*2,500 words\*\*. 



\## Suggested writeup title



\*\*MedTutor Agent: A Multi-Agent Medical Exam Coach for Lecture-Based Learning\*\*



\## Subtitle



\*\*Transforming passive medical lectures into grounded MCQs, OSCE cases, and active recall workflows using ADK-style agents and MCP tools.\*\*



\## Writeup sections



```markdown

\# 1. Problem

Medical students often study from dense lecture PDFs...



\# 2. Solution

MedTutor Agent converts lecture material into active exam practice...



\# 3. Why Agents?

A single chatbot is not enough because exam generation requires retrieval, reasoning, validation, and formatting...



\# 4. Architecture

Include diagram and explain each agent.



\# 5. Key Course Concepts Demonstrated

\- Multi-agent system

\- MCP tools

\- Security features

\- Deployability

\- Agent skills



\# 6. Demo Workflow

Upload lecture → choose mode → generate → validate → export.



\# 7. Safety and Responsible AI

Educational-only disclaimer, PHI warning, prompt-injection filter.



\# 8. Future Work

Spaced repetition, multilingual output, Anki export, curriculum mapping.

```



\---



\# 11. Public project link requirement



Kaggle requires a public project link or public repo with setup instructions. 



Your safest option:



\* public GitHub repo

\* clear README

\* screenshots

\* sample input

\* sample output

\* `.env.example`

\* no real API keys



A live demo is useful, but not mandatory if the repo is complete and reproducible.



\---



\# 12. README checklist



Your README should include:



```markdown

\# MedTutor Agent



\## Problem



\## Solution



\## Architecture



\## Agents



\## MCP Tools



\## Security Features



\## Installation



\## Running Locally



\## Demo



\## Sample Outputs



\## Limitations



\## Future Work

```



Add this command:



```bash

pip install -r requirements.txt

streamlit run app.py

```



Add `.env.example`:



```env

GOOGLE\_API\_KEY=your\_google\_api\_key\_here

```



\---



\# 13. Architecture diagram text



Use this in your diagram:



```text

&#x20;               ┌────────────────────┐

&#x20;               │      User UI        │

&#x20;               │ Streamlit / Gradio  │

&#x20;               └─────────┬──────────┘

&#x20;                         │

&#x20;                         ▼

&#x20;               ┌────────────────────┐

&#x20;               │ Coordinator Agent   │

&#x20;               └─────────┬──────────┘

&#x20;                         │

&#x20;    ┌────────────────────┼────────────────────┐

&#x20;    ▼                    ▼                    ▼

┌──────────────┐   ┌──────────────┐   ┌────────────────┐

│ Retrieval    │   │ Exam Builder │   │ OSCE Examiner  │

│ Agent        │   │ Agent        │   │ Agent          │

└──────┬───────┘   └──────┬───────┘   └───────┬────────┘

&#x20;      │                  │                   │

&#x20;      ▼                  ▼                   ▼

┌──────────────────────────────────────────────────────┐

│                MCP Tool Server                        │

│ search\_lecture | get\_chunk | validate\_phi | export    │

└──────────────────────────────────────────────────────┘

&#x20;                         │

&#x20;                         ▼

&#x20;               ┌────────────────────┐

&#x20;               │ Validator Agent     │

&#x20;               └─────────┬──────────┘

&#x20;                         ▼

&#x20;               ┌────────────────────┐

&#x20;               │ Final Output        │

&#x20;               │ JSON / MD / CSV     │

&#x20;               └────────────────────┘

```



\---



\# 14. What to submit



Your valid submission needs:



\* \*\*Kaggle Writeup\*\*

\* \*\*Media Gallery\*\*

\* \*\*YouTube video\*\*

\* \*\*Public project link\*\*

&#x20; These are explicitly required for eligibility. 



Also remember the deadline: \*\*July 6, 2026 at 11:59 PM PT\*\*. 



\---



\# Final recommendation



Build \*\*MedTutor Agent\*\*.



It is better than a generic productivity agent because it has:



\* a clear real-world problem

\* strong personal fit with your medical exam workflow

\* obvious social value under \*\*Agents for Good\*\*

\* easy-to-demo input/output

\* natural multi-agent architecture

\* strong safety story

\* strong documentation potential



The winning angle is:



> “This is not just an AI quiz generator. It is a responsible multi-agent medical study system that retrieves lecture evidence, generates exam material, validates correctness, and exports structured study assets.”



