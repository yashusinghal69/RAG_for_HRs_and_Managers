"use client";

import React, { useState, useEffect, useRef } from "react";
import { RefreshCcwIcon, CopyIcon, MicIcon } from "lucide-react";
import { Actions, Action } from "@/components/ai-elements/actions";
import { Message, MessageContent } from "@/components/ai-elements/message";
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputSubmit,
  PromptInputToolbar,
  PromptInputTools,
  PromptInputButton,
} from "@/components/ai-elements/prompt-input";
import { Response } from "@/components/ai-elements/response";
import { Suggestion, Suggestions } from "@/components/ai-elements/suggestion";
import {
  Source,
  Sources,
  SourcesContent,
  SourcesTrigger,
} from "@/components/ai-elements/source";
import { Loader } from "@/components/ai-elements/loader";
import { Button } from "@/components/ui/button";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Array<{
    source: string;
    page: number;
    section: string;
  }>;
  confidence_score?: number;
  confidence_level?: string;
}

interface HRChatDashboardProps {
  userRole: string;
  activeChat?: string;
  onSendMessage?: (
    query: string,
    userRole: string
  ) => Promise<WorkflowResponse>;
  onChatCreated?: (title: string) => string | null;
  isNewChat?: boolean;
}

interface WorkflowResponse {
  success: boolean;
  data?: {
    answer: string;
    sources: Array<{
      source: string;
      page: number;
      section: string;
    }>;
    confidence_score: number;
    confidence_level: string;
  };
  error?: string;
}

const hrSuggestions = [
  "What is the company match for the 401(k) retirement plan?",
  "How many weeks of fully paid leave is a primary caregiver entitled to for parental leave?",
  "In what year was NovaCorp founded?",
  "What is the standard duration of a Performance Improvement Plan (PIP)?",
  "What is the code name for the active $200M SaaS acquisition project?",
  "How long is the consideration period for a release agreement under the ADEA for a group termination?",
  "By what date must managers complete their team's annual performance reviews?",
];

