import { ChatWidget } from "@/components/ChatWidget";
import styles from "@/styles/chat.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <header className={styles.pageHeader}>
        <div className={styles.logo}>
          <div className={styles.logoIcon}>
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" x2="12" y1="19" y2="22" />
            </svg>
          </div>
          <span>Staff Echo</span>
        </div>
        <p className={styles.tagline}>
          AI-powered support trained on your team
        </p>
      </header>

      <div className={styles.pipeline}>
        <div className={styles.pipelineStep}>
          <div className={styles.pipelineIcon}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            </svg>
          </div>
          <span>Staff Recordings</span>
        </div>
        <div className={styles.pipelineArrow}>&rarr;</div>
        <div className={styles.pipelineStep}>
          <div className={styles.pipelineIcon}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
          </div>
          <span>Transcription</span>
        </div>
        <div className={styles.pipelineArrow}>&rarr;</div>
        <div className={styles.pipelineStep}>
          <div className={styles.pipelineIcon}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <ellipse cx="12" cy="5" rx="9" ry="3" />
              <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
              <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
            </svg>
          </div>
          <span>BigQuery</span>
        </div>
        <div className={styles.pipelineArrow}>&rarr;</div>
        <div className={styles.pipelineStep}>
          <div className={styles.pipelineIcon}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <span>Gemini AI</span>
        </div>
        <div className={styles.pipelineArrow}>&rarr;</div>
        <div className={styles.pipelineStep}>
          <div className={styles.pipelineIcon}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <span>Customer Chat</span>
        </div>
      </div>

      <main className={styles.main}>
        {/* ── Left Panel: Training Data ── */}
        <aside className={styles.sidePanel}>
          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              </svg>
              Training Data
            </h3>
            <div className={styles.statGrid}>
              <div className={styles.stat}>
                <span className={styles.statValue}>847</span>
                <span className={styles.statLabel}>Voice Recordings</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statValue}>12,450</span>
                <span className={styles.statLabel}>Transcribed Segments</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statValue}>156</span>
                <span className={styles.statLabel}>Knowledge Entries</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statValue}>23</span>
                <span className={styles.statLabel}>Pricing Records</span>
              </div>
            </div>
            <div className={styles.cardMeta}>Last sync: Mar 25, 2026</div>
          </div>

          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              Staff Voice Profile
            </h3>
            <div className={styles.profileList}>
              <div className={styles.profileRow}>
                <span className={styles.profileLabel}>Tone</span>
                <span className={styles.profileBadge}>Casual &amp; Friendly</span>
              </div>
              <div className={styles.profileRow}>
                <span className={styles.profileLabel}>Greeting</span>
                <span className={styles.profileValue}>&ldquo;Hey there!&rdquo;</span>
              </div>
              <div className={styles.profileRow}>
                <span className={styles.profileLabel}>Staff Sources</span>
                <span className={styles.profileValue}>Sarah J., Mike C.</span>
              </div>
            </div>
            <div className={styles.tagList}>
              <span className={styles.tag}>absolutely</span>
              <span className={styles.tag}>happy to help</span>
              <span className={styles.tag}>great question</span>
              <span className={styles.tag}>we&apos;ve got you covered</span>
            </div>
          </div>

          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              Recent Activity
            </h3>
            <div className={styles.activityList}>
              <div className={styles.activityItem}>
                <div className={styles.activityDot} />
                <div>
                  <div className={styles.activityText}>5 new recordings processed</div>
                  <div className={styles.activityTime}>2 hours ago</div>
                </div>
              </div>
              <div className={styles.activityItem}>
                <div className={styles.activityDot} />
                <div>
                  <div className={styles.activityText}>Pricing data synced from BigQuery</div>
                  <div className={styles.activityTime}>6 hours ago</div>
                </div>
              </div>
              <div className={styles.activityItem}>
                <div className={styles.activityDot} />
                <div>
                  <div className={styles.activityText}>Tone profile updated</div>
                  <div className={styles.activityTime}>1 day ago</div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* ── Center: Chat ── */}
        <ChatWidget />

        {/* ── Right Panel: Analytics ── */}
        <aside className={styles.sidePanel}>
          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
              Response Quality
            </h3>
            <div className={styles.metricList}>
              <div className={styles.metric}>
                <div className={styles.metricHeader}>
                  <span>Accuracy</span>
                  <span className={styles.metricValue}>98.2%</span>
                </div>
                <div className={styles.metricBar}>
                  <div className={styles.metricFill} style={{ width: "98.2%" }} />
                </div>
              </div>
              <div className={styles.metric}>
                <div className={styles.metricHeader}>
                  <span>Tone Match</span>
                  <span className={styles.metricValue}>94.7%</span>
                </div>
                <div className={styles.metricBar}>
                  <div className={styles.metricFill} style={{ width: "94.7%" }} />
                </div>
              </div>
              <div className={styles.metric}>
                <div className={styles.metricHeader}>
                  <span>Verified Responses</span>
                  <span className={styles.metricValue}>91.3%</span>
                </div>
                <div className={styles.metricBar}>
                  <div className={styles.metricFill} style={{ width: "91.3%" }} />
                </div>
              </div>
              <div className={styles.metric}>
                <div className={styles.metricHeader}>
                  <span>Human Handoffs</span>
                  <span className={styles.metricValueSmall}>3.1%</span>
                </div>
                <div className={styles.metricBar}>
                  <div className={styles.metricFillWarn} style={{ width: "3.1%" }} />
                </div>
              </div>
            </div>
          </div>

          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 20V10" />
                <path d="M18 20V4" />
                <path d="M6 20v-4" />
              </svg>
              Knowledge Coverage
            </h3>
            <div className={styles.coverageList}>
              <div className={styles.coverageItem}>
                <div className={styles.coverageHeader}>
                  <span>Product Specs</span>
                  <span>42 entries</span>
                </div>
                <div className={styles.metricBar}>
                  <div className={styles.metricFill} style={{ width: "85%" }} />
                </div>
              </div>
              <div className={styles.coverageItem}>
                <div className={styles.coverageHeader}>
                  <span>Pricing</span>
                  <span>23 entries</span>
                </div>
                <div className={styles.metricBar}>
                  <div className={styles.metricFillSuccess} style={{ width: "100%" }} />
                </div>
              </div>
              <div className={styles.coverageItem}>
                <div className={styles.coverageHeader}>
                  <span>FAQs</span>
                  <span>67 entries</span>
                </div>
                <div className={styles.metricBar}>
                  <div className={styles.metricFill} style={{ width: "72%" }} />
                </div>
              </div>
              <div className={styles.coverageItem}>
                <div className={styles.coverageHeader}>
                  <span>General</span>
                  <span>24 entries</span>
                </div>
                <div className={styles.metricBar}>
                  <div className={styles.metricFill} style={{ width: "60%" }} />
                </div>
              </div>
            </div>
          </div>

          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
              Coming Soon
            </h3>
            <div className={styles.roadmapList}>
              <div className={styles.roadmapItem}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
                <span>Calendar Filters</span>
              </div>
              <div className={styles.roadmapItem}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
                <span>PDF Export</span>
              </div>
              <div className={styles.roadmapItem}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
                <span>Multi-language</span>
              </div>
            </div>
          </div>
        </aside>
      </main>

      <footer className={styles.pageFooter}>
        Demo: HomeRevive powered by Staff Echo &mdash; AI trained on real staff
        conversations
      </footer>
    </div>
  );
}
