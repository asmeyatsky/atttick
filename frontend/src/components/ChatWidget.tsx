"use client";

import { useChat } from "@/hooks/useChat";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";
import styles from "@/styles/chat.module.css";

export function ChatWidget() {
  const {
    messages,
    isLoading,
    isOpen,
    error,
    isHandedOff,
    sendMessage,
    toggleWidget,
    clearError,
  } = useChat();

  return (
    <div className={styles.widgetContainer}>
      {isOpen && (
        <div className={styles.chatPanel}>
          <div className={styles.chatHeader}>
            <div className={styles.headerInfo}>
              <div className={styles.headerDot} />
              <span className={styles.headerTitle}>Staff Echo</span>
            </div>
            <button
              className={styles.closeButton}
              onClick={toggleWidget}
              aria-label="Close chat"
            >
              &times;
            </button>
          </div>

          {isHandedOff && (
            <div className={styles.handoffBanner}>
              Connecting you to a team member...
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

          <MessageList messages={messages} isLoading={isLoading} />
          <MessageInput onSend={sendMessage} disabled={isLoading || isHandedOff} />
        </div>
      )}

      <button
        className={styles.chatBubble}
        onClick={toggleWidget}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M18 6L6 18" />
            <path d="M6 6l12 12" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
          </svg>
        )}
      </button>
    </div>
  );
}
