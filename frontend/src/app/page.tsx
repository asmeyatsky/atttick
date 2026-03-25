import { ChatWidget } from "@/components/ChatWidget";

export default function Home() {
  return (
    <main
      style={{
        maxWidth: 800,
        margin: "0 auto",
        padding: "60px 24px",
      }}
    >
      <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 16 }}>
        Staff Echo Demo
      </h1>
      <p style={{ fontSize: 18, color: "#6b7280", lineHeight: 1.7 }}>
        This is a customer-facing AI chatbot trained on staff voice data. It
        mimics the specific expertise, pricing knowledge, and brand personality
        of the internal team.
      </p>
      <p style={{ fontSize: 18, color: "#6b7280", lineHeight: 1.7 }}>
        Click the chat bubble in the bottom-right corner to start a
        conversation. The bot will respond with staff-like tone and verified
        pricing from BigQuery.
      </p>

      <div
        style={{
          marginTop: 40,
          padding: 24,
          background: "white",
          borderRadius: 12,
          border: "1px solid #e5e7eb",
        }}
      >
        <h2 style={{ fontSize: 20, fontWeight: 600, marginTop: 0 }}>
          Features
        </h2>
        <ul style={{ lineHeight: 2, color: "#4b5563" }}>
          <li>Real-time streaming responses via WebSocket</li>
          <li>Staff tone alignment from voice training data</li>
          <li>Verified pricing with source citations</li>
          <li>Automatic human handoff for unverified pricing</li>
          <li>PII masking on all training data</li>
        </ul>
      </div>

      <ChatWidget />
    </main>
  );
}
