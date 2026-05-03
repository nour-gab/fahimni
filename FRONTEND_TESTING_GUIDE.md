# Frontend Testing Guide

Complete walkthrough to test the Fahimni frontend with seeded demo data, student/professor dashboards, and AI workflows.

---

## Prerequisites & Setup

### 1. Start the Backend Server

Open a terminal and run:

```bash
cd c:\Users\gaboussa\Documents\Projects\Fahimni
uv run uvicorn fahimni.main:app --reload --reload-dir src
```

**Expected output:**
```
INFO:     Started server process [PID]
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

✅ **Verify:** Open `http://localhost:8000/health` in browser → Should see `{"status":"ok"}`

---

### 2. Start the Frontend Dev Server

Open a new terminal and run:

```bash
cd c:\Users\gaboussa\Documents\Projects\Fahimni\frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in XX ms

➜  Local:   http://localhost:5173/
➜  Press h + enter to show help
```

✅ **Verify:** Navigate to `http://localhost:5173` → Landing page loads with animations

---

## Demo Credentials & Data

| Role       | Email                      | Password       |
|-----------|----------------------------|-----------------|
| Professor | professor.demo@fahimni.com | demo-password  |
| Student   | student.demo@fahimni.com   | demo-password  |

**Course:** FAH-101 (Foundations of Algorithms)

**Pre-seeded Resources:**
- Material: Demo Algorithm Notes (ID: `dc5b3120-76e7-44ec-9ad7-8f3e95884803`)
- Archive: Demo Midterm 2025 (ID: `ef549ee4-9d0d-4120-a050-ea1af066ca4e`)

---

# Test Flows

## Phase 1: Landing Page & Auth

### 1.1 Landing Page Verification

**Steps:**
1. Navigate to `http://localhost:5173`
2. Observe the landing page layout:
   - ✅ Navigation bar (sticky, with Fahimni branding)
   - ✅ Hero section (title + subtitle + CTA buttons)
   - ✅ About section (paragraph describing Fahimni)
   - ✅ Features cards (6 cards: Smart Learning Paths, RAG Q&A, Quiz Engine, Archive Intelligence, Collaboration, Personalization)
   - ✅ Call-to-action footer section
3. Verify animations (fade-ins, slide-ups, hover effects on cards)
4. Click **"Get Started"** button

**Expected result:** Navigates to login screen

---

### 1.2 Professor Login

**Steps:**
1. On the login screen, enter:
   - **Email:** `professor.demo@fahimni.com`
   - **Password:** `demo-password`
2. Click **"Login"** button
3. Wait for redirect and dashboard load

**Expected result:**
- ✅ JWT token stored in localStorage/cookies
- ✅ Redirect to dashboard page
- ✅ Page shows "Professor Dashboard" or similar header
- ✅ Navigation bar shows logout option + professor name

**If auth fails:**
- Check backend logs for error details
- Verify `/auth/login` endpoint works: `curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"professor.demo@fahimni.com","password":"demo-password"}'`

---

## Phase 2: Professor Dashboard

### 2.1 Dashboard Overview

**Expected elements on Professor Dashboard:**

✅ **Courses Panel**
- Should show **"FAH-101: Foundations of Algorithms"**
- Course code visible
- Option to click/navigate to course details

✅ **Quick Stats** (if implemented)
- Number of enrolled students (should be 1: Demo Student)
- Materials uploaded (should be 1: Demo Algorithm Notes)
- Archives added (should be 1: Demo Midterm 2025)

✅ **Recent Activity** (if implemented)
- Learning events from student (should show recursion question event)
- Latest material uploads

---

### 2.2 Access Course Details

**Steps:**
1. Click on **"FAH-101"** course card
2. Should navigate to course detail page

**Expected to see:**
- ✅ Course title: "Foundations of Algorithms"
- ✅ Course code: FAH-101
- ✅ Course description: "A demo course used to exercise the AI workflow against seeded content."
- ✅ Tab or section: **Materials**
- ✅ Tab or section: **Archives** (Exams, TDs, Summaries)
- ✅ Tab or section: **Students** (list with Demo Student)
- ✅ Tab or section: **Announcements** (empty initially)

