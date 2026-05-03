const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

function buildUrl(path) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalizedPath}`;
}

function parseResponseText(text) {
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function getErrorMessage(payload, status) {
  if (payload && typeof payload === "object") {
    if (typeof payload.detail === "string") {
      return payload.detail;
    }

    if (payload.detail && typeof payload.detail === "object" && "message" in payload.detail) {
      return String(payload.detail.message);
    }
  }

  return `Request failed with status ${status}`;
}

export async function request(path, { method = "GET", token, body, headers, isFormData = false } = {}) {
  const requestHeaders = { ...(headers || {}) };
  const options = { method, headers: requestHeaders };

  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  if (body !== undefined && body !== null) {
    if (isFormData) {
      options.body = body;
    } else {
      requestHeaders["Content-Type"] = "application/json";
      options.body = JSON.stringify(body);
    }
  }

  const response = await fetch(buildUrl(path), options);
  const payload = parseResponseText(await response.text());

  if (!response.ok) {
    throw new Error(getErrorMessage(payload, response.status));
  }

  return payload;
}

export function health() {
  return request("/health");
}

export function register(body) {
  return request("/api/v1/auth/register", { method: "POST", body });
}

export function login(body) {
  return request("/api/v1/auth/login", { method: "POST", body });
}

export function me(token) {
  return request("/api/v1/auth/me", { token });
}

export function listCourses(token) {
  return request("/api/v1/courses", { token });
}

export function createCourse(token, body) {
  return request("/api/v1/courses", { method: "POST", token, body });
}

export function enrollStudent(token, body) {
  return request("/api/v1/courses/enroll", { method: "POST", token, body });
}

export function listAnnouncements(token, courseId) {
  return request(`/api/v1/announcements/course/${courseId}`, { token });
}

export function createAnnouncement(token, body) {
  return request("/api/v1/announcements", { method: "POST", token, body });
}

export function sendMessage(token, body) {
  return request("/api/v1/messages", { method: "POST", token, body });
}

export function getConversation(token, otherUserId) {
  return request(`/api/v1/messages/conversation/${otherUserId}`, { token });
}

export function createAssignment(token, body) {
  return request("/api/v1/grades/assignments", { method: "POST", token, body });
}

export function postGrade(token, body) {
  return request("/api/v1/grades", { method: "POST", token, body });
}

export function listMyGrades(token) {
  return request("/api/v1/grades/me", { token });
}

export function ragAsk(token, body) {
  return request("/api/v1/ai/rag/ask", { method: "POST", token, body });
}

export function hybridSearch(token, body) {
  return request("/api/v1/ai/search/hybrid", { method: "POST", token, body });
}

export function teacherAnalyze(token, body) {
  return request("/api/v1/ai/teacher/analyze", { method: "POST", token, body });
}

export function orchestrateAgents(token, body) {
  return request("/api/v1/ai/agents/orchestrate", { method: "POST", token, body });
}

export function learningPath(token, body) {
  return request("/api/v1/ai/learning-path", { method: "POST", token, body });
}

export function generateExam(token, body) {
  return request("/api/v1/ai/quiz/exam-generator", { method: "POST", token, body });
}

export function evaluateAnswer(token, body) {
  return request("/api/v1/ai/answers/evaluate", { method: "POST", token, body });
}

export function analytics(token, body) {
  return request("/api/v1/ai/analytics", { method: "POST", token, body });
}

export function uploadPdf(token, courseId, file) {
  const formData = new FormData();
  formData.append("file", file);
  return request(`/api/v1/ai/upload/pdf?course_id=${courseId}`, {
    method: "POST",
    token,
    body: formData,
    isFormData: true,
  });
}

export function uploadOcr(token, courseId, file) {
  const formData = new FormData();
  formData.append("file", file);
  return request(`/api/v1/ai/upload/ocr?course_id=${courseId}`, {
    method: "POST",
    token,
    body: formData,
    isFormData: true,
  });
}

export function listMaterials(token, courseId, params = {}) {
  const query = new URLSearchParams();
  if (params.include_unverified) query.set("include_unverified", "true");
  if (params.source_type) query.set("source_type", params.source_type);
  if (params.year) query.set("year", String(params.year));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return request(`/api/v1/materials/${courseId}${suffix}`, { token });
}

export function createMaterial(token, body) {
  return request("/api/v1/materials", { method: "POST", token, body });
}

export function listArchiveResources(token, courseId, params = {}) {
  const query = new URLSearchParams();
  if (params.year) query.set("year", String(params.year));
  if (params.only_processed) query.set("only_processed", "true");
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return request(`/api/v1/materials/archive/${courseId}${suffix}`, { token });
}

export function createArchiveResource(token, body) {
  return request("/api/v1/materials/archive", { method: "POST", token, body });
}

export function trackEvent(token, body) {
  return request("/api/v1/materials/events", { method: "POST", token, body });
}

export function upsertProgress(token, body) {
  return request("/api/v1/materials/progress", { method: "POST", token, body });
}

export function listProgress(token, courseId) {
  return request(`/api/v1/materials/progress/${courseId}`, { token });
}