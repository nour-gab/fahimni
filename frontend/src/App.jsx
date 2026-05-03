import { useEffect, useMemo, useState } from "react";

import LandingPage from "./components/LandingPage";
import {
  analytics as apiAnalytics,
  createAnnouncement,
  createArchiveResource,
  createAssignment,
  createCourse,
  createMaterial,
  enrollStudent,
  evaluateAnswer,
  generateExam,
  getConversation,
  health,
  hybridSearch,
  learningPath,
  listAnnouncements,
  listArchiveResources,
  listCourses,
  listMaterials,
  listMyGrades,
  listProgress,
  login,
  me,
  orchestrateAgents,
  postGrade,
  ragAsk,
  register,
  sendMessage,
  teacherAnalyze,
  uploadOcr,
  uploadPdf,
  trackEvent,
  upsertProgress,
} from "./lib/api";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", hint: "Overview" },
  { id: "courses", label: "Courses", hint: "Create + enroll" },
  { id: "announcements", label: "Announcements", hint: "Course news" },
  { id: "materials", label: "Materials", hint: "Upload + archive" },
  { id: "ai", label: "AI Studio", hint: "RAG + agents" },
  { id: "messages", label: "Messages", hint: "Inbox + chat" },
  { id: "grades", label: "Grades", hint: "Assignments" },
  { id: "analytics", label: "Analytics", hint: "Events + mastery" },
];

const ROLE_OPTIONS = ["STUDENT", "PROFESSOR", "ADMIN"];
const DEFAULT_ROLE = "PROFESSOR";
const EMPTY_AUTH = {
  email: "",
  password: "",
  full_name: "",
  role: DEFAULT_ROLE,
};

const EMPTY_COURSE = { title: "", code: "", description: "" };
const EMPTY_ENROLLMENT = { course_id: "", student_id: "" };
const EMPTY_ANNOUNCEMENT = { course_id: "", title: "", body: "" };
const EMPTY_MESSAGE = { recipient_id: "", content: "" };
const EMPTY_ASSIGNMENT = { course_id: "", title: "", description: "", total_points: 100 };
const EMPTY_GRADE = { assignment_id: "", student_id: "", score: 90, feedback: "" };
const EMPTY_MATERIAL = {
  course_id: "",
  title: "",
  material_type: "PDF",
  source_type: "TEACHER",
  year: new Date().getFullYear(),
  is_verified: true,
  storage_url: "",
};
const EMPTY_ARCHIVE = {
  course_id: "",
  title: "",
  resource_type: "EXAM",
  year: new Date().getFullYear(),
  university: "",
  professor: "",
  difficulty: "MEDIUM",
  file_url: "",
};
const EMPTY_PROGRESS = {
  course_id: "",
  topic: "",
  mastery_score: 60,
  last_seen: "",
};
const EMPTY_AI = {
  question: "",
  search_query: "",
  teacher_content: "",
  prompt: "",
  exam_topic: "",
  exam_question_count: 5,
  evaluate_reference: "",
  evaluate_student: "",
  path_topics: "Recursion, Graphs",
  path_days: 5,
  path_minutes: 45,
  analytics_records: "[{\"topic\":\"Recursion\",\"score\":72}]",
};

function useLocalStorageState(key, initialValue) {
  const [value, setValue] = useState(() => {
    if (typeof window === "undefined") {
      return initialValue;
    }

    const stored = window.localStorage.getItem(key);
    return stored ? stored : initialValue;
  });

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (value === null || value === undefined || value === "") {
      window.localStorage.removeItem(key);
      return;
    }

    window.localStorage.setItem(key, value);
  }, [key, value]);

  return [value, setValue];
}