---

### 2.3 View Materials

**Steps:**
1. Click on **"Materials"** tab/section in course detail
2. Should display a list of course materials

**Expected to see:**
- ✅ **"Demo Algorithm Notes"** material entry
- ✅ Material type: "NOTES"
- ✅ Source type: "TEACHER"
- ✅ Year: 2026
- ✅ Verified: ✓ (checkmark/badge)
- ✅ Action buttons: View, Edit, Delete (or similar)

**Click on material** → Should show:
- ✅ Material title and metadata
- ✅ Storage URL (demo://algorithm-notes)
- ✅ Full content preview or link to view

---

### 2.4 View Archive Resources

**Steps:**
1. Click on **"Archives"** tab/section in course detail
2. Should display a list of archive resources (exams, TDs, summaries)

**Expected to see:**
- ✅ **"Demo Midterm 2025"** archive entry
- ✅ Resource type: "EXAM"
- ✅ Year: 2025
- ✅ University: "Fahimni University"
- ✅ Professor: "Demo Professor"
- ✅ Difficulty: "MEDIUM" (badge/label)
- ✅ File URL: demo://midterm-2025.pdf
- ✅ Processed: ✗ (not yet processed)

**Click on archive** → Should show:
- ✅ Archive details and metadata
- ✅ Option to download or view
- ✅ Status: "Pending processing" or similar

---

### 2.5 View Enrolled Students

**Steps:**
1. Click on **"Students"** tab/section in course detail

**Expected to see:**
- ✅ List with **"Demo Student"** (email: student.demo@fahimni.com)
- ✅ Student role/badge
- ✅ Enrollment date
- ✅ Quick actions (view progress, send message, etc.)

**Click on student** → Should show:
- ✅ Student profile and enrolled courses
- ✅ Learning progress/events
- ✅ Grades (empty initially)

---

## Phase 3: Student Dashboard

### 3.1 Logout & Login as Student

**Steps:**
1. Click **"Logout"** button (top right or menu)
2. Redirect to landing page
3. Click **"Get Started"** → Login screen
4. Enter:
   - **Email:** `student.demo@fahimni.com`
   - **Password:** `demo-password`
5. Click **"Login"**

**Expected result:**
- ✅ Redirect to Student Dashboard
- ✅ Different dashboard layout than Professor (student-specific)
- ✅ Navigation shows student name

---

### 3.2 Student Dashboard Overview

**Expected elements on Student Dashboard:**

✅ **Enrolled Courses Panel**
- Should show **"FAH-101: Foundations of Algorithms"**
- Course code and progress indicator (if implemented)

✅ **My Progress** (if implemented)
- Topics studied (should show "recursion" with 72.5% mastery)
- Recent learning events (should show "Recursion question asked")

✅ **Quick Links/Actions**
- Access to course materials
- Access to quizzes/exams
- Link to AI tools (RAG Ask, Learning Path, etc.)

---

### 3.3 Access Enrolled Course

**Steps:**
1. Click on **"FAH-101"** course card

**Expected to see (student view):**
- ✅ Course title: "Foundations of Algorithms"
- ✅ Course description
- ✅ **Materials** tab: "Demo Algorithm Notes" accessible
- ✅ **Archives** tab: "Demo Midterm 2025" accessible
- ✅ **Progress** tab: Mastery score for "recursion" (72.5%)
- ✅ **AI Tools** section or tab (RAG Ask, Learning Path, etc.)

---

### 3.4 View Course Materials (Student View)

**Steps:**
1. Click on **"Materials"** tab
2. Should list "Demo Algorithm Notes"

**Expected to see:**
- ✅ Material title
- ✅ Type: NOTES
- ✅ Created by: "Demo Professor"
- ✅ Preview or view link

**Click on material** → Should display:
- ✅ Content preview or full text
- ✅ No edit/delete options (student read-only)

---

### 3.5 View Learning Progress

**Steps:**
1. Click on **"Progress"** or **"My Progress"** tab

**Expected to see:**
- ✅ Topic: "recursion"
- ✅ Mastery score: 72.5%
- ✅ Last seen: Recently (current date/time)
- ✅ Skill breakdown or mastery gauge

---

## Phase 4: AI Workflow Testing

### 4.1 RAG Q&A (Ask Question)

**Setup:**
- Logged in as **Student** (`student.demo@fahimni.com`)
- On course **FAH-101** page

**Steps:**
1. Look for **"Ask Question"**, **"RAG Ask"**, or **"Ask AI"** button/section
2. Click it → Should open a modal/form
3. Enter question: `Explain recursion and how a base case works`
4. Select course: **FAH-101** (should be pre-selected)
5. Click **"Ask"** button

**Expected result (within 2-5 seconds):**
- ✅ AI answer displayed in modal/panel
- ✅ Answer should reference "recursion" and "base case" concepts
- ✅ Example response: *"Recursion is a technique where a function calls itself to solve smaller instances of the same problem. A recursion base case stops the repeated calls and prevents infinite loops."*
- ✅ Source attribution showing materials/archives used
- ✅ Option to save/export answer

**If no answer appears:**
- Check backend logs for `/api/v1/ai/rag-ask` errors
- Verify ChromaDB is running and indexed content: `curl http://localhost:8001/api/v1` should respond
- Check that `DemoAIService` or `AIService` is initialized

---

### 4.2 Hybrid Search

**Steps:**
1. Look for **"Search"**, **"Hybrid Search"**, or **"Knowledge Search"** option
2. Click it → Open search interface
3. Enter query: `recursion and binary search`
4. Click **"Search"** button

**Expected results (within 2-3 seconds):**

**First result:**
- ✅ Text: *"Recursion is a technique... A recursion base case... Binary search is efficient because it halves the search space..."*
- ✅ Source: "teacher-upload" or "Demo Algorithm Notes"
- ✅ Score: ~1.0 (high relevance)
- ✅ Page: 1
- ✅ Highlight: First 200 chars showing matching keywords

**Second result:**
- ✅ Same text (from duplicate indexing)
- ✅ Source: "demo-seed-notes"
- ✅ Score: ~0.675 (BM25 ranking)
- ✅ Page: 1
- ✅ Highlight: Similar excerpt

---

### 4.3 Orchestrate Multi-Agent Workflow

**Steps:**
1. Look for **"AI Studio"**, **"Orchestrate"**, or **"Multi-Agent"** feature
2. Click it → Open orchestration interface
3. Select course: **FAH-101**
4. Select student: (auto-filled, should be current user)
5. Enter topic: `recursion`
6. Select agents to run (check all if available):
   - ✅ Search Agent
   - ✅ Tutor Agent
   - ✅ Quiz Agent
   - ✅ Planner Agent
   - ✅ Evaluator Agent
7. Click **"Run Workflow"** button

**Expected results (5-10 seconds, may show progress):**

**Search Agent Output:**
- ✅ Found 2 relevant chunks about recursion with scores

**Tutor Agent Output:**
- ✅ Personalized explanation: *"Demo AI response grounded in the seeded course content."*
- ✅ Tailored to student's mastery level (72.5%)

**Quiz Agent Output:**
- ✅ Quiz preview with 3 questions:
  1. Explain recursion
  2. Contrast BFS and DFS
  3. Why is binary search efficient?

**Planner Agent Output:**
- ✅ Learning path: 5 days recommended
- ✅ Topics: recursion, binary search, graphs, dynamic programming
- ✅ Daily breakdown with milestones

**Evaluator Agent Output:**
- ✅ Evaluation score: 67/100
- ✅ Strengths and weak areas identified

---

### 4.4 Generate Exam

**Steps:**
1. Look for **"Generate Exam"**, **"Create Quiz"**, or **"Exam Builder"**
2. Click it → Open exam creation form
3. Select course: **FAH-101**
4. Select topic(s): `recursion`, `binary search` (multi-select)
5. Number of questions: 5
6. Difficulty: MEDIUM
7. Click **"Generate"** button

**Expected results (3-5 seconds):**
- ✅ Exam generated with 5 questions on selected topics
- ✅ Question types: multiple choice, short answer, explanation (mix)
- ✅ Questions reference course materials
- ✅ Option to preview, edit, save, or assign to students

**Example generated questions:**
- "Explain recursion with a code example."
- "Compare recursive and iterative approaches to binary search."
- "Define base case and why it's critical in recursion."
- "How does dynamic programming optimize recursive solutions?"
- "Trace through a recursive binary search algorithm."

---

### 4.5 Learning Path Generation

**Steps:**
1. Look for **"Learning Path"**, **"Personalized Path"**, or **"Study Plan"**
2. Click it → Open learning path form
3. Select course: **FAH-101**
4. Weak topics (auto-detected from progress):
   - ✅ "recursion" (72.5% mastery < 85% threshold)
5. Available time per day: 45 minutes
6. Duration: 5 days
7. Click **"Generate Path"** button

**Expected results (2-3 seconds):**

**Learning Plan:**
- ✅ **Day 1:** Recursion fundamentals (base case, function calls)
  - Materials: Demo Algorithm Notes (30 min)
  - Practice: Quiz on recursion basics (15 min)

- ✅ **Day 2:** Recursive algorithms (binary search, tree traversal)
  - Materials: Demo Midterm 2025 (25 min)
  - Practice: Code tracing exercises (20 min)

- ✅ **Day 3:** Dynamic programming intro
  - Materials: Review + new content (40 min)
  - Practice: Simple DP problems (5 min)

- ✅ **Day 4:** Optimization techniques
- ✅ **Day 5:** Mastery checkpoint & review

**For each day:**
- ✅ Estimated time breakdown (study/practice)
- ✅ Linked materials and resources
- ✅ Checkpoint quizzes
- ✅ Mastery targets

---

### 4.6 Evaluate Student Answer

**Steps:**
1. Look for **"Evaluate Answer"**, **"Grade Submission"**, or **"Answer Review"**
2. Click it → Open evaluation form
3. Question: `Explain how recursion works with a base case`
4. Student answer: `A function that calls itself until a condition (base case) is true, then stops recursing and returns the value up the call stack.`
5. Reference answer (auto-filled from materials): *"A recursion base case stops the repeated calls and prevents infinite loops."*
6. Click **"Evaluate"** button

**Expected results (2-3 seconds):**
- ✅ Evaluation score: 67/100
- ✅ Feedback: "Good understanding of base case concept. Mention call stack mechanics for complete answer."
- ✅ Suggestions: "Study stack frames and trace execution step-by-step."
- ✅ Comparison to reference answer (similarity score)
- ✅ Recommendation for follow-up topics

---

## Phase 5: Dashboard Feature Validation

### 5.1 Professor Dashboard - Announcements

**Logged in as Professor:**

**Steps:**
1. Navigate to course FAH-101
2. Click **"Announcements"** tab
3. Click **"Create Announcement"** button

**Enter:**
- Title: `Welcome to FAH-101`
- Body: `This course covers fundamental algorithms. Looking forward to working with you all!`
- Click **"Post"** button

**Expected result:**
- ✅ Announcement appears in the list
- ✅ Shows title, body, author (Demo Professor), timestamp
- ✅ Available for students to view immediately

---

### 5.2 Student Dashboard - View Announcements

**Logged in as Student:**

**Steps:**
1. Navigate to course FAH-101
2. Click **"Announcements"** tab

**Expected to see:**
- ✅ "Welcome to FAH-101" announcement
- ✅ By: Demo Professor
- ✅ Posted: Today
- ✅ Full body text visible

---

### 5.3 Message Between Professor & Student

**Logged in as Professor:**

**Steps:**
1. Click on **"Messages"** or **"Inbox"** in navigation
2. Start new message: Click **"New Message"** or similar
3. Recipient: Search for "Demo Student"
4. Subject: `Progress on Recursion`
5. Body: `Hi, your recent work on recursion looks good! Keep practicing with the provided exercises.`
6. Click **"Send"**

**Expected result:**
- ✅ Message sent to student
- ✅ Appears in professor's sent folder

**Then log in as Student:**

**Steps:**
1. Click on **"Messages"** or **"Inbox"**
2. Should see message from Demo Professor

**Expected to see:**
- ✅ Message sender: "Demo Professor"
- ✅ Subject line
- ✅ Preview of body
- ✅ Timestamp (today)
- ✅ Unread indicator (if not opened yet)

**Click to open:**
- ✅ Full message body displayed
- ✅ Reply button available
- ✅ Mark as read/unread options

---

### 5.4 Progress Tracking

**Logged in as Student:**

**Steps:**
1. Navigate to course FAH-101
2. Click **"Progress"** or **"My Skills"** tab

**Expected to see:**
- ✅ Topic: "recursion"
- ✅ Mastery score: 72.5% (with visual gauge/bar)
- ✅ Last seen: Recently
- ✅ Skill status: "Developing" or "Intermediate"
- ✅ Recommended actions: "Complete learning path" or "Practice more"

---

## Troubleshooting

### Backend Connection Issues

**Problem:** Frontend shows "Cannot connect to backend" or 404 errors

**Solutions:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check API endpoints
curl http://localhost:8000/api/v1/

# Verify CORS settings (if frontend on different port)
# Check console logs in browser (F12 → Console tab)
```

---

### Auth Token Expiration

**Problem:** "Unauthorized" after logging in and navigating

**Solution:**
- Token expires after 24 hours (default)
- Log out and log back in
- Check browser DevTools (F12) → Application → Cookies/LocalStorage for `access_token`

---

### AI Workflow Returns Empty Results

**Problem:** RAG Ask or Search returns no results

**Solutions:**
```bash
# Verify ChromaDB is running and populated
curl http://localhost:8001/api/v1

# Check if vector store has indexed documents
# Run smoke test again to re-index
uv run python -m fahimni.scripts.demo_workflow

# Check backend logs for AI service errors
```

---

### Frontend Build Errors

**Problem:** `npm run dev` fails with build errors

**Solutions:**
```bash
# Clear node_modules and reinstall
cd frontend
rm -r node_modules package-lock.json
npm install
npm run dev

# Check Node.js version (should be 16+)
node --version

# Try clearing Vite cache
rm -r .vite
npm run dev
```

---

## Success Checklist

- [x] Backend server running on localhost:8000
- [x] Frontend dev server running on localhost:5173
- [x] Landing page loads with animations
- [x] Professor login works (professor.demo@fahimni.com)
- [x] Professor dashboard shows FAH-101 course
- [x] Professor can view materials, archives, students
- [x] Professor can create announcements
- [x] Student login works (student.demo@fahimni.com)
- [x] Student dashboard shows FAH-101 course
- [x] Student can view materials, archives, progress
- [x] RAG Ask returns AI-generated answer
- [x] Hybrid Search returns ranked results with highlights
- [x] Multi-agent orchestration completes (search, tutor, quiz, planner, evaluator)
- [x] Exam generation creates questions
- [x] Learning path generation creates daily plan
- [x] Answer evaluation returns score & feedback
- [x] Professor can message student
- [x] Student can receive & reply to messages
- [x] Progress tracking shows mastery scores

---

## Next Steps (Post-Testing)

1. **Streaming Responses:** Implement SSE/WebSocket for long-running AI workflows
2. **PDF Upload:** Test teacher material upload and OCR processing
3. **Real HuggingFace LLM:** Switch from DemoAIService to production AIService with real embeddings
4. **Performance Optimization:** Profile and optimize slow endpoints
5. **E2E Tests:** Write Playwright/Cypress tests for critical user flows
6. **Deployment:** Package frontend build and deploy to production
