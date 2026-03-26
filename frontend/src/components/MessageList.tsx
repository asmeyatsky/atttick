"use client";

import { useEffect, useRef } from "react";
import type { Message } from "@/types/chat";
import { SourceBadge } from "./SourceBadge";
import styles from "@/styles/chat.module.css";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  onSuggestionClick: (text: string) => void;
}

const SUGGESTIONS = [
  "What kitchen renovation packages do you offer?",
  "How much does a bathroom remodel cost?",
  "Do you offer free consultations?",
  "What's your warranty policy?",
];

export function MessageList({
  messages,
  isLoading,
  onSuggestionClick,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const showSuggestions =
    messages.length === 1 && messages[0].role === "assistant" && !isLoading;

  return (
    <div className={styles.messageList}>
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`${styles.messageRow} ${
            msg.role === "user"
              ? styles.messageRowUser
              : styles.messageRowAssistant
          }`}
        >
          {msg.role === "assistant" && (
            <div className={styles.botAvatar}>
              <svg
                width="16"
                height="16"
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
          )}
          <div
            className={`${styles.messageBubble} ${
              msg.role === "user" ? styles.userBubble : styles.assistantBubble
            }`}
          >
            <div className={styles.messageContent}>{msg.content}</div>
            {msg.role === "assistant" && (
              <SourceBadge sources={msg.sources} isVerified={msg.isVerified} />
            )}
          </div>
        </div>
      ))}

      {showSuggestions && (
        <div className={styles.suggestions}>
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              className={styles.suggestionChip}
              onClick={() => onSuggestionClick(s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {isLoading && (
        <div className={`${styles.messageRow} ${styles.messageRowAssistant}`}>
          <div className={styles.botAvatar}>
            <svg
              width="16"
              height="16"
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
          <div
            className={`${styles.messageBubble} ${styles.assistantBubble}`}
          >
            <div className={styles.typingIndicator}>
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
