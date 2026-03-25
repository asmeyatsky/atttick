"use client";

import { useState, useCallback } from "react";
import styles from "@/styles/chat.module.css";

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  placeholder?: string;
}

export function MessageInput({
  onSend,
  disabled,
  placeholder = "Ask me anything...",
}: MessageInputProps) {
  const [text, setText] = useState("");

  const handleSubmit = useCallback(() => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText("");
    }
  }, [text, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={styles.inputContainer}>
      <textarea
        className={styles.input}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Conversation handed off..." : placeholder}
        disabled={disabled}
        rows={1}
      />
      <button
        className={styles.sendButton}
        onClick={handleSubmit}
        disabled={disabled || !text.trim()}
        aria-label="Send message"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M22 2L11 13" />
          <path d="M22 2L15 22L11 13L2 9L22 2Z" />
        </svg>
      </button>
    </div>
  );
}
