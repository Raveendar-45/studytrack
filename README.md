# StudyTrack — Unified Full-Stack Study Management Platform

StudyTrack is a single, unified full-stack application built for **Myntra’s internal Trainee Enablement team**. It seamlessly integrates live Student and Course roster CRUD management over a SQLite database, a hand-rolled algorithm engine (Insertion Sort, Iterative Binary Search, Roster Aggregations), and an offline AI Study Assistant (Note Summarizer, 12-Word Vocabulary Vector Embedding & Cosine Similarity Search) into a single dashboard.

---

## 🏛 Architecture & Run Mode Selection

StudyTrack operates under **Single-Process Mode** (Recommended):
- **Backend**: FastAPI + SQLAlchemy ORM running on Uvicorn.
- **Frontend**: Plain HTML5, CSS Box Model stylesheet, and vanilla JavaScript (`app.js`) using event delegation.
- **Static Mounting**: `frontend/` is mounted as static files directly into FastAPI (`app.mount("/", StaticFiles(directory="frontend", html=True), name="static")`) after API routes registration.
- **Same-Origin Access**: Navigating to `http://localhost:8000/` serves the live dashboard, and all fetch calls in `app.js` use relative endpoints (e.g., `/students/`, `/assistant/summarize`).
- **CORS Configuration**: Explicitly configured via `CORSMiddleware` to allow local origins `http://localhost:5500` and `http://localhost:8000`. Wildcard `"*"` is **never** used.

---

## 📁 Repository Structure

```text
studytrack/
├── backend/
│   ├── main.py            # FastAPI app, routes, CORS, static file mount, startup seeding
│   ├── database.py        # SQLAlchemy engine, sessionmaker, declarative base & DB dependency
│   ├── models.py          # Student and Course ORM models with relationship & constraints
│   ├── schemas.py         # Pydantic request/response schemas with field validation
│   ├── crud.py            # Database CRUD functions & func.count course aggregator
│   ├── algorithms.py      # Hand-rolled Insertion Sort, Binary Search, & Roster Report
│   ├── ai_service.py      # Note Summarizer, 12-word vocabulary embedder & Cosine Similarity
│   ├── seed_data.py       # Seed dataset & startup database auto-seeding
│   ├── test_main.py       # Automated Pytest suite covering all endpoints & edge cases
│   └── requirements.txt   # Backend Python dependencies
├── frontend/
│   ├── index.html         # Dashboard HTML structure with semantic tags & AI Helper panel
│   ├── style.css          # CSS Box Model styling, modern glassmorphic theme & max-width 600px media query
│   └── app.js             # Vanilla JS dashboard logic with event delegation & relative fetch calls
├── .env.example           # Example environment configuration (AI_MODE=mock)
├── .gitignore             # Git exclusion rules for .env, SQLite DB, __pycache__, and venv
└── README.md              # Complete platform documentation & complexity analysis
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup & Dependency Installation

Ensure Python 3.10+ is installed on your system.

```bash
# Clone the repository
git clone https://github.com/Raveendar-45/studytrack.git
cd studytrack

# Install backend dependencies
python -m pip install -r backend/requirements.txt
```

### 2. Running the Application (Single-Process Mode)

Execute the Uvicorn server from the repository root:

```bash
python -m uvicorn backend.main:app --port 8000 --reload
```

- **Live Dashboard**: Open your browser at `http://localhost:8000/`
- **Interactive API Documentation (Swagger UI)**: Open `http://localhost:8000/docs`

---

## 🧪 Running Automated Verification Tests

StudyTrack includes an automated test suite powered by `pytest` and FastAPI `TestClient`:

```bash
python -m pytest backend/test_main.py
```

All tests pass cleanly, verifying CRUD operations, edge-case validation, algorithm sorting/searching correctness, zero-vector cosine similarity safety, and offline AI note summarization.

---

## 📑 Detailed API Endpoint Reference

### Roster CRUD Endpoints

