export interface Message {
  id: string;
  content: string;
  role: "user" | "assistant" | "system";
  sources: string[];
  isVerified: boolean;
  createdAt: string;
}

export interface Conversation {
  id: string;
  customerId: string;
  messages: Message[];
  status: "active" | "handed_off" | "closed";
}

export interface StreamChunk {
  conversation_id: string;
  chunk: string;
  is_final: boolean;
  sources: string[];
  requires_handoff: boolean;
}

export interface SendMessageRequest {
  conversation_id: string | null;
  customer_id: string;
  message: string;
}

export interface SendMessageResponse {
  conversation_id: string;
  response_text: string;
  sources: string[];
  is_verified: boolean;
  requires_handoff: boolean;
}
