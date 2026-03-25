"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import type {
  Message,
  StreamChunk,
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

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHandedOff, setIsHandedOff] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

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
      if (!conversationId) {
        setConversationId(currentConvId);
      }

      // Try WebSocket streaming first, fall back to REST
      try {
        await sendViaWebSocket(currentConvId, customerId, text);
      } catch {
        try {
          await sendViaRest(currentConvId, customerId, text);
        } catch (e) {
          setError(e instanceof Error ? e.message : "Failed to send message");
        }
      }

      setIsLoading(false);
    },
    [conversationId, isLoading, isHandedOff]
  );

  async function sendViaWebSocket(
    convId: string,
    customerId: string,
    text: string
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(
        `${protocol}//${window.location.host}/api/chat/ws/${convId}`
      );
      wsRef.current = ws;

      let assistantContent = "";
      const assistantId = generateId();

      // Add placeholder assistant message
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          content: "",
          role: "assistant",
          sources: [],
          isVerified: false,
          createdAt: new Date().toISOString(),
        },
      ]);

      ws.onopen = () => {
        ws.send(JSON.stringify({ customer_id: customerId, message: text }));
      };

      ws.onmessage = (event) => {
        const chunk: StreamChunk = JSON.parse(event.data);
        setConversationId(chunk.conversation_id);

        if (chunk.is_final) {
          // Update final message with sources and metadata
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    content: assistantContent,
                    sources: chunk.sources,
                    isVerified: chunk.sources.length > 0,
                  }
                : m
            )
          );
          if (chunk.requires_handoff) {
            setIsHandedOff(true);
          }
          ws.close();
          resolve();
        } else {
          assistantContent += chunk.chunk;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: assistantContent } : m
            )
          );
        }
      };

      ws.onerror = () => {
        // Remove placeholder and reject to trigger REST fallback
        setMessages((prev) => prev.filter((m) => m.id !== assistantId));
        ws.close();
        reject(new Error("WebSocket failed"));
      };

      ws.onclose = (event) => {
        if (!event.wasClean && assistantContent === "") {
          setMessages((prev) => prev.filter((m) => m.id !== assistantId));
          reject(new Error("WebSocket closed unexpectedly"));
        }
      };
    });
  }

  async function sendViaRest(
    convId: string,
    customerId: string,
    text: string
  ): Promise<void> {
    const request: SendMessageRequest = {
      conversation_id: convId,
      customer_id: customerId,
      message: text,
    };

    const response = await fetch("/api/chat/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
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
  }

  const toggleWidget = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    conversationId,
    isLoading,
    isOpen,
    error,
    isHandedOff,
    sendMessage,
    toggleWidget,
    clearError,
  };
}