| Method | Endpoint | Description | Request Body / Params | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/students/` | Creates a new student record | `{"name": str, "email": str, "age": int}` | `201 Created` — Student Object |
| `GET` | `/students/` | Lists all students (with optional `min_age` filter) | Query: `?min_age=20` (Optional) | `200 OK` — List of Student Objects |
| `GET` | `/students/{id}` | Fetches a single student by ID | Path: `id` (int) | `200 OK` or `404 Not Found` |
| `PATCH` | `/students/{id}` | Partial update of student details (e.g. age) | `{"age": int}` (Optional fields) | `200 OK` or `404 Not Found` |
| `DELETE` | `/students/{id}` | Deletes a student record | Path: `id` (int) | `200 OK` `{"detail": "..."}` or `404` |
| `GET` | `/students/{id}/course-count` | Computes student enrolled course count via SQL aggregate | Path: `id` (int) | `200 OK` `{"student_id": int, "course_count": int}` |
| `POST` | `/courses/` | Enrolls student in a course (credits 1–6) | `{"course_name": str, "credits": int, "student_id": int}` | `201 Created` — Course Object |
| `GET` | `/courses/` | Lists all course enrollments | None | `200 OK` — List of Course Objects |
| `GET` | `/courses/{id}` | Fetches a single course enrollment | Path: `id` (int) | `200 OK` or `404 Not Found` |
| `PATCH` | `/courses/{id}` | Partial update of course enrollment | `{"credits": int}` | `200 OK` or `404 Not Found` |
| `DELETE` | `/courses/{id}` | Deletes a course enrollment | Path: `id` (int) | `200 OK` or `404 Not Found` |

*Note on `course-count` implementation*: The `/students/{id}/course-count` endpoint computes enrollments via a database-level aggregate query in `crud.py` (`db.query(func.count(models.Course.id)).filter(models.Course.student_id == student_id).scalar()`), rather than loading rows into Python memory.

### Integrated Algorithms Engine Endpoints

| Method | Endpoint | Description | Query Parameters | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/students/sorted` | Hand-rolled in-place Insertion Sort | `?by=age` or `?by=name` (Default: `age`) | `200 OK` — Sorted Student List |
| `GET` | `/students/search` | Hand-rolled iterative Binary Search | `?name=Priya Iyer` (Exact match) | `200 OK` Student dict or `404 Not Found` |
| `GET` | `/students/report` | Roster report text & min_age count accumulator | `?min_age=21` (Default: `21`) | `200 OK` `{"report": str, "count_meeting_min_age": int}` |

### Integrated AI Assistant Endpoints

| Method | Endpoint | Description | Request / Query | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/assistant/summarize` | Deterministic study note summarizer | Body: `{"text": str}` | `200 OK` `{"topic": str, "key_points": list, "difficulty": str}` |
| `GET` | `/assistant/search` | Vocabulary embedding & Cosine Similarity search | Query: `?query=binary search` | `200 OK` — List of ranked note objects with `score` |

---

## 🧮 Part 2 — Complexity Analysis & Theoretical Foundation

### 1. Insertion Sort Complexity ($O(n^2)$ Worst Case vs $O(n)$ Best Case)
Hand-rolled in `backend/algorithms.py` via `insertion_sort_by_field(students, field)`:
- **Worst-Case Time Complexity — $O(n^2)$**: Occurs when the student roster is initially sorted in reverse order relative to the desired sorting field (e.g., sorting by age ascending when ages are in descending order). For each element at index $i$, the inner `while` loop must shift all $i$ preceding elements to the right. The total number of shifts equals the sum of the first $n-1$ integers: $\sum_{i=1}^{n-1} i = \frac{n(n-1)}{2} = \frac{n^2 - n}{2}$, yielding quadratic complexity $O(n^2)$.
- **Best-Case Time Complexity — $O(n)$**: Occurs when the roster is already sorted in ascending order by the target field. For every outer loop iteration $i$, the key element is immediately compared to `students[i-1]`. Because `students[i-1][field] <= key[field]`, the inner `while` loop condition fails on the very first evaluation. Thus, exactly 1 comparison and 0 element shifts occur per item, resulting in $n-1$ total comparisons and linear time complexity $O(n)$.

### 2. Binary Search Prerequisites (Sorted Precondition)
Hand-rolled in `backend/algorithms.py` via `binary_search_by_name(sorted_by_name_list, name)`:
- Iterative Binary Search relies on the invariant of **monotonic ordering**. At each step, the algorithm computes the midpoint index `mid = low + (high - low) // 2` and compares `sorted_by_name_list[mid]["name"]` against the target `name`.
- If the roster were not strictly sorted alphabetically prior to execution, comparing the midpoint target would give false directional information. An unsorted array invalidates the assumption that all elements to the left of `mid` are smaller and all elements to the right are larger. Consequently, discarding half the search space could eliminate the target element even if present, leading to incorrect search failures. Hence, sorting by the search key (`sorted(students, key=lambda s: s['name'])`) is a mandatory prerequisite.

---

## 🤖 Part 3 — Integrated AI Assistant & Structured Prompting

### Offline Mock Mode (`AI_MODE=mock`)
By default, StudyTrack runs in **100% offline mock mode**, requiring **zero network calls, zero external API keys, and zero account setups**:
1. **Note Summarizer (`summarize_notes`)**:
   - **Topic**: Derived from the clean first non-empty line (up to 60 chars) or defaults to `"untitled"` for empty input.
   - **Key Points**: Extracted by splitting text into sentences on `.`, `!`, `?` taking up to 3 non-empty stripped strings. Empty input produces `[]`.
   - **Difficulty**: Word count threshold (< 40 words $\rightarrow$ `"easy"`, 40–100 words $\rightarrow$ `"medium"`, > 100 words $\rightarrow$ `"hard"`).
   - **Empty Input Safety**: Calling `summarize_notes("")` returns `{"topic": "untitled", "key_points": [], "difficulty": "easy"}` without throwing any exception.
