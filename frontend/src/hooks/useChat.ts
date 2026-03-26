"use client";

import { useState, useCallback, useRef } from "react";
import type {
  Message,
  SendMessageRequest,
  SendMessageResponse,
} from "@/types/chat";

function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

function getCustomerId(): string {
  if (typeof window === "undefined") return "anonymous";
  let id = sessionStorage.getItem("staff_echo_customer_id");
  if (!id) {
    id = "customer_" + generateId();
    sessionStorage.setItem("staff_echo_customer_id", id);
  }
  return id;
}

const WELCOME_MESSAGE: Message = {
  id: "welcome",
  content:
    "Hey there! Thanks for reaching out to HomeRevive. I'm an AI assistant trained on our team's actual phone conversations, so I know our services, pricing, and processes inside and out. How can I help you today?",
  role: "assistant",
  sources: [],
  isVerified: false,
  createdAt: new Date().toISOString(),
};

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHandedOff, setIsHandedOff] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isLoading || isHandedOff) return;

      const customerId = getCustomerId();
      const userMessage: Message = {
        id: generateId(),
        content: text,
        role: "user",
        sources: [],
        isVerified: false,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      const currentConvId = conversationId || generateId();
      if (!conversationId) setConversationId(currentConvId);

      try {
        abortRef.current = new AbortController();

        const request: SendMessageRequest = {
          conversation_id: currentConvId,
          customer_id: customerId,
          message: text,
        };

        const response = await fetch("/api/chat/send", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(request),
          signal: abortRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(
            response.status === 503
              ? "Service is temporarily unavailable. Please try again."
              : `Something went wrong (${response.status}). Please try again.`
          );
        }

        const data: SendMessageResponse = await response.json();
        setConversationId(data.conversation_id);

        const assistantMessage: Message = {
          id: generateId(),
          content: data.response_text,
          role: "assistant",
          sources: data.sources,
          isVerified: data.is_verified,
          createdAt: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);

        if (data.requires_handoff) {
          setIsHandedOff(true);
        }
      } catch (e) {
        if (e instanceof Error && e.name === "AbortError") return;
        setError(
          e instanceof Error
            ? e.message
            : "Unable to connect. Please check your connection and try again."
        );
      } finally {
        setIsLoading(false);
        abortRef.current = null;
      }
    },
    [conversationId, isLoading, isHandedOff]
  );

  const clearError = useCallback(() => setError(null), []);

  const resetChat = useCallback(() => {
    setMessages([WELCOME_MESSAGE]);
    setConversationId(null);
    setIsLoading(false);
    setError(null);
    setIsHandedOff(false);
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  return {
    messages,
    isLoading,
    error,
    isHandedOff,
    sendMessage,
    clearError,
    resetChat,
  };
}
