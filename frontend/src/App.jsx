import { useEffect, useState } from "react";
import { api, clearTokens, getToken, listResults, saveTokens } from "./api";

const NAVIGATION = [
  ["home", "Home", "✦"],
  ["jobs", "Explore Jobs", "🔍"],
  ["dashboard", "My Cockpit", "📊"],
  ["applications", "Applications", "💼"],
  ["resumes", "Resumes", "📄"],
  ["assistant", "AI Assistant", "🤖"],
];

function hashRoute() {
  return window.location.hash.replace("#", "") || "home";
}

export function App() {
  const [route, setRoute] = useState(hashRoute());
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const updateRoute = () => setRoute(hashRoute());
    window.addEventListener("hashchange", updateRoute);
    return () => window.removeEventListener("hashchange", updateRoute);
  }, []);

  useEffect(() => {
    if (!authenticated) {
      setProfile(null);
      return;
    }
    api("/api/profile/")
      .then(setProfile)
      .catch(() => {
        clearTokens();
        setAuthenticated(false);
      });
  }, [authenticated]);

  const navigate = (nextRoute) => {
    window.location.hash = nextRoute;
    setRoute(nextRoute);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const logout = () => {
    clearTokens();
    setAuthenticated(false);
    navigate("home");
  };

  let page = <HomePage navigate={navigate} authenticated={authenticated} />;
  if (route === "jobs") page = <JobsPage authenticated={authenticated} navigate={navigate} />;
  if (route === "dashboard") page = <DashboardPage authenticated={authenticated} navigate={navigate} profile={profile} />;
  if (route === "applications") page = <ApplicationsPage authenticated={authenticated} navigate={navigate} />;
  if (route === "resumes") page = <ResumesPage authenticated={authenticated} navigate={navigate} />;
  if (route === "assistant") page = <AssistantPage authenticated={authenticated} navigate={navigate} />;
  if (route === "profile") page = <ProfilePage authenticated={authenticated} navigate={navigate} profile={profile} onProfileChange={setProfile} />;
  if (route === "auth") page = <AuthPage onAuthenticated={() => { setAuthenticated(true); navigate("dashboard"); }} />;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header className="topbar">
        <a className="brand" href="#home" onClick={(e) => { e.preventDefault(); navigate("home"); }}>
          <div className="brand-icon">✦</div>
          <div>JobPilot <span className="highlight">AI</span></div>
        </a>

        <nav className="desktop-nav">
          {NAVIGATION.map(([path, label, icon]) => (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`nav-link ${route === path ? "active" : ""}`}
            >
              <span>{icon}</span> {label}
            </button>
          ))}
        </nav>

        <div className="header-actions">
          {authenticated ? (
            <>
              <div className="user-profile-badge" onClick={() => navigate("profile")}>
                <div className="user-avatar">{profile?.full_name?.[0] || "U"}</div>
                <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>{profile?.full_name || "Profile"}</span>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={logout}>Log out</button>
            </>
          ) : (
            <>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate("auth")}>Sign in</button>
              <button className="btn btn-primary btn-sm" onClick={() => navigate("auth")}>Get Started ↗</button>
            </>
          )}
        </div>
      </header>

      <main className="main-content" style={{ flex: 1 }}>{page}</main>

      <footer style={{ borderTop: "1px solid var(--border-glass)", padding: "2rem 0", marginTop: "4rem", textAlign: "center", color: "var(--text-muted)", fontSize: "0.85rem" }}>
        <p>JobPilot AI — Autonomous Job Search & Application Assistant · Powered by Django REST Framework & AI Agent Tools</p>
      </footer>
    </div>
  );
}

