import { useState } from "react";
import "../styles/landing.css";

export default function LandingPage({ onGetStarted }) {
  const [hoveredCard, setHoveredCard] = useState(null);

  const features = [
    {
      id: 1,
      icon: "🎓",
      title: "Smart Learning Paths",
      description: "AI-powered personalized learning journeys adapted to your pace and style",
    },
    {
      id: 2,
      icon: "🤖",
      title: "Intelligent Agents",
      description: "Advanced AI tutors, planners, and evaluators working together for your success",
    },
    {
      id: 3,
      icon: "📚",
      title: "Rich Materials",
      description: "Access comprehensive course materials with smart archiving and search",
    },
    {
      id: 4,
      icon: "📊",
      title: "Real-time Analytics",
      description: "Track your progress with detailed insights and performance metrics",
    },
    {
      id: 5,
      icon: "💬",
      title: "Instant Support",
      description: "Get immediate answers through our AI chat and messaging system",
    },
    {
      id: 6,
      icon: "🎯",
      title: "Quiz Engine",
      description: "Adaptive assessments that challenge and reinforce your learning",
    },
  ];

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="nav-brand">
          <span className="brand-logo">𝓕</span>
          <span className="brand-text">Fahimni</span>
        </div>
        <button className="btn btn-nav" onClick={onGetStarted}>
          Sign In
        </button>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="gradient-text">Fahimni</span>
            <br />
            Your AI-Powered Learning Companion
          </h1>
          <p className="hero-subtitle">
            Transform your educational journey with intelligent tutoring, adaptive learning paths,
            and real-time insights
          </p>
          <div className="hero-buttons">
            <button className="btn btn-primary" onClick={onGetStarted}>Get Started</button>
            <button className="btn btn-secondary" onClick={() => {
              // Scroll to about section
              document.querySelector('.about').scrollIntoView({ behavior: 'smooth' });
            }}>Learn More</button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-element elem-1"></div>
          <div className="floating-element elem-2"></div>
          <div className="floating-element elem-3"></div>
        </div>
      </section>

      {/* About Section */}
      <section className="about">
        <div className="about-container">
          <h2 className="section-title">About Fahimni</h2>
          <p className="about-text">
            Fahimni is a next-generation learning platform that combines cutting-edge AI technology
            with proven educational methodologies. Our intelligent agents work seamlessly to provide
            personalized tutoring, adaptive content recommendations, and comprehensive progress
            tracking. Whether you're a student seeking to master new concepts or an educator
            delivering exceptional learning experiences, Fahimni empowers you with tools designed
            for the future of education.
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="features-container">
          <h2 className="section-title">Powerful Features</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div
                key={feature.id}
                className="feature-card"
                style={{ "--delay": `${index * 0.1}s` }}
                onMouseEnter={() => setHoveredCard(feature.id)}
                onMouseLeave={() => setHoveredCard(null)}
              >
                <div className="card-icon">{feature.icon}</div>
                <h3 className="card-title">{feature.title}</h3>
                <p className="card-description">{feature.description}</p>
                <div className="card-indicator"></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="cta-content">
          <h2>Ready to Transform Your Learning?</h2>
          <p>Join thousands of students and educators already using Fahimni</p>
          <div className="cta-buttons">
            <button className="btn btn-primary" onClick={onGetStarted}>Sign Up Today</button>
            <button className="btn btn-secondary" onClick={() => {
              // Scroll to features section
              document.querySelector('.features').scrollIntoView({ behavior: 'smooth' });
            }}>Request Demo</button>
          </div>
        </div>
      </section>
    </div>
  );
}
