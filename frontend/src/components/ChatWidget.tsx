"use client";

import { useChat } from "@/hooks/useChat";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";
import styles from "@/styles/chat.module.css";

export function ChatWidget() {
  const { messages, isLoading, error, isHandedOff, sendMessage, clearError, resetChat } =
    useChat();

  return (
    <div className={styles.chatCard}>
      <div className={styles.chatHeader}>
        <div className={styles.headerLeft}>
          <div className={styles.avatarIcon}>
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
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
            </svg>
          </div>
          <div>
            <div className={styles.headerTitle}>HomeRevive Assistant</div>
            <div className={styles.headerStatus}>
              <span className={styles.statusDot} />
              Online
            </div>
          </div>
        </div>
        {messages.length > 1 && (
          <button
            className={styles.resetButton}
            onClick={resetChat}
            aria-label="New conversation"
            title="New conversation"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9" />
              <polyline points="16 3 21 3 21 8" />
              <line x1="21" y1="3" x2="14" y2="10" />
            </svg>
          </button>
        )}
      </div>

      {isHandedOff && (
        <div className={styles.handoffBanner}>
          Connecting you with a team member for more detailed assistance...
        </div>
      )}

      {error && (
        <div className={styles.errorBanner}>
          <span>{error}</span>
          <button onClick={clearError} className={styles.errorDismiss}>
            &times;
          </button>
        </div>
      )}

      <MessageList
        messages={messages}
        isLoading={isLoading}
        onSuggestionClick={sendMessage}
      />
      <MessageInput
        onSend={sendMessage}
        disabled={isLoading || isHandedOff}
      />
    </div>
  );
}