function App() {
  const [token, setToken] = useLocalStorageState("fahimni.token", "");
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("dashboard");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: "info", message: "Ready to connect to the backend." });
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState(EMPTY_AUTH);
  const [showLanding, setShowLanding] = useState(!token);
  const [courses, setCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [announcements, setAnnouncements] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [archiveResources, setArchiveResources] = useState([]);
  const [progressRows, setProgressRows] = useState([]);
  const [grades, setGrades] = useState([]);
  const [conversation, setConversation] = useState([]);
  const [aiState, setAiState] = useState({});
  const [aiResult, setAiResult] = useState(null);
  const [analyticsResult, setAnalyticsResult] = useState(null);
  const [uploadState, setUploadState] = useState({ pdf: null, ocr: null });

  const [courseForm, setCourseForm] = useState(EMPTY_COURSE);
  const [enrollmentForm, setEnrollmentForm] = useState(EMPTY_ENROLLMENT);
  const [announcementForm, setAnnouncementForm] = useState(EMPTY_ANNOUNCEMENT);
  const [messageForm, setMessageForm] = useState(EMPTY_MESSAGE);
  const [assignmentForm, setAssignmentForm] = useState(EMPTY_ASSIGNMENT);
  const [gradeForm, setGradeForm] = useState(EMPTY_GRADE);
  const [materialForm, setMaterialForm] = useState(EMPTY_MATERIAL);
  const [archiveForm, setArchiveForm] = useState(EMPTY_ARCHIVE);
  const [progressForm, setProgressForm] = useState(EMPTY_PROGRESS);

  const canManageContent = user && ["PROFESSOR", "ADMIN"].includes(user.role);
  const selectedCourse = useMemo(
    () => courses.find((item) => item.id === selectedCourseId) ?? courses[0] ?? null,
    [courses, selectedCourseId],
  );

  useEffect(() => {
    void initializeSession();
    void loadHealth();
  }, []);

  useEffect(() => {
    if (!token) {
      return;
    }

    void refreshCourseData(selectedCourseId);
  }, [token, selectedCourseId]);

  useEffect(() => {
    if (!token || !page) {
      return;
    }

    if (page === "grades") {
      void refreshGrades();
    }

    if (page === "messages" && messageForm.recipient_id) {
      void refreshConversation(messageForm.recipient_id);
    }
  }, [page, token]);

  useEffect(() => {
    if (selectedCourseId) {
      setAnnouncementForm((current) => ({ ...current, course_id: selectedCourseId }));
      setAssignmentForm((current) => ({ ...current, course_id: selectedCourseId }));
      setMaterialForm((current) => ({ ...current, course_id: selectedCourseId }));
      setArchiveForm((current) => ({ ...current, course_id: selectedCourseId }));
      setProgressForm((current) => ({ ...current, course_id: selectedCourseId }));
      setAiState((current) => ({ ...current, course_id: selectedCourseId }));
    }
  }, [selectedCourseId]);

  async function initializeSession() {
    if (!token) {
      return;
    }

    try {
      const [meResponse, courseResponse] = await Promise.all([me(token), listCourses(token)]);
      setUser(meResponse);
      setCourses(courseResponse || []);

      const firstCourse = courseResponse?.[0];
      if (firstCourse) {
        setSelectedCourseId(firstCourse.id);
        setCourseForm((current) => ({ ...current }));
      }

      setStatus({ type: "success", message: `Signed in as ${meResponse.full_name}.` });
    } catch (error) {
      setToken("");
      setUser(null);
      setCourses([]);
      setStatus({ type: "error", message: error.message });
    }
  }

  async function loadHealth() {
    try {
      await health();
    } catch (error) {
      setStatus({ type: "error", message: `Backend health check failed: ${error.message}` });
    }
  }

  async function refreshCourses() {
    if (!token) {
      return;
    }

    try {
      const response = await listCourses(token);
      setCourses(response || []);
      if (!selectedCourseId && response?.[0]) {
        setSelectedCourseId(response[0].id);
      }
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    }
  }

  async function refreshCourseData(courseId = selectedCourseId) {
    if (!token || !courseId) {
      return;
    }

    try {
      const [announcementResponse, materialResponse, archiveResponse, progressResponse] = await Promise.all([
        listAnnouncements(token, courseId),
        listMaterials(token, courseId),
        listArchiveResources(token, courseId),
        listProgress(token, courseId),
      ]);

      setAnnouncements(announcementResponse || []);
      setMaterials(materialResponse || []);
      setArchiveResources(archiveResponse || []);
      setProgressRows(progressResponse || []);
      setAnnouncementForm((current) => ({ ...current, course_id: courseId }));
      setAssignmentForm((current) => ({ ...current, course_id: courseId }));
      setMaterialForm((current) => ({ ...current, course_id: courseId }));
      setArchiveForm((current) => ({ ...current, course_id: courseId }));
      setProgressForm((current) => ({ ...current, course_id: courseId }));
      setAiState((current) => ({ ...current, course_id: courseId }));
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    }
  }

  async function refreshGrades() {
    if (!token) {
      return;
    }

    try {
      const response = await listMyGrades(token);
      setGrades(response || []);
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    }
  }

  async function refreshConversation(otherUserId) {
    if (!token || !otherUserId) {
      return;
    }

    try {
      const response = await getConversation(token, otherUserId);
      setConversation(response || []);
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    }
  }

  function updateAuthField(field, value) {
    setAuthForm((current) => ({ ...current, [field]: value }));
  }

  function updatePageField(setter, field, value) {
    setter((current) => ({ ...current, [field]: value }));
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setLoading(true);

    try {
      if (authMode === "register") {
        await register(authForm);
        setStatus({ type: "success", message: "Account created. Log in to continue." });
        setAuthMode("login");
      } else {
        const response = await login(authForm);
        setToken(response.access_token);
        const [meResponse, courseResponse] = await Promise.all([me(response.access_token), listCourses(response.access_token)]);
        setUser(meResponse);
        setCourses(courseResponse || []);
        setSelectedCourseId(courseResponse?.[0]?.id || "");
        setStatus({ type: "success", message: `Welcome back, ${meResponse.full_name}.` });
        setPage("dashboard");
      }
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateCourse(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await createCourse(token, courseForm);
      setCourses((current) => [response, ...current]);
      setSelectedCourseId(response.id);
      setCourseForm(EMPTY_COURSE);
      setStatus({ type: "success", message: `Course ${response.title} created.` });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleEnrollStudent(event) {
    event.preventDefault();
    setLoading(true);

    try {
      await enrollStudent(token, enrollmentForm);
      setEnrollmentForm(EMPTY_ENROLLMENT);
      setStatus({ type: "success", message: "Enrollment created." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateAnnouncement(event) {
    event.preventDefault();
    setLoading(true);

    try {
      await createAnnouncement(token, announcementForm);
      await refreshCourseData(announcementForm.course_id);
      setAnnouncementForm((current) => ({ ...current, title: "", body: "" }));
      setStatus({ type: "success", message: "Announcement posted." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleSendMessage(event) {
    event.preventDefault();
    setLoading(true);

    try {
      await sendMessage(token, messageForm);
      if (messageForm.recipient_id) {
        await refreshConversation(messageForm.recipient_id);
      }
      setMessageForm(EMPTY_MESSAGE);
      setStatus({ type: "success", message: "Message sent." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateAssignment(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await createAssignment(token, assignmentForm);
      setGradeForm((current) => ({ ...current, assignment_id: response.id, student_id: "" }));
      setAssignmentForm(EMPTY_ASSIGNMENT);
      setStatus({ type: "success", message: "Assignment created." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handlePostGrade(event) {
    event.preventDefault();
    setLoading(true);

    try {
      await postGrade(token, gradeForm);
      await refreshGrades();
      setGradeForm(EMPTY_GRADE);
      setStatus({ type: "success", message: "Grade posted." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateMaterial(event) {
    event.preventDefault();
    setLoading(true);

    try {
      await createMaterial(token, materialForm);
      await refreshCourseData(materialForm.course_id);
      setMaterialForm((current) => ({ ...EMPTY_MATERIAL, course_id: current.course_id || selectedCourseId }));
      setStatus({ type: "success", message: "Material saved." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateArchive(event) {
    event.preventDefault();
    setLoading(true);

    try {
      await createArchiveResource(token, archiveForm);
      await refreshCourseData(archiveForm.course_id);
      setArchiveForm((current) => ({ ...EMPTY_ARCHIVE, course_id: current.course_id || selectedCourseId }));
      setStatus({ type: "success", message: "Archive resource added." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleUpsertProgress(event) {
    event.preventDefault();
    setLoading(true);

    try {
      await upsertProgress(token, progressForm);
      await refreshCourseData(progressForm.course_id);
      setProgressForm((current) => ({ ...EMPTY_PROGRESS, course_id: current.course_id || selectedCourseId }));
      setStatus({ type: "success", message: "Progress saved." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleUploadPdf(event) {
    event.preventDefault();
    const courseId = selectedCourseId || materialForm.course_id || archiveForm.course_id;

    if (!courseId || !uploadState.pdf) {
      setStatus({ type: "error", message: "Select a course and PDF file first." });
      return;
    }

    setLoading(true);
    try {
      const response = await uploadPdf(token, courseId, uploadState.pdf);
      await refreshCourseData(courseId);
      setUploadState((current) => ({ ...current, pdf: null }));
      setStatus({ type: "success", message: `PDF indexed: ${response.chunks_indexed ?? response.chunks ?? 0} chunks.` });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleUploadOcr(event) {
    event.preventDefault();
    const courseId = selectedCourseId || materialForm.course_id || archiveForm.course_id;

    if (!courseId || !uploadState.ocr) {
      setStatus({ type: "error", message: "Select a course and image file first." });
      return;
    }

    setLoading(true);
    try {
      const response = await uploadOcr(token, courseId, uploadState.ocr);
      await refreshCourseData(courseId);
      setUploadState((current) => ({ ...current, ocr: null }));
      setStatus({ type: "success", message: `OCR indexed: ${response.chunks ?? 0} chunks.` });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleAskAi(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await ragAsk(token, {
        course_id: selectedCourseId,
        question: aiState.question,
        task_hint: "student help",
      });
      setAiResult(response);
      await trackEvent(token, {
        course_id: selectedCourseId,
        event_type: "QUESTION_ASKED",
        topic: aiState.question,
        payload: { surface: "rag" },
      });
      setStatus({ type: "success", message: "AI answer generated." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleSearchAi(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await hybridSearch(token, {
        course_id: selectedCourseId,
        query: aiState.search_query,
        k: 5,
      });
      setAiResult(response);
      setStatus({ type: "success", message: "Hybrid search complete." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleTeacherAnalyze(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await teacherAnalyze(token, {
        course_id: selectedCourseId,
        content: aiState.teacher_content,
      });
      setAiResult(response);
      setStatus({ type: "success", message: "Teacher analysis ready." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleOrchestrate(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await orchestrateAgents(token, {
        course_id: selectedCourseId,
        student_id: user.id,
        prompt: aiState.prompt,
      });
      setAiResult(response);
      setStatus({ type: "success", message: "Orchestrator response ready." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleLearningPath(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await learningPath(token, {
        weak_topics: aiState.path_topics.split(",").map((item) => item.trim()).filter(Boolean),
        study_minutes_per_day: Number(aiState.path_minutes),
        horizon_days: Number(aiState.path_days),
      });
      setAiResult(response);
      setStatus({ type: "success", message: "Learning path generated." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateExam(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await generateExam(token, {
        course_id: selectedCourseId,
        topic: aiState.exam_topic,
        question_count: Number(aiState.exam_question_count),
      });
      setAiResult(response);
      setStatus({ type: "success", message: "Exam generated." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleEvaluateAnswer(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await evaluateAnswer(token, {
        reference_answer: aiState.evaluate_reference,
        student_answer: aiState.evaluate_student,
      });
      setAiResult(response);
      setStatus({ type: "success", message: "Answer evaluated." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalytics(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const payload = JSON.parse(aiState.analytics_records);
      const response = await apiAnalytics(token, { records: payload });
      setAnalyticsResult(response);
      setStatus({ type: "success", message: "Analytics summary generated." });
    } catch (error) {
      setStatus({ type: "error", message: error.message });
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    setToken("");
    setUser(null);
    setCourses([]);
    setSelectedCourseId("");
    setAnnouncements([]);
    setMaterials([]);
    setArchiveResources([]);
    setProgressRows([]);
    setGrades([]);
    setConversation([]);
    setAiResult(null);
    setAnalyticsResult(null);
    setUploadState({ pdf: null, ocr: null });
    setStatus({ type: "info", message: "Logged out." });
    setPage("dashboard");
  }

  if (showLanding) {
    return (
      <LandingPage
        onGetStarted={() => {
          setShowLanding(false);
          setAuthMode("login");
        }}
      />
    );
  }

  if (!token || !user) {
    return (
      <AuthScreen
        authMode={authMode}
        authForm={authForm}
        loading={loading}
        status={status}
        setAuthMode={setAuthMode}
        setAuthForm={setAuthForm}
        updateAuthField={updateAuthField}
        onSubmit={handleAuthSubmit}
      />
    );
  }

  return (
    <div className="layout app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">F</div>
          <div>
            <h1 className="brand">fahimni</h1>
            <p className="brand-subtitle">Academic AI workspace</p>
          </div>
        </div>

        <nav className="nav-stack">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${page === item.id ? "active" : ""}`}
              onClick={() => setPage(item.id)}
            >
              <span>{item.label}</span>
              <small>{item.hint}</small>
            </button>
          ))}
        </nav>

        <button className="sidebar-logout" onClick={logout}>
          Logout
        </button>
      </aside>

      <main className="page">
        <header className="top-row">
          <div>
            <p className="eyebrow">Connected to backend</p>
            <h2>{pageTitle(page)}</h2>
          </div>
          <div className="button-row">
            <button className="action lavender" onClick={() => refreshCourseData()}>
              Refresh
            </button>
            <button className="action mint" onClick={() => setPage("materials")}>
              Archive
            </button>
            <button className="action lilac" onClick={() => setPage("ai")}>
              AI Studio
            </button>
          </div>
        </header>

        <StatusBanner status={status} />

        <section className="hero-grid">
          <StatCard label="Active user" value={user.full_name} detail={user.role} accent="lavender" />
          <StatCard label="Courses" value={String(courses.length)} detail="Loaded from /courses" accent="mint" />
          <StatCard label="Archive items" value={String(archiveResources.length)} detail="Old resources" accent="lilac" />
          <StatCard label="Grades" value={String(grades.length)} detail="Current records" accent="peach" />
        </section>

        {page === "dashboard" && (
          <DashboardPage
            selectedCourse={selectedCourse}
            courses={courses}
            announcements={announcements}
            materials={materials}
            archiveResources={archiveResources}
            progressRows={progressRows}
            grades={grades}
            canManageContent={canManageContent}
            setPage={setPage}
            setSelectedCourseId={setSelectedCourseId}
          />
        )}

        {page === "courses" && (
          <CoursesPage
            courses={courses}
            selectedCourseId={selectedCourseId}
            setSelectedCourseId={setSelectedCourseId}
            courseForm={courseForm}
            enrollmentForm={enrollmentForm}
            canManageContent={canManageContent}
            setCourseForm={setCourseForm}
            setEnrollmentForm={setEnrollmentForm}
            updatePageField={updatePageField}
            onCreateCourse={handleCreateCourse}
            onEnrollStudent={handleEnrollStudent}
          />
        )}

        {page === "announcements" && (
          <AnnouncementsPage
            selectedCourse={selectedCourse}
            announcements={announcements}
            announcementForm={announcementForm}
            canManageContent={canManageContent}
            setSelectedCourseId={setSelectedCourseId}
            setAnnouncementForm={setAnnouncementForm}
            updatePageField={updatePageField}
            onCreateAnnouncement={handleCreateAnnouncement}
          />
        )}

        {page === "materials" && (
          <MaterialsPage
            selectedCourse={selectedCourse}
            materials={materials}
            archiveResources={archiveResources}
            progressRows={progressRows}
            materialForm={materialForm}
            archiveForm={archiveForm}
            progressForm={progressForm}
            uploadState={uploadState}
            canManageContent={canManageContent}
            setSelectedCourseId={setSelectedCourseId}
            setMaterialForm={setMaterialForm}
            setArchiveForm={setArchiveForm}
            setProgressForm={setProgressForm}
            setUploadState={setUploadState}
            updatePageField={updatePageField}
            onCreateMaterial={handleCreateMaterial}
            onCreateArchive={handleCreateArchive}
            onUpsertProgress={handleUpsertProgress}
            onUploadPdf={handleUploadPdf}
            onUploadOcr={handleUploadOcr}
          />
        )}

        {page === "ai" && (
          <AiStudioPage
            selectedCourse={selectedCourse}
            aiState={aiState}
            aiResult={aiResult}
            setAiState={setAiState}
            updatePageField={updatePageField}
            onAskAi={handleAskAi}
            onSearchAi={handleSearchAi}
            onTeacherAnalyze={handleTeacherAnalyze}
            onOrchestrate={handleOrchestrate}
            onLearningPath={handleLearningPath}
            onGenerateExam={handleGenerateExam}
            onEvaluateAnswer={handleEvaluateAnswer}
          />
        )}

        {page === "messages" && (
          <MessagesPage
            conversation={conversation}
            messageForm={messageForm}
            setMessageForm={setMessageForm}
            updatePageField={updatePageField}
            onSendMessage={handleSendMessage}
            onLoadConversation={refreshConversation}
          />
        )}

        {page === "grades" && (
          <GradesPage
            grades={grades}
            assignmentForm={assignmentForm}
            gradeForm={gradeForm}
            canManageContent={canManageContent}
            setAssignmentForm={setAssignmentForm}
            setGradeForm={setGradeForm}
            updatePageField={updatePageField}
            onCreateAssignment={handleCreateAssignment}
            onPostGrade={handlePostGrade}
          />
        )}

        {page === "analytics" && (
          <AnalyticsPage
            analyticsResult={analyticsResult}
            aiState={aiState}
            setAiState={setAiState}
            updatePageField={updatePageField}
            onSubmit={handleAnalytics}
          />
        )}
      </main>
    </div>
  );
}

function pageTitle(page) {
  const item = NAV_ITEMS.find((entry) => entry.id === page);
  return item ? item.label : "Dashboard";
}

function AuthScreen({ authMode, authForm, loading, status, setAuthMode, updateAuthField, onSubmit }) {
  return (
    <div className="auth-screen">
      <section className="auth-hero">
        <p className="eyebrow">fahimni</p>
        <h1>One workspace for courses, archives, AI tutoring, and grading.</h1>
        <p>
          Sign in to connect to the FastAPI backend and manage courses, materials, old exams, progress,
          messaging, and AI workflows from one polished interface.
        </p>
        <div className="auth-points">
          <span>JWT auth</span>
          <span>Postgres-backed data</span>
          <span>Archive intelligence</span>
        </div>
      </section>

      <section className="auth-card panel">
        <div className="auth-tabs">
          <button className={authMode === "login" ? "tab active" : "tab"} onClick={() => setAuthMode("login")}>
            Login
          </button>
          <button className={authMode === "register" ? "tab active" : "tab"} onClick={() => setAuthMode("register")}>
            Register
          </button>
        </div>

        <StatusBanner status={status} />

        <form className="form-stack" onSubmit={onSubmit}>
          <label className="field">
            <span>Email</span>
            <input type="email" value={authForm.email} onChange={(event) => updateAuthField("email", event.target.value)} />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={authForm.password}
              onChange={(event) => updateAuthField("password", event.target.value)}
            />
          </label>

          {authMode === "register" && (
            <>
              <label className="field">
                <span>Full name</span>
                <input
                  value={authForm.full_name}
                  onChange={(event) => updateAuthField("full_name", event.target.value)}
                />
              </label>

              <label className="field">
                <span>Role</span>
                <select value={authForm.role} onChange={(event) => updateAuthField("role", event.target.value)}>
                  {ROLE_OPTIONS.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </label>
            </>
          )}

          <button className="submit-btn" disabled={loading} type="submit">
            {loading ? "Working..." : authMode === "login" ? "Login" : "Create account"}
          </button>
        </form>
      </section>
    </div>
  );
}

function StatusBanner({ status }) {
  if (!status?.message) {
    return null;
  }

  return <div className={`status-banner ${status.type || "info"}`}>{status.message}</div>;
}

function StatCard({ label, value, detail, accent }) {
  return (
    <article className={`stat-card ${accent}`}>
      <p>{label}</p>
      <h3>{value}</h3>
      <span>{detail}</span>
    </article>
  );
}

function DashboardPage({
  selectedCourse,
  courses,
  announcements,
  materials,
  archiveResources,
  progressRows,
  grades,
  canManageContent,
  setPage,
  setSelectedCourseId,
}) {
  return (
    <div className="page-stack">
      <section className="panel hero-panel">
        <div>
          <p className="eyebrow">Current course</p>
          <h3>{selectedCourse ? selectedCourse.title : "No course selected"}</h3>
          <p>{selectedCourse ? selectedCourse.description : "Create a course to unlock the rest of the workspace."}</p>
        </div>
        <div className="hero-actions">
          <button className="action lavender" onClick={() => setPage("courses")}>
            Courses
          </button>
          <button className="action mint" onClick={() => setPage("materials")}>
            Archive
          </button>
          <button className="action lilac" onClick={() => setPage("ai")}>
            Tutor
          </button>
        </div>
      </section>

      <section className="cards-grid course-card-grid">
        {courses.map((course) => (
          <button key={course.id} className="course-card" onClick={() => setSelectedCourseId(course.id)}>
            <span className="course-title">{course.title}</span>
            <span className="course-meta">{course.code}</span>
            <span className="course-next">{course.description || "No description yet"}</span>
          </button>
        ))}
      </section>

      <section className="big-grade-card">
        <div>
          <p className="label">Loaded course data</p>
          <h3>{selectedCourse ? selectedCourse.title : "Select a course"}</h3>
          <p className="big-grade">{announcements.length} updates</p>
        </div>
        <div className="summary-list">
          <p><strong>Materials:</strong> {materials.length}</p>
          <p><strong>Archive resources:</strong> {archiveResources.length}</p>
          <p><strong>Progress topics:</strong> {progressRows.length}</p>
          <p><strong>Grades:</strong> {grades.length}</p>
        </div>
      </section>

      <section className="panel split-panel">
        <div>
          <p className="section-label">Announcements</p>
          <div className="list-stack">
            {announcements.length === 0 ? <EmptyState text="No announcements yet." /> : announcements.map((item) => <Row key={item.id} title={item.title} subtitle={item.body} />)}
          </div>
        </div>
        <div>
          <p className="section-label">Archive preview</p>
          <div className="list-stack">
            {archiveResources.length === 0 ? <EmptyState text="No archive resources yet." /> : archiveResources.map((item) => <Row key={item.id} title={`${item.title} (${item.year})`} subtitle={`${item.resource_type} · ${item.university}`} />)}
          </div>
        </div>
      </section>

      <section className="panel split-panel">
        <div>
          <p className="section-label">Materials</p>
          <div className="list-stack">
            {materials.length === 0 ? <EmptyState text="No course materials yet." /> : materials.map((item) => <Row key={item.id} title={item.title} subtitle={`${item.material_type} · ${item.source_type} · ${item.year}`} />)}
          </div>
        </div>
        <div>
          <p className="section-label">Progress</p>
          <div className="list-stack">
            {progressRows.length === 0 ? <EmptyState text="No mastery records yet." /> : progressRows.map((item) => <Row key={item.id} title={item.topic} subtitle={`Mastery ${item.mastery_score}% · last seen ${new Date(item.last_seen).toLocaleDateString()}`} />)}
          </div>
        </div>
      </section>

      <section className="panel">
        <p className="section-label">Teaching status</p>
        <p>{canManageContent ? "You can publish official materials and manage content." : "You are in read-only learner mode for official content."}</p>
      </section>
    </div>
  );
}

function CoursesPage({
  courses,
  selectedCourseId,
  setSelectedCourseId,
  courseForm,
  enrollmentForm,
  canManageContent,
  setCourseForm,
  setEnrollmentForm,
  updatePageField,
  onCreateCourse,
  onEnrollStudent,
}) {
  return (
    <div className="page-stack">
      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onCreateCourse}>
          <p className="section-label">Create course</p>
          <label className="field"><span>Title</span><input value={courseForm.title} onChange={(event) => updatePageField(setCourseForm, "title", event.target.value)} /></label>
          <label className="field"><span>Code</span><input value={courseForm.code} onChange={(event) => updatePageField(setCourseForm, "code", event.target.value)} /></label>
          <label className="field"><span>Description</span><textarea rows="4" value={courseForm.description} onChange={(event) => updatePageField(setCourseForm, "description", event.target.value)} /></label>
          <button className="submit-btn" disabled={!canManageContent} type="submit">Create course</button>
        </form>

        <form className="form-stack" onSubmit={onEnrollStudent}>
          <p className="section-label">Enroll student</p>
          <label className="field"><span>Course ID</span><input value={enrollmentForm.course_id} onChange={(event) => updatePageField(setEnrollmentForm, "course_id", event.target.value)} /></label>
          <label className="field"><span>Student ID</span><input value={enrollmentForm.student_id} onChange={(event) => updatePageField(setEnrollmentForm, "student_id", event.target.value)} /></label>
          <button className="submit-btn" disabled={!canManageContent} type="submit">Enroll</button>
        </form>
      </section>

      <section className="panel">
        <p className="section-label">Courses</p>
        <div className="cards-grid course-card-grid">
          {courses.map((course) => (
            <button key={course.id} className={`course-card ${course.id === selectedCourseId ? "active" : ""}`} onClick={() => setSelectedCourseId(course.id)}>
              <span className="course-title">{course.title}</span>
              <span className="course-meta">{course.code}</span>
              <span className="course-next">{course.id}</span>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

function AnnouncementsPage({ selectedCourse, announcements, announcementForm, canManageContent, setSelectedCourseId, setAnnouncementForm, updatePageField, onCreateAnnouncement }) {
  return (
    <div className="page-stack">
      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onCreateAnnouncement}>
          <p className="section-label">Post announcement</p>
          <label className="field"><span>Course ID</span><input value={announcementForm.course_id} onChange={(event) => updatePageField(setAnnouncementForm, "course_id", event.target.value)} /></label>
          <label className="field"><span>Title</span><input value={announcementForm.title} onChange={(event) => updatePageField(setAnnouncementForm, "title", event.target.value)} /></label>
          <label className="field"><span>Body</span><textarea rows="5" value={announcementForm.body} onChange={(event) => updatePageField(setAnnouncementForm, "body", event.target.value)} /></label>
          <button className="submit-btn" disabled={!canManageContent} type="submit">Publish</button>
        </form>

        <section className="info-column">
          <p className="section-label">Selected course</p>
          <button className="pill-button" onClick={() => selectedCourse && setSelectedCourseId(selectedCourse.id)}>
            {selectedCourse ? `${selectedCourse.title} · ${selectedCourse.code}` : "No course selected"}
          </button>
          <p className="muted">Announcements are returned directly from the backend and can be created by teachers/admins.</p>
        </section>
      </section>

      <section className="panel">
        <p className="section-label">Course announcements</p>
        <div className="list-stack">
          {announcements.length === 0 ? <EmptyState text="No announcements published." /> : announcements.map((item) => <Row key={item.id} title={item.title} subtitle={item.body} />)}
        </div>
      </section>
    </div>
  );
}

function MaterialsPage({
  selectedCourse,
  materials,
  archiveResources,
  progressRows,
  materialForm,
  archiveForm,
  progressForm,
  uploadState,
  canManageContent,
  setSelectedCourseId,
  setMaterialForm,
  setArchiveForm,
  setProgressForm,
  setUploadState,
  updatePageField,
  onCreateMaterial,
  onCreateArchive,
  onUpsertProgress,
  onUploadPdf,
  onUploadOcr,
}) {
  return (
    <div className="page-stack">
      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onCreateMaterial}>
          <p className="section-label">Official material</p>
          <label className="field"><span>Course ID</span><input value={materialForm.course_id} onChange={(event) => updatePageField(setMaterialForm, "course_id", event.target.value)} /></label>
          <label className="field"><span>Title</span><input value={materialForm.title} onChange={(event) => updatePageField(setMaterialForm, "title", event.target.value)} /></label>
          <label className="field"><span>Type</span><select value={materialForm.material_type} onChange={(event) => updatePageField(setMaterialForm, "material_type", event.target.value)}><option>PDF</option><option>IMAGE</option><option>NOTES</option><option>ARCHIVE</option></select></label>
          <label className="field"><span>Source</span><select value={materialForm.source_type} onChange={(event) => updatePageField(setMaterialForm, "source_type", event.target.value)}><option>TEACHER</option><option>STUDENT</option><option>ARCHIVE</option></select></label>
          <label className="field"><span>Year</span><input type="number" value={materialForm.year} onChange={(event) => updatePageField(setMaterialForm, "year", Number(event.target.value))} /></label>
          <label className="field"><span>Storage URL</span><input value={materialForm.storage_url} onChange={(event) => updatePageField(setMaterialForm, "storage_url", event.target.value)} /></label>
          <button className="submit-btn" disabled={!canManageContent} type="submit">Save material</button>
        </form>

        <form className="form-stack" onSubmit={onCreateArchive}>
          <p className="section-label">Archive resource</p>
          <label className="field"><span>Course ID</span><input value={archiveForm.course_id} onChange={(event) => updatePageField(setArchiveForm, "course_id", event.target.value)} /></label>
          <label className="field"><span>Title</span><input value={archiveForm.title} onChange={(event) => updatePageField(setArchiveForm, "title", event.target.value)} /></label>
          <label className="field"><span>Type</span><select value={archiveForm.resource_type} onChange={(event) => updatePageField(setArchiveForm, "resource_type", event.target.value)}><option>EXAM</option><option>TD</option><option>SUMMARY</option></select></label>
          <label className="field"><span>Year</span><input type="number" value={archiveForm.year} onChange={(event) => updatePageField(setArchiveForm, "year", Number(event.target.value))} /></label>
          <label className="field"><span>University</span><input value={archiveForm.university} onChange={(event) => updatePageField(setArchiveForm, "university", event.target.value)} /></label>
          <label className="field"><span>Professor</span><input value={archiveForm.professor} onChange={(event) => updatePageField(setArchiveForm, "professor", event.target.value)} /></label>
          <label className="field"><span>Difficulty</span><select value={archiveForm.difficulty} onChange={(event) => updatePageField(setArchiveForm, "difficulty", event.target.value)}><option>EASY</option><option>MEDIUM</option><option>HARD</option></select></label>
          <label className="field"><span>File URL</span><input value={archiveForm.file_url} onChange={(event) => updatePageField(setArchiveForm, "file_url", event.target.value)} /></label>
          <button className="submit-btn" type="submit">Add archive</button>
        </form>
      </section>

      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onUpsertProgress}>
          <p className="section-label">Personal progress</p>
          <p className="muted">This feeds mastery tracking and future recommendations.</p>
          <label className="field"><span>Course ID</span><input value={progressForm.course_id} onChange={(event) => updatePageField(setProgressForm, "course_id", event.target.value)} /></label>
          <label className="field"><span>Topic</span><input value={progressForm.topic} onChange={(event) => updatePageField(setProgressForm, "topic", event.target.value)} /></label>
          <label className="field"><span>Mastery score</span><input type="number" value={progressForm.mastery_score} onChange={(event) => updatePageField(setProgressForm, "mastery_score", Number(event.target.value))} /></label>
          <button className="submit-btn" type="submit">Save progress</button>
        </form>

        <section className="info-column">
          <p className="section-label">Selected course</p>
          <button className="pill-button" onClick={() => selectedCourse && setSelectedCourseId(selectedCourse.id)}>
            {selectedCourse ? `${selectedCourse.title} · ${selectedCourse.code}` : "No course selected"}
          </button>
          <p className="muted">Archive and progress data are loaded from the backend and ready for citations and analytics.</p>
        </section>
      </section>

      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onUploadPdf}>
          <p className="section-label">Upload PDF to index</p>
          <label className="field">
            <span>Select PDF</span>
            <input
              type="file"
              accept="application/pdf"
              onChange={(event) => setUploadState((current) => ({ ...current, pdf: event.target.files?.[0] || null }))}
            />
          </label>
          <button className="submit-btn" type="submit">Upload and index PDF</button>
        </form>

        <form className="form-stack" onSubmit={onUploadOcr}>
          <p className="section-label">Upload image for OCR</p>
          <label className="field">
            <span>Select image</span>
            <input
              type="file"
              accept="image/*"
              onChange={(event) => setUploadState((current) => ({ ...current, ocr: event.target.files?.[0] || null }))}
            />
          </label>
          <button className="submit-btn" type="submit">Upload and OCR</button>
        </form>
      </section>

      <section className="panel split-panel">
        <div>
          <p className="section-label">Materials</p>
          <div className="list-stack">{materials.length === 0 ? <EmptyState text="No materials yet." /> : materials.map((item) => <Row key={item.id} title={item.title} subtitle={`${item.material_type} · ${item.source_type} · ${item.year}`} />)}</div>
        </div>
        <div>
          <p className="section-label">Archive resources</p>
          <div className="list-stack">{archiveResources.length === 0 ? <EmptyState text="No archive resources yet." /> : archiveResources.map((item) => <Row key={item.id} title={item.title} subtitle={`${item.resource_type} · ${item.year} · ${item.university}`} />)}</div>
        </div>
      </section>

      <section className="panel">
        <p className="section-label">Progress rows</p>
        <div className="list-stack">{progressRows.length === 0 ? <EmptyState text="No progress records yet." /> : progressRows.map((item) => <Row key={item.id} title={item.topic} subtitle={`Mastery ${item.mastery_score}% · updated ${new Date(item.updated_at || item.last_seen).toLocaleString()}`} />)}</div>
      </section>
    </div>
  );
}

function AiStudioPage({ selectedCourse, aiState, aiResult, setAiState, updatePageField, onAskAi, onSearchAi, onTeacherAnalyze, onOrchestrate, onLearningPath, onGenerateExam, onEvaluateAnswer }) {
  return (
    <div className="page-stack">
      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onAskAi}>
          <p className="section-label">RAG tutor</p>
          <label className="field"><span>Question</span><textarea rows="5" value={aiState.question || ""} onChange={(event) => updatePageField(setAiState, "question", event.target.value)} /></label>
          <button className="submit-btn" type="submit">Ask</button>
        </form>

        <form className="form-stack" onSubmit={onSearchAi}>
          <p className="section-label">Hybrid search</p>
          <label className="field"><span>Query</span><textarea rows="5" value={aiState.search_query || ""} onChange={(event) => updatePageField(setAiState, "search_query", event.target.value)} /></label>
          <button className="submit-btn" type="submit">Search</button>
        </form>
      </section>

      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onOrchestrate}>
          <p className="section-label">Multi-agent orchestrator</p>
          <label className="field"><span>Prompt</span><textarea rows="4" value={aiState.prompt || ""} onChange={(event) => updatePageField(setAiState, "prompt", event.target.value)} /></label>
          <button className="submit-btn" type="submit">Run orchestrator</button>
        </form>

        <form className="form-stack" onSubmit={onLearningPath}>
          <p className="section-label">Learning path</p>
          <label className="field"><span>Weak topics</span><input value={aiState.path_topics || ""} onChange={(event) => updatePageField(setAiState, "path_topics", event.target.value)} /></label>
          <label className="field"><span>Days</span><input type="number" value={aiState.path_days || 5} onChange={(event) => updatePageField(setAiState, "path_days", Number(event.target.value))} /></label>
          <label className="field"><span>Minutes/day</span><input type="number" value={aiState.path_minutes || 45} onChange={(event) => updatePageField(setAiState, "path_minutes", Number(event.target.value))} /></label>
          <button className="submit-btn" type="submit">Generate path</button>
        </form>
      </section>

      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onGenerateExam}>
          <p className="section-label">Exam generator</p>
          <label className="field"><span>Topic</span><input value={aiState.exam_topic || ""} onChange={(event) => updatePageField(setAiState, "exam_topic", event.target.value)} /></label>
          <label className="field"><span>Question count</span><input type="number" value={aiState.exam_question_count || 5} onChange={(event) => updatePageField(setAiState, "exam_question_count", Number(event.target.value))} /></label>
          <button className="submit-btn" type="submit">Generate exam</button>
        </form>

        <form className="form-stack" onSubmit={onEvaluateAnswer}>
          <p className="section-label">Answer evaluation</p>
          <label className="field"><span>Reference answer</span><textarea rows="4" value={aiState.evaluate_reference || ""} onChange={(event) => updatePageField(setAiState, "evaluate_reference", event.target.value)} /></label>
          <label className="field"><span>Student answer</span><textarea rows="4" value={aiState.evaluate_student || ""} onChange={(event) => updatePageField(setAiState, "evaluate_student", event.target.value)} /></label>
          <button className="submit-btn" type="submit">Evaluate</button>
        </form>
      </section>

      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onTeacherAnalyze}>
          <p className="section-label">Teacher analyze</p>
          <label className="field"><span>Uploaded text</span><textarea rows="5" value={aiState.teacher_content || ""} onChange={(event) => updatePageField(setAiState, "teacher_content", event.target.value)} /></label>
          <button className="submit-btn" type="submit">Analyze</button>
        </form>

        <section className="info-column">
          <p className="section-label">Selected course</p>
          <button className="pill-button">{selectedCourse ? selectedCourse.title : "No course selected"}</button>
          <p className="muted">Results appear below as soon as the backend returns them.</p>
        </section>
      </section>

      <section className="panel">
        <p className="section-label">AI result</p>
        <pre className="result-block">{formatResult(aiResult)}</pre>
      </section>
    </div>
  );
}

function MessagesPage({ conversation, messageForm, setMessageForm, updatePageField, onSendMessage, onLoadConversation }) {
  return (
    <div className="page-stack">
      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onSendMessage}>
          <p className="section-label">Send message</p>
          <label className="field"><span>Recipient ID</span><input value={messageForm.recipient_id} onChange={(event) => updatePageField(setMessageForm, "recipient_id", event.target.value)} onBlur={() => onLoadConversation(messageForm.recipient_id)} /></label>
          <label className="field"><span>Content</span><textarea rows="5" value={messageForm.content} onChange={(event) => updatePageField(setMessageForm, "content", event.target.value)} /></label>
          <button className="submit-btn" type="submit">Send</button>
        </form>

        <section className="info-column">
          <p className="section-label">Conversation</p>
          <button className="pill-button" onClick={() => onLoadConversation(messageForm.recipient_id || "")}>Load conversation</button>
          <div className="list-stack conversation-stack">
            {conversation.length === 0 ? <EmptyState text="No conversation loaded yet." /> : conversation.map((item) => <Row key={item.id} title={item.content} subtitle={`${item.sender_id} → ${item.recipient_id}`} />)}
          </div>
        </section>
      </section>
    </div>
  );
}

function GradesPage({ grades, assignmentForm, gradeForm, canManageContent, setAssignmentForm, setGradeForm, updatePageField, onCreateAssignment, onPostGrade }) {
  return (
    <div className="page-stack">
      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onCreateAssignment}>
          <p className="section-label">Create assignment</p>
          <label className="field"><span>Course ID</span><input value={assignmentForm.course_id} onChange={(event) => updatePageField(setAssignmentForm, "course_id", event.target.value)} /></label>
          <label className="field"><span>Title</span><input value={assignmentForm.title} onChange={(event) => updatePageField(setAssignmentForm, "title", event.target.value)} /></label>
          <label className="field"><span>Description</span><textarea rows="4" value={assignmentForm.description} onChange={(event) => updatePageField(setAssignmentForm, "description", event.target.value)} /></label>
          <label className="field"><span>Total points</span><input type="number" value={assignmentForm.total_points} onChange={(event) => updatePageField(setAssignmentForm, "total_points", Number(event.target.value))} /></label>
          <button className="submit-btn" disabled={!canManageContent} type="submit">Create assignment</button>
        </form>

        <form className="form-stack" onSubmit={onPostGrade}>
          <p className="section-label">Post grade</p>
          <label className="field"><span>Assignment ID</span><input value={gradeForm.assignment_id} onChange={(event) => updatePageField(setGradeForm, "assignment_id", event.target.value)} /></label>
          <label className="field"><span>Student ID</span><input value={gradeForm.student_id} onChange={(event) => updatePageField(setGradeForm, "student_id", event.target.value)} /></label>
          <label className="field"><span>Score</span><input type="number" value={gradeForm.score} onChange={(event) => updatePageField(setGradeForm, "score", Number(event.target.value))} /></label>
          <label className="field"><span>Feedback</span><textarea rows="4" value={gradeForm.feedback} onChange={(event) => updatePageField(setGradeForm, "feedback", event.target.value)} /></label>
          <button className="submit-btn" disabled={!canManageContent} type="submit">Post grade</button>
        </form>
      </section>

      <section className="panel">
        <p className="section-label">My grades</p>
        <div className="list-stack">
          {grades.length === 0 ? <EmptyState text="No grades loaded yet." /> : grades.map((item) => <Row key={item.id} title={`${item.score} points`} subtitle={item.feedback || `${item.assignment_id} · ${item.student_id}`} />)}
        </div>
      </section>
    </div>
  );
}

function AnalyticsPage({ analyticsResult, aiState, setAiState, updatePageField, onSubmit }) {
  return (
    <div className="page-stack">
      <section className="panel split-panel">
        <form className="form-stack" onSubmit={onSubmit}>
          <p className="section-label">Analytics records JSON</p>
          <label className="field"><span>Records</span><textarea rows="10" value={aiState.analytics_records || ""} onChange={(event) => updatePageField(setAiState, "analytics_records", event.target.value)} /></label>
          <button className="submit-btn" type="submit">Run analytics</button>
        </form>

        <section className="panel nested-panel">
          <p className="section-label">Result</p>
          <pre className="result-block compact">{formatResult(analyticsResult)}</pre>
        </section>
      </section>
    </div>
  );
}

function Row({ title, subtitle }) {
  return (
    <article className="row-item">
      <strong>{title}</strong>
      <span>{subtitle}</span>
    </article>
  );
}

function EmptyState({ text }) {
  return <div className="empty-state">{text}</div>;
}

function formatResult(value) {
  if (!value) {
    return "Run an action to see the backend result here.";
  }

  if (typeof value === "string") {
    return value;
  }

  return JSON.stringify(value, null, 2);
}

export default App;