/* ==================== HOME PAGE ==================== */
function HomePage({ navigate, authenticated }) {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    api("/api/jobs/?ordering=-collected_at")
      .then((data) => setJobs(listResults(data).slice(0, 3)))
      .catch(() => setJobs([]));
  }, []);

  return (
    <div>
      <section className="hero-grid">
        <div>
          <div className="badge-glow">
            <span className="pulse-dot" /> Autonomous Career Intelligence
          </div>
          <h1 className="hero-title">
            Land roles that <span className="accent">match your true potential.</span>
          </h1>
          <p className="hero-sub">
            JobPilot AI transparently analyzes job descriptions against your resume, calculates multi-factor fit scores, generates cover letters, and executes application workflows via a controlled tool-calling AI agent.
          </p>
          <div className="hero-cta">
            <button className="btn btn-primary" onClick={() => navigate(authenticated ? "dashboard" : "auth")}>
              Launch My Cockpit ↗
            </button>
            <button className="btn btn-secondary" onClick={() => navigate("jobs")}>
              Explore Opportunities
            </button>
          </div>
        </div>

        <div>
          <div className="match-visual-card">
            <div className="match-score-header">
              <div>
                <span className="tag tag-emerald">Live Candidate Match</span>
                <h3 style={{ marginTop: "6px", fontSize: "1.2rem" }}>Senior Python / Django Engineer</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>Northstar Labs · Remote</p>
              </div>
              <div className="score-large-circle">
                <div className="score-circle-inner">
                  <span className="score-number" style={{ color: "var(--electric-cyan)" }}>88%</span>
                  <span className="score-label">MATCH</span>
                </div>
              </div>
            </div>

            <div style={{ marginTop: "1.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", marginBottom: "6px" }}>
                <span>Skill Alignment (50% Weight)</span>
                <span style={{ color: "var(--electric-cyan)", fontWeight: 700 }}>92%</span>
              </div>
              <div className="progress-bar-bg">
                <div className="progress-bar-fill" style={{ width: "92%" }} />
              </div>

              <div style={{ display: "flex", gap: "8px", marginTop: "1rem", flexWrap: "wrap" }}>
                <span className="tag tag-emerald">✓ Python</span>
                <span className="tag tag-emerald">✓ Django</span>
                <span className="tag tag-emerald">✓ DRF</span>
                <span className="tag tag-emerald">✓ MySQL</span>
                <span className="tag tag-purple">+ AWS (Growth Gap)</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Jobs Section */}
      <section style={{ marginTop: "3rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "1.5rem" }}>
          <div>
            <span className="tag tag-cyan">Featured Roles</span>
            <h2 style={{ fontSize: "2rem", marginTop: "0.4rem" }}>Recommended for You</h2>
          </div>
          <button className="btn btn-ghost" onClick={() => navigate("jobs")}>View All Roles ↗</button>
        </div>

        <div className="grid-3">
          {jobs.length ? (
            jobs.map((job) => (
              <div key={job.id} className="glass-card glass-card-hover" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                    <span className="tag tag-emerald">{job.employment_type?.replace("_", " ")}</span>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>{job.location || "Remote"}</span>
                  </div>
                  <h3 style={{ fontSize: "1.2rem", marginBottom: "0.4rem" }}>{job.title}</h3>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>{job.company}</p>
                </div>
                <button className="btn btn-secondary btn-sm" style={{ width: "100%" }} onClick={() => navigate("jobs")}>
                  Inspect Job & Match Score
                </button>
              </div>
            ))
          ) : (
            <div className="glass-card" style={{ gridColumn: "1/-1", textAlign: "center", padding: "3rem" }}>
              <p style={{ color: "var(--text-muted)" }}>Loading jobs...</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

/* ==================== JOBS EXPLORER & MATCHING ==================== */
function JobsPage({ authenticated, navigate }) {
  const [jobs, setJobs] = useState([]);
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [selectedJob, setSelectedJob] = useState(null);
  const [matches, setMatches] = useState({});
  const [notice, setNotice] = useState("");

  const fetchJobs = () => {
    const params = new URLSearchParams();
    if (query) params.set("search", query);
    if (location) params.set("location", location);
    api(`/api/jobs/?${params.toString()}`)
      .then((data) => setJobs(listResults(data)))
      .catch(() => setJobs([]));
  };

  useEffect(fetchJobs, []);

  useEffect(() => {
    if (!authenticated || !jobs.length) return;
    Promise.all(
      jobs.slice(0, 15).map(async (job) => [job.id, await api(`/api/jobs/${job.id}/match/`).catch(() => null)])
    ).then((entries) => setMatches(Object.fromEntries(entries.filter(([, v]) => v))));
  }, [authenticated, jobs]);

  const saveJob = async (job) => {
    if (!authenticated) {
      navigate("auth");
      return;
    }
    try {
      await api("/api/applications/", { method: "POST", body: JSON.stringify({ job: job.id, status: "SAVED" }) });
      setNotice(`✓ Saved "${job.title}" to your Applications Tracker.`);
    } catch (err) {
      setNotice(err.message.includes("already") ? "Role is already saved in your tracker." : err.message);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <span className="badge-glow"><span className="pulse-dot" /> Multi-Factor Ingestion & Matching</span>
        <h1 style={{ fontSize: "2.8rem", marginTop: "0.5rem" }}>Opportunity Explorer</h1>
        <p style={{ color: "var(--text-muted)" }}>Search real opportunities. Fit scores are computed deterministically against your verified candidate profile.</p>
      </div>

      <form className="search-bar" onSubmit={(e) => { e.preventDefault(); fetchJobs(); }}>
        <div className="input-group">
          <label className="input-label">Role or Keywords</label>
          <input className="input-field" placeholder="e.g. Python Developer, Django, DRF..." value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
        <div className="input-group">
          <label className="input-label">Location</label>
          <input className="input-field" placeholder="e.g. Hyderabad, Remote..." value={location} onChange={(e) => setLocation(e.target.value)} />
        </div>
        <button type="submit" className="btn btn-primary" style={{ alignSelf: "flex-end", height: "42px" }}>Search Jobs</button>
      </form>

      {notice && <div className="toast-notice">{notice}</div>}

      <div className="grid-2">
        {jobs.map((job) => {
          const match = matches[job.id];
          return (
            <div key={job.id} className="glass-card glass-card-hover" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                  <div>
                    <h2 style={{ fontSize: "1.3rem" }}>{job.title}</h2>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.88rem" }}>{job.company} · {job.location || "Flexible"}</p>
                  </div>
                  {match && (
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: "1.4rem", fontWeight: 800, color: match.overall_match >= 75 ? "var(--electric-cyan)" : "var(--warm-amber)" }}>
                        {match.overall_match}%
                      </span>
                      <div style={{ fontSize: "0.68rem", color: "var(--text-muted)" }}>MATCH SCORE</div>
                    </div>
                  )}
                </div>

                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", margin: "1rem 0" }}>
                  {job.required_skills?.slice(0, 4).map((s) => <span key={s} className="tag tag-cyan">{s}</span>)}
                </div>
              </div>

              <div style={{ display: "flex", gap: "10px", marginTop: "1rem" }}>
                <button type="button" className="btn btn-secondary btn-sm" style={{ flex: 1 }} onClick={() => setSelectedJob(job)}>
                  View Details & Match Breakdown
                </button>
                <button type="button" className="btn btn-primary btn-sm" onClick={() => saveJob(job)}>
                  + Save
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {selectedJob && (
        <JobDetailDrawer
          job={selectedJob}
          match={matches[selectedJob.id]}
          authenticated={authenticated}
          onClose={() => setSelectedJob(null)}
          onSave={() => saveJob(selectedJob)}
        />
      )}
    </div>
  );
}

function JobDetailDrawer({ job, match, onClose, onSave }) {
  return (
    <div className="drawer-right" onClick={onClose}>
      <div className="drawer-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
          <span className="tag tag-emerald">{job.employment_type?.replace("_", " ")}</span>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>✕ Close</button>
        </div>

        <h2 style={{ fontSize: "2rem", marginBottom: "0.2rem" }}>{job.title}</h2>
        <p style={{ color: "var(--text-muted)", fontSize: "1rem", marginBottom: "1.5rem" }}>{job.company} · {job.location}</p>

        {match && (
          <div className="glass-card" style={{ marginBottom: "1.5rem", background: "rgba(6, 182, 212, 0.08)", borderColor: "rgba(6, 182, 212, 0.3)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <span style={{ fontWeight: 700, fontSize: "1.1rem" }}>Deterministic Match Breakdown</span>
              <span style={{ fontSize: "1.8rem", fontWeight: 900, color: "var(--electric-cyan)" }}>{match.overall_match}%</span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.85rem" }}>
              <div>Skills (50%): <strong style={{ color: "var(--electric-cyan)" }}>{match.breakdown?.skills}%</strong></div>
              <div>Experience (20%): <strong>{match.breakdown?.experience}%</strong></div>
              <div>Location (10%): <strong>{match.breakdown?.location}%</strong></div>
              <div>Salary (10%): <strong>{match.breakdown?.salary}%</strong></div>
              <div>Education (10%): <strong>{match.breakdown?.education}%</strong></div>
            </div>
          </div>
        )}

        <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>Required Skills</h3>
        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          {job.required_skills?.map((s) => <span key={s} className="tag tag-emerald">{s}</span>)}
        </div>

        <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>Description</h3>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{job.description}</p>

        <div style={{ marginTop: "2rem", display: "flex", gap: "10px" }}>
          <button type="button" className="btn btn-primary" style={{ flex: 1 }} onClick={onSave}>Save to Application Tracker</button>
        </div>
      </div>
    </div>
  );
}

/* ==================== DASHBOARD (MY COCKPIT) ==================== */
function DashboardPage({ authenticated, navigate, profile }) {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    if (authenticated) api("/api/dashboard/").then(setDashboard).catch(() => {});
  }, [authenticated]);

  if (!authenticated) {
    return (
      <div style={{ textAlign: "center", padding: "4rem 0" }}>
        <h2>Sign in to access your Job Cockpit.</h2>
        <button className="btn btn-primary" style={{ marginTop: "1rem" }} onClick={() => navigate("auth")}>Sign In ↗</button>
      </div>
    );
  }

  if (!dashboard) return <div style={{ color: "var(--text-muted)", padding: "3rem", textAlign: "center" }}>Loading Cockpit Metrics...</div>;

  const statusCount = dashboard.applications_by_status || {};

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <span className="badge-glow"><span className="pulse-dot" /> Real-Time Workspace Insights</span>
        <h1 style={{ fontSize: "2.8rem", marginTop: "0.5rem" }}>Welcome, {profile?.full_name?.split(" ")[0] || "Candidate"}</h1>
      </div>

      <div className="grid-4" style={{ marginBottom: "2rem" }}>
        <div className="metric-card">
          <div className="metric-title">Tracked Applications</div>
          <div className="metric-value metric-accent-emerald">{dashboard.applications || 0}</div>
        </div>
        <div className="metric-card">
          <div className="metric-title">Interviews Scheduled</div>
          <div className="metric-value metric-accent-cyan">{statusCount.INTERVIEW || 0}</div>
        </div>
        <div className="metric-card">
          <div className="metric-title">Follow-ups Due</div>
          <div className="metric-value metric-accent-amber">{dashboard.pending_follow_ups || 0}</div>
        </div>
        <div className="metric-card">
          <div className="metric-title">Highest Match Score</div>
          <div className="metric-value metric-accent-purple">
            {dashboard.top_matching_jobs?.[0] ? `${dashboard.top_matching_jobs[0].overall_match}%` : "—"}
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="glass-card">
          <h2 style={{ fontSize: "1.3rem", marginBottom: "1rem" }}>Top Matching Opportunities</h2>
          {dashboard.top_matching_jobs?.length ? (
            dashboard.top_matching_jobs.map((job) => (
              <div key={job.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--border-glass)" }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{job.title}</div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{job.company}</div>
                </div>
                <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                  <span style={{ fontSize: "1.3rem", fontWeight: 800, color: "var(--electric-cyan)" }}>{job.overall_match}%</span>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => navigate("jobs")}>Inspect</button>
                </div>
              </div>
            ))
          ) : (
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>No matching jobs yet. Explore jobs to generate scores.</p>
          )}
        </div>

        <div className="glass-card">
          <h2 style={{ fontSize: "1.3rem", marginBottom: "0.5rem" }}>Growth Skill Cloud</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>Most requested skills missing from your candidate profile:</p>
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "1rem" }}>
            {dashboard.most_common_missing_skills?.map((skill) => (
              <span key={skill} className="tag tag-purple" style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
                + {skill}
              </span>
            ))}
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => navigate("profile")}>Update Candidate Profile ↗</button>
        </div>
      </div>
    </div>
  );
}

/* ==================== APPLICATIONS TRACKER ==================== */
function ApplicationsPage({ authenticated, navigate }) {
  const [apps, setApps] = useState([]);
  const [coverLetter, setCoverLetter] = useState(null);
  const [notice, setNotice] = useState("");

  const fetchApps = () => {
    if (authenticated) {
      api("/api/applications/").then((data) => setApps(listResults(data))).catch(() => setApps([]));
    }
  };

  useEffect(fetchApps, [authenticated]);

  if (!authenticated) {
    return (
      <div style={{ textAlign: "center", padding: "4rem 0" }}>
        <h2>Sign in to track your job applications.</h2>
        <button className="btn btn-primary" style={{ marginTop: "1rem" }} onClick={() => navigate("auth")}>Sign In ↗</button>
      </div>
    );
  }

  const updateStatus = async (appId, newStatus) => {
    await api(`/api/applications/${appId}/`, { method: "PATCH", body: JSON.stringify({ status: newStatus }) });
    setNotice("✓ Application status updated.");
    fetchApps();
  };

  const deleteApp = async (appId) => {
    if (!confirm("Remove this application from your tracker?")) return;
    await api(`/api/applications/${appId}/`, { method: "DELETE" });
    setNotice("✓ Application removed.");
    fetchApps();
  };

  const generateCoverLetter = async (jobId) => {
    try {
      const letter = await api("/api/cover-letters/", { method: "POST", body: JSON.stringify({ job: jobId }) });
      setCoverLetter(letter);
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <span className="badge-glow"><span className="pulse-dot" /> Lifecycle & Status Workflow</span>
        <h1 style={{ fontSize: "2.8rem", marginTop: "0.5rem" }}>Application Tracker</h1>
      </div>

      {notice && <div className="toast-notice">{notice}</div>}

      <div className="grid-3">
        {apps.map((app) => (
          <div key={app.id} className="glass-card" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1rem" }}>
                <span className="tag tag-cyan">{app.status}</span>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{new Date(app.created_at).toLocaleDateString()}</span>
              </div>
              <h3 style={{ fontSize: "1.2rem" }}>{app.job_details?.title || `Job #${app.job}`}</h3>
              <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>{app.job_details?.company}</p>
            </div>

            <div>
              <label className="input-label" style={{ marginBottom: "4px" }}>Change Status</label>
              <select
                className="input-field"
                value={app.status}
                onChange={(e) => updateStatus(app.id, e.target.value)}
                style={{ marginBottom: "1rem" }}
              >
                <option value="SAVED">SAVED</option>
                <option value="APPLIED">APPLIED</option>
                <option value="INTERVIEW">INTERVIEW</option>
                <option value="REJECTED">REJECTED</option>
                <option value="SELECTED">SELECTED</option>
                <option value="WITHDRAWN">WITHDRAWN</option>
              </select>

              <div style={{ display: "flex", gap: "6px" }}>
                <button type="button" className="btn btn-secondary btn-sm" style={{ flex: 1 }} onClick={() => generateCoverLetter(app.job)}>
                  📄 Cover Letter
                </button>
                <button type="button" className="btn btn-ghost btn-sm" style={{ color: "var(--hyper-rose)" }} onClick={() => deleteApp(app.id)}>
                  🗑️
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {coverLetter && (
        <div className="modal-overlay" onClick={() => setCoverLetter(null)}>
          <div className="glass-card" style={{ maxWidth: "650px", width: "100%", padding: "2rem", background: "var(--bg-surface)" }} onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>Generated Cover Letter</h2>
            <div style={{ background: "rgba(0,0,0,0.4)", padding: "1.2rem", borderRadius: "10px", fontSize: "0.9rem", lineHeight: 1.6, whiteSpace: "pre-wrap", maxHeight: "400px", overflowY: "auto", marginBottom: "1.5rem" }}>
              {coverLetter.content}
            </div>
            <button type="button" className="btn btn-primary" onClick={() => setCoverLetter(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ==================== RESUME MANAGER ==================== */
function ResumesPage({ authenticated, navigate }) {
  const [resumes, setResumes] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState("");

  const fetchResumes = () => {
    if (authenticated) api("/api/resumes/").then((data) => setResumes(listResults(data))).catch(() => setResumes([]));
  };

  useEffect(fetchResumes, [authenticated]);

  if (!authenticated) {
    return (
      <div style={{ textAlign: "center", padding: "4rem 0" }}>
        <h2>Sign in to manage your resumes.</h2>
        <button className="btn btn-primary" style={{ marginTop: "1rem" }} onClick={() => navigate("auth")}>Sign In ↗</button>
      </div>
    );
  }

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name);
    formData.append("is_primary", "true");
    try {
      await api("/api/resumes/", { method: "POST", body: formData });
      setNotice("✓ Resume uploaded & parsed successfully.");
      fetchResumes();
    } catch (err) {
      alert(err.message);
    } finally {
      setUploading(false);
    }
  };

  const setPrimary = async (resumeId) => {
    await api(`/api/resumes/${resumeId}/`, { method: "PATCH", body: JSON.stringify({ is_primary: true }) });
    setNotice("✓ Set primary resume.");
    fetchResumes();
  };

  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <span className="badge-glow"><span className="pulse-dot" /> Private Storage & Rule Parsing</span>
        <h1 style={{ fontSize: "2.8rem", marginTop: "0.5rem" }}>Resume Manager</h1>
      </div>

      {notice && <div className="toast-notice">{notice}</div>}

      <div className="glass-card" style={{ marginBottom: "2rem", textAlign: "center", padding: "2.5rem" }}>
        <h3 style={{ fontSize: "1.3rem", marginBottom: "0.5rem" }}>Upload PDF Resume</h3>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>Local text extraction parses skills and profile data securely.</p>
        <input type="file" accept=".pdf" onChange={handleUpload} style={{ display: "none" }} id="resume-input" />
        <label htmlFor="resume-input" className="btn btn-primary" style={{ cursor: "pointer" }}>
          {uploading ? "Extracting & Parsing..." : "📁 Upload PDF Resume"}
        </label>
      </div>

      <div className="grid-2">
        {resumes.map((res) => (
          <div key={res.id} className="glass-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h3 style={{ fontSize: "1.2rem" }}>{res.title}</h3>
              {res.is_primary ? (
                <span className="tag tag-emerald">PRIMARY RESUME</span>
              ) : (
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setPrimary(res.id)}>Make Primary</button>
              )}
            </div>

            <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "0.5rem" }}>Extracted Skills</h4>
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {res.parsed_data?.skills?.map((s) => <span key={s} className="tag tag-cyan">{s}</span>) || <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>No skills parsed yet.</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ==================== AI ASSISTANT (TOOL AGENT) ==================== */
function AssistantPage({ authenticated, navigate }) {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! I am JobPilot AI Agent. I can search jobs, calculate match scores, generate cover letters, and track follow-ups using approved internal tools." }
  ]);
  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);

  if (!authenticated) {
    return (
      <div style={{ textAlign: "center", padding: "4rem 0" }}>
        <h2>Sign in to speak with the AI Assistant Agent.</h2>
        <button className="btn btn-primary" style={{ marginTop: "1rem" }} onClick={() => navigate("auth")}>Sign In ↗</button>
      </div>
    );
  }

  const sendPrompt = async (textToSend) => {
    const msg = textToSend || prompt;
    if (!msg.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setPrompt("");
    setBusy(true);

    try {
      const res = await api("/api/agent/chat/", { method: "POST", body: JSON.stringify({ message: msg }) });
      const responseText = res.response || (typeof res.data === "string" ? res.data : res.data?.explanation || JSON.stringify(res.data)) || "Tool executed successfully.";
      const toolCalls = res.tool_calls || (res.tool ? [{ tool: res.tool, params: {} }] : []);
      setMessages((prev) => [...prev, { role: "assistant", text: responseText, toolCalls, rawData: res.data }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", text: `Error: ${err.message}` }]);
    } finally {
      setBusy(false);
    }
  };


  return (
    <div>
      <div style={{ marginBottom: "2rem" }}>
        <span className="badge-glow"><span className="pulse-dot" /> Controlled Tool-Calling Agent</span>
        <h1 style={{ fontSize: "2.8rem", marginTop: "0.5rem" }}>AI Career Assistant</h1>
      </div>

      <div className="glass-card" style={{ minHeight: "450px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <div style={{ overflowY: "auto", maxHeight: "400px", display: "flex", flexDirection: "column", gap: "1rem" }}>
          {messages.map((m, idx) => (
            <div key={idx} style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", maxWidth: "80%" }}>
              <div style={{ background: m.role === "user" ? "var(--primary-gradient)" : "rgba(255,255,255,0.06)", color: "#fff", padding: "12px 16px", borderRadius: "14px", fontSize: "0.92rem", lineHeight: 1.5 }}>
                {m.text}
              </div>

              {m.toolCalls?.map((tc, tIdx) => (
                <div key={tIdx} style={{ marginTop: "6px", fontSize: "0.75rem", fontFamily: "JetBrains Mono", color: "var(--electric-cyan)" }}>
                  🔧 Executed Tool: <strong>{tc.tool}</strong>
                </div>
              ))}
            </div>
          ))}
        </div>

        <div style={{ marginTop: "1.5rem" }}>
          <div style={{ display: "flex", gap: "8px", marginBottom: "1rem", flexWrap: "wrap" }}>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => sendPrompt("Find Python Django jobs in Hyderabad")}>
              "Find Python jobs"
            </button>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => sendPrompt("Show my pending follow-up tasks")}>
              "Show pending follow-ups"
            </button>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => sendPrompt("Show jobs where I have high match")}>
              "Show top matches"
            </button>
          </div>

          <form style={{ display: "flex", gap: "10px" }} onSubmit={(e) => { e.preventDefault(); sendPrompt(); }}>
            <input className="input-field" placeholder="Ask the agent to search jobs, match skills, or track applications..." value={prompt} onChange={(e) => setPrompt(e.target.value)} />
            <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? "Executing Tool..." : "Send"}</button>
          </form>
        </div>
      </div>
    </div>
  );
}

/* ==================== PROFILE EDITOR ==================== */
function ProfilePage({ authenticated, navigate, profile, onProfileChange }) {
  const [formData, setFormData] = useState({
    full_name: profile?.full_name || "",
    professional_headline: profile?.professional_headline || "",
    location: profile?.location || "",
    years_of_experience: profile?.years_of_experience || 0,
    skills: profile?.skills?.join(", ") || "",
  });
  const [notice, setNotice] = useState("");

  if (!authenticated) return null;

  const save = async (e) => {
    e.preventDefault();
    const skillsArray = formData.skills.split(",").map((s) => s.trim()).filter(Boolean);
    const updated = await api("/api/profile/", {
      method: "PATCH",
      body: JSON.stringify({ ...formData, skills: skillsArray }),
    });
    onProfileChange(updated);
    setNotice("✓ Profile updated successfully.");
  };

  return (
    <div style={{ maxWidth: "650px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "2.5rem", marginBottom: "1.5rem" }}>Candidate Profile</h1>
      {notice && <div className="toast-notice">{notice}</div>}
      <form className="glass-card" onSubmit={save} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div className="input-group">
          <label className="input-label">Full Name</label>
          <input className="input-field" value={formData.full_name} onChange={(e) => setFormData({ ...formData, full_name: e.target.value })} />
        </div>
        <div className="input-group">
          <label className="input-label">Headline</label>
          <input className="input-field" value={formData.professional_headline} onChange={(e) => setFormData({ ...formData, professional_headline: e.target.value })} />
        </div>
        <div className="input-group">
          <label className="input-label">Skills (comma separated)</label>
          <input className="input-field" value={formData.skills} onChange={(e) => setFormData({ ...formData, skills: e.target.value })} />
        </div>
        <button type="submit" className="btn btn-primary" style={{ marginTop: "1rem" }}>Save Profile</button>
      </form>
    </div>
  );
}

/* ==================== AUTHENTICATION PAGE ==================== */
function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setBusy(true);
    const form = new FormData(e.currentTarget);
    const username = form.get("username");
    const password = form.get("password");
    try {
      if (mode === "register") {
        await api("/api/auth/register/", { method: "POST", body: JSON.stringify({ username, password, email: form.get("email") }) });
      }
      const tokens = await api("/api/auth/login/", { method: "POST", body: JSON.stringify({ username, password }) });
      saveTokens(tokens);
      onAuthenticated();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const useDemo = async () => {
    setBusy(true);
    try {
      const tokens = await api("/api/auth/login/", { method: "POST", body: JSON.stringify({ username: "demo_candidate", password: "DemoPass123!" }) });
      saveTokens(tokens);
      onAuthenticated();
    } catch (err) {
      setError("Demo user not found. Run 'python manage.py seed_demo_data'.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ maxWidth: "450px", margin: "3rem auto" }}>
      <div className="glass-card">
        <div style={{ display: "flex", gap: "10px", marginBottom: "1.5rem" }}>
          <button type="button" className={`btn btn-sm ${mode === "login" ? "btn-primary" : "btn-secondary"}`} style={{ flex: 1 }} onClick={() => setMode("login")}>Sign In</button>
          <button type="button" className={`btn btn-sm ${mode === "register" ? "btn-primary" : "btn-secondary"}`} style={{ flex: 1 }} onClick={() => setMode("register")}>Register</button>
        </div>

        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {mode === "register" && (
            <div className="input-group">
              <label className="input-label">Email</label>
              <input className="input-field" name="email" type="email" required />
            </div>
          )}
          <div className="input-group">
            <label className="input-label">Username</label>
            <input className="input-field" name="username" required />
          </div>
          <div className="input-group">
            <label className="input-label">Password</label>
            <input className="input-field" name="password" type="password" required />
          </div>

          {error && <div style={{ color: "var(--hyper-rose)", fontSize: "0.85rem" }}>{error}</div>}

          <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}</button>
        </form>

        <div style={{ borderTop: "1px solid var(--border-glass)", marginTop: "1.5rem", paddingTop: "1rem", textAlign: "center" }}>
          <button type="button" className="btn btn-secondary btn-sm" style={{ width: "100%" }} onClick={useDemo}>
            ⚡ One-Click Demo Candidate Sign-In
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