export function HRChatDashboard({
  userRole,
  activeChat,
  onChatCreated,
  isNewChat = true,
}: HRChatDashboardProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Load messages from localStorage when activeChat changes
  useEffect(() => {
    if (activeChat && activeChat !== "new") {
      const savedMessages = localStorage.getItem(`hr-chat-${activeChat}`);
      if (savedMessages) {
        try {
          const parsed = JSON.parse(savedMessages);
          setMessages(parsed);
        } catch (error) {
          console.error("Error loading messages:", error);
        }
      }
    } else {
      // Clear messages for new chat
      setMessages([]);
    }
  }, [activeChat]);

  // Save messages to localStorage whenever they change and we have an active chat
  useEffect(() => {
    if (activeChat && activeChat !== "new" && messages.length > 0) {
      localStorage.setItem(`hr-chat-${activeChat}`, JSON.stringify(messages));
    }
  }, [messages, activeChat]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    console.log("🚀 Submit handler called with:", {
      activeChat,
      input,
      messagesLength: messages.length,
      userRole,
    });

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
    };

    // If this is a new chat, create a new chat session first
    let currentChatId = activeChat;
    if (!activeChat || activeChat === "new" || messages.length === 0) {
      console.log("📝 Creating new chat session");
      if (onChatCreated) {
        const chatTitle =
          input.length > 30 ? input.substring(0, 30) + "..." : input;
        const newChatId = onChatCreated(chatTitle);
        currentChatId = newChatId || undefined;
        console.log("✅ New chat created with ID:", currentChatId);
      }
    }

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    console.log("🔄 Starting API call to backend...");

    try {
      // We'll add the assistant message only when we get a response
      const assistantMessageId = `assistant-${Date.now()}`;

      // Call Render FastAPI directly (no proxy needed)
      console.log("📡 Calling Render FastAPI directly with payload:", {
        query: currentInput,
        user_id: userRole,
      });

      // Get FastAPI URL from environment or use localhost for development
      const FASTAPI_URL =
        process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000";

      const response = await fetch(`${FASTAPI_URL}/api/workflow`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: currentInput,
          user_id: userRole,
        }),
      });

      console.log("📥 Response status:", response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("✅ Backend response:", result);

      if (result.success && result.data) {
        console.log("🎯 Adding response message");
        // Add the assistant message with the response
        const assistantMessage: ChatMessage = {
          id: assistantMessageId,
          role: "assistant",
          content: result.data.answer,
          sources: result.data.sources,
          confidence_score: result.data.confidence_score,
          confidence_level: result.data.confidence_level,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        console.log("❌ Backend returned error:", result);
        // Add error message
        const errorMessage: ChatMessage = {
          id: assistantMessageId,
          role: "assistant",
          content: `Sorry, I encountered an error: ${
            result.error || "Unknown error occurred"
          }`,
        };

        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Error calling backend:", error);
      // Add error message
      const errorMessage: ChatMessage = {
        id: `assistant-error-${Date.now()}`,
        role: "assistant",
        content:
          "Sorry, I could not connect to the server. Please try again later.",
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    // Create a synthetic form event and submit
    setTimeout(() => {
      const syntheticEvent = { preventDefault: () => {} } as React.FormEvent;
      handleSubmit(syntheticEvent);
    }, 100);
  };

  const handleCopyMessage = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      // You could add a toast notification here
    } catch (error) {
      console.error("Failed to copy message:", error);
    }
  };

  const handleRegenerateLastMessage = async () => {
    if (messages.length < 2) return;

    const lastUserMessage = messages
      .slice()
      .reverse()
      .find((msg) => msg.role === "user");

    if (lastUserMessage) {
      // Remove the last assistant message and regenerate
      setMessages((prev) =>
        prev.filter(
          (msg) =>
            !(
              msg.role === "assistant" &&
              msg.id === messages[messages.length - 1].id
            )
        )
      );

      setInput(lastUserMessage.content);
      setTimeout(() => {
        handleSubmit({ preventDefault: () => {} } as React.FormEvent);
      }, 100);
    }
  };

  const getSourceUrl = (source: {
    source: string;
    page: number;
    section: string;
  }) => {
    // Create a meaningful URL or identifier for the source
    return `#${source.source}-page-${source.page}`;
  };

  const renderMessage = (message: ChatMessage, messageIndex: number) => {
    const isLastMessage = messageIndex === messages.length - 1;

    return (
      <div key={message.id}>
        {/* Sources for assistant messages */}
        {message.role === "assistant" &&
          message.sources &&
          message.sources.length > 0 && (
            <Sources>
              <SourcesTrigger count={Math.min(message.sources.length, 3)} />
              <SourcesContent>
                {message.sources.slice(0, 3).map((source, i) => (
                  <Source
                    key={`${message.id}-source-${i}`}
                    href={getSourceUrl(source)}
                    title={`${source.source} - Page ${source.page}`}
                  />
                ))}
              </SourcesContent>
            </Sources>
          )}

        <Message from={message.role}>
          <MessageContent>
            <div>
              <Response>{message.content}</Response>

              {/* Confidence indicator for assistant messages */}
              {message.role === "assistant" && message.confidence_level && (
                <div className="mt-2 text-xs text-muted-foreground">
                  Confidence: {message.confidence_level}
                  {message.confidence_score &&
                    ` (${Math.round(message.confidence_score * 100)}%)`}
                </div>
              )}

              {/* Actions for the last assistant message */}
              {message.role === "assistant" && isLastMessage && (
                <Actions className="mt-3">
                  <Action
                    onClick={handleRegenerateLastMessage}
                    label="Regenerate"
                  >
                    <RefreshCcwIcon className="size-3" />
                  </Action>
                  <Action
                    onClick={() => handleCopyMessage(message.content)}
                    label="Copy"
                  >
                    <CopyIcon className="size-3" />
                  </Action>
                </Actions>
              )}
            </div>
          </MessageContent>
        </Message>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* Show suggestions when no messages */}
      {messages.length === 0 && (
        <div className="flex flex-col h-full">
          {/* Welcome section - reduced height */}
          <div className="flex flex-col items-center justify-center flex-1 p-6 pb-2">
            <div className="text-center">
              <h1 className="text-2xl font-bold mb-2">
                Welcome to NovaCorp HR Assistant
              </h1>
              <p className="text-muted-foreground">
                Ask me anything about HR policies, procedures, and guidelines.
              </p>
            </div>
          </div>

          {/* Suggestions section - positioned just above input */}
          <div className="px-4 pb-2">
            <Suggestions className="max-w-4xl mx-auto">
              {hrSuggestions.map((suggestion) => (
                <Suggestion
                  key={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                  suggestion={suggestion}
                />
              ))}
            </Suggestions>
          </div>
        </div>
      )}

      {/* Chat conversation */}
      {messages.length > 0 && (
        <Conversation className="flex-1 min-h-0">
          <ConversationContent>
            {messages.map((message, index) => renderMessage(message, index))}

            {/* Loading indicator */}
            {isLoading && (
              <Message from="assistant">
                <MessageContent>
                  <div className="flex items-center gap-2">
                    <Loader />
                    <span className="text-muted-foreground text-sm">
                      Searching knowledge base...
                    </span>
                  </div>
                </MessageContent>
              </Message>
            )}
          </ConversationContent>
          <ConversationScrollButton />
        </Conversation>
      )}

      {/* Input area - reduced padding and size */}
      <div className="p-3 border-t">
        <PromptInput onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <PromptInputTextarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask NovaCorp HR anything..."
            disabled={isLoading}
            className="min-h-[30px] text-sm"
          />
          <PromptInputToolbar>
            <PromptInputTools>
              <PromptInputButton>
                <MicIcon size={16} />
              </PromptInputButton>
            </PromptInputTools>
            <PromptInputSubmit
              disabled={!input.trim() || isLoading}
              status={isLoading ? "streaming" : "ready"}
            />
          </PromptInputToolbar>
        </PromptInput>
      </div>
    </div>
  );
}