2. **Vocabulary Embedding (`mock_embed`) & Cosine Similarity (`cosine_similarity`)**:
   - Vectorizes text against a fixed 12-word vocabulary: `["sort", "search", "binary", "insertion", "sql", "join", "fastapi", "pydantic", "prompt", "llm", "database", "validate"]`.
   - Lowercases input string and tokenizes by non-alphanumeric separators. Counts exact whole-token frequency matches.
   - Cosine Similarity computes $\frac{\vec{a} \cdot \vec{b}}{\|\vec{a}\| \|\vec{b}\|}$. If either vector magnitude is 0.0 (e.g. empty or out-of-vocabulary query), it directly returns `0.0` to eliminate `ZeroDivisionError`.

### Optional Real LLM Mode & Structured Prompt Design (`AI_MODE=real`)
If connected to a live LLM endpoint (e.g., OpenAI / Gemini / Anthropic), the following **Structured Role Prompt** is used to guarantee the exact JSON schema:

```text
System: You are an expert educational assistant for Myntra Trainee Enablement.
Task: Summarize the provided raw study notes and evaluate their difficulty.

Constraints:
1. You MUST respond with valid JSON containing EXACTLY three keys: "topic", "key_points", and "difficulty".
2. "topic": A concise 3 to 6 word title summarizing the central theme.
3. "key_points": A JSON array of 1 to 3 distinct bullet points summarizing key concepts.
4. "difficulty": Exactly one of "easy", "medium", or "hard" based on conceptual complexity and length.
5. Do NOT include markdown code fences (e.g. ```json), introductory text, or explanations outside the JSON object.

User Input:
<raw_study_notes>
```

---

## 🕹 Step-by-Step Dashboard Walkthrough & Log Verification

Below is an end-to-end walkthrough demonstrating all features running seamlessly in a single app instance:

1. **Dashboard Initialization**:
   - Open `http://localhost:8000/`.
   - The frontend executes `GET /students/` on load. The database automatically seeds the 9 initial student records (Aditi Rao, Rohan Mehta, Kavya Nair, Farhan Sheikh, Priya Iyer, Devansh Gupta, Meera Joshi, Sameer Khan, Ananya Sharma).
   - Backend log: `INFO: 127.0.0.1:54321 - "GET /students/ HTTP/1.1" 200 OK`

2. **Inline Age Update (Event Delegation)**:
   - On Priya Iyer's student card, change age input to `19` and click **"Save Age"**.
   - Event delegation on `#roster-list` catches the event and triggers `PATCH /students/5`.
   - Backend log: `INFO: 127.0.0.1:54321 - "PATCH /students/5 HTTP/1.1" 200 OK`

3. **Student Record Creation**:
   - Fill the **Student Roster Management** form: Name: `Vikram Verma`, Email: `vikram.verma@example.com`, Age: `22`. Click **"Add Student"**.
   - Sends `POST /students/`. A new card appears dynamically at the end of the roster list without reloading the page.
   - Backend log: `INFO: 127.0.0.1:54321 - "POST /students/ HTTP/1.1" 201 Created`

4. **Insertion Sort Algorithm**:
   - Click **"Sort by Age (Asc)"** under the Algorithms Engine section.
   - Triggers `GET /students/sorted?by=age`. The roster updates in-place ordered by age.
   - Backend log: `INFO: 127.0.0.1:54321 - "GET /students/sorted?by=age HTTP/1.1" 200 OK`

5. **Binary Search Algorithm**:
   - Enter `Priya Iyer` into the Binary Search input and click **"Search"**.
   - Triggers `GET /students/search?name=Priya%20Iyer`. The green match card displays Priya Iyer's record details.
   - Backend log: `INFO: 127.0.0.1:54321 - "GET /students/search?name=Priya%20Iyer HTTP/1.1" 200 OK`

6. **AI Helper Note Summarizer**:
   - Paste text: `"FastAPI uses Pydantic models to validate request bodies and automatically generates Swagger documentation."`
   - Click **"Summarize Notes"**.
   - Sends `POST /assistant/summarize`. Renders topic, difficulty badge (`easy`), and key points.
   - Backend log: `INFO: 127.0.0.1:54321 - "POST /assistant/summarize HTTP/1.1" 200 OK`

---

## 📜 License & Originality

This repository is submitted as a single, original work for **Myntra Trainee Enablement**. All code, algorithms, and documentation are original implementations.
