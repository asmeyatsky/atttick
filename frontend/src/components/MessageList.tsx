"use client";

import { useEffect, useRef } from "react";
import type { Message } from "@/types/chat";
import { SourceBadge } from "./SourceBadge";
import styles from "@/styles/chat.module.css";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className={styles.messageList}>
      {messages.length === 0 && (
        <div className={styles.emptyState}>
          <p className={styles.emptyTitle}>Welcome to Staff Echo</p>
          <p className={styles.emptySubtitle}>
            Ask me anything about our products, pricing, or services.
          </p>
        </div>
      )}

      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`${styles.messageBubble} ${
            msg.role === "user" ? styles.userMessage : styles.assistantMessage
          }`}
        >
          <div className={styles.messageContent}>{msg.content}</div>
          {msg.role === "assistant" && (
            <SourceBadge sources={msg.sources} isVerified={msg.isVerified} />
          )}
        </div>
      ))}

      {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
        <div className={`${styles.messageBubble} ${styles.assistantMessage}`}>
          <div className={styles.typingIndicator}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
