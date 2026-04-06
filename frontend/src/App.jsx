import { useMemo, useState } from "react";

const COURSES = [
  {
    id: "cs101",
    title: "Intro to AI",
    grade: "A-",
    nextItem: "Assignment 3 due Wednesday",
    materials: ["Lecture 8 Slides", "RAG Lab Notebook", "Prompting Guide"],
    assignments: [
      { name: "Assignment 1", grade: "94/100" },
      { name: "Assignment 2", grade: "89/100" },
      { name: "Quiz 1", grade: "18/20" },
    ],
    messages: 4,
  },
  {
    id: "math220",
    title: "Discrete Math",
    grade: "B+",
    nextItem: "Professor announcement posted",
    materials: ["Graph Theory Notes", "Problem Set 4", "Proof Clinic"],
    assignments: [
      { name: "Problem Set 1", grade: "30/30" },
      { name: "Problem Set 2", grade: "26/30" },
      { name: "Midterm", grade: "82/100" },
    ],
    messages: 1,
  },
  {
    id: "hist103",
    title: "Modern History",
    grade: "A",
    nextItem: "Essay feedback available",
    materials: ["Week 6 Timeline", "Archive Links", "Essay Rubric"],
    assignments: [
      { name: "Essay Draft", grade: "47/50" },
      { name: "Discussion", grade: "10/10" },
      { name: "Timeline Quiz", grade: "19/20" },
    ],
    messages: 2,
  },
];

function App() {
  const [activeCourseId, setActiveCourseId] = useState(COURSES[0].id);

  const activeCourse = useMemo(
    () => COURSES.find((course) => course.id === activeCourseId) ?? COURSES[0],
    [activeCourseId],
  );

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1 className="brand">fahimni</h1>
        <button className="sidebar-icon">Home</button>
        <button className="sidebar-icon">Courses</button>
        <button className="sidebar-icon">Grades</button>
        <button className="sidebar-icon">Chat</button>
      </aside>

      <main className="page">
        <header className="top-row">
          <h2>Professor Student Portal</h2>
          <div className="button-row">
            <button className="action lavender">New Msg</button>
            <button className="action mint">Announce</button>
            <button className="action lilac">Gradebook</button>
          </div>
        </header>

        <section className="cards-grid">
          {COURSES.map((course) => (
            <button
              key={course.id}
              className={`course-card ${course.id === activeCourse.id ? "active" : ""}`}
              onClick={() => setActiveCourseId(course.id)}
            >
              <span className="course-title">{course.title}</span>
              <span className="course-grade">Current Grade {course.grade}</span>
              <span className="course-next">{course.nextItem}</span>
            </button>
          ))}
        </section>

        <section className="big-grade-card">
          <div>
            <p className="label">Current Course Grade</p>
            <h3>{activeCourse.title}</h3>
            <p className="big-grade">{activeCourse.grade}</p>
          </div>
          <div>
            <p className="label">Next Assignment or Announcement</p>
            <p>{activeCourse.nextItem}</p>
            <p className="label">Unread Messages</p>
            <p>{activeCourse.messages}</p>
          </div>
        </section>

        <section className="materials-section">
          <div className="materials-header">
            <button className="invisible-btn">Course Materials</button>
            <button className="action mint">Assignments</button>
          </div>
          <div className="underline-divider" />
          <div className="materials-grid">
            <article className="materials-list">
              {activeCourse.materials.map((material) => (
                <p key={material}>{material}</p>
              ))}
            </article>
            <article className="assignments-list">
              {activeCourse.assignments.map((assignment) => (
                <div key={assignment.name} className="assignment-row">
                  <span>{assignment.name}</span>
                  <strong>{assignment.grade}</strong>
                </div>
              ))}
            </article>
          </div>
          <div className="messages-underline">Messages</div>
        </section>
      </main>
    </div>
  );
}

export default App;
