"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { ChatMessageBubble } from "@/components/chat/ChatMessageBubble";
import { HowItWorksSection } from "@/components/public/HowItWorksSection";
import { chatWithPublicPortfolio } from "@/lib/api";
import { formatChatTimestamp } from "@/lib/chat";
import {
  getPublicPortfolioChatErrorMessage,
  PUBLIC_INSUFFICIENT_CONTEXT_NOTE,
  PUBLIC_PORTFOLIO_INCOMPLETE_NOTE,
  PUBLIC_PORTFOLIO_INTRO,
  PUBLIC_PORTFOLIO_PROMPTS,
} from "@/lib/public-portfolio";
import type { ChatMessage } from "@/types/chat";

const DEFAULT_RETRIEVAL_LIMIT = 5;

function createMessageId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function PortfolioAskInterface() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const submitQuestion = async (question: string) => {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || isSending) {
      return;
    }

    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      content: trimmedQuestion,
      timestamp: formatChatTimestamp(),
    };

    const loadingMessage: ChatMessage = {
      id: createMessageId(),
      role: "loading",
      content: "Searching public portfolio materials...",
      timestamp: formatChatTimestamp(),
    };

    setMessages((current) => [...current, userMessage, loadingMessage]);
    setInputValue("");
    setIsSending(true);

    try {
      const response = await chatWithPublicPortfolio(
        trimmedQuestion,
        DEFAULT_RETRIEVAL_LIMIT,
      );

      const assistantMessage: ChatMessage = {
        id: createMessageId(),
        role: "assistant",
        content: response.answer,
        timestamp: formatChatTimestamp(),
        question: trimmedQuestion,
        citations: response.citations,
        insufficientContext: response.insufficient_context,
        policyBlocked: response.policy_blocked,
      };

      setMessages((current) => [
        ...current.filter((message) => message.id !== loadingMessage.id),
        assistantMessage,
      ]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: createMessageId(),
        role: "assistant",
        content: getPublicPortfolioChatErrorMessage(error),
        timestamp: formatChatTimestamp(),
        isError: true,
      };

      setMessages((current) => [
        ...current.filter((message) => message.id !== loadingMessage.id),
        errorMessage,
      ]);
    } finally {
      setIsSending(false);
      textareaRef.current?.focus();
    }
  };

  const handleSend = () => {
    void submitQuestion(inputValue);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 bg-white px-6 py-5">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Ask About My Work
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-600">
          {PUBLIC_PORTFOLIO_INTRO}
        </p>
        <p className="mt-2 max-w-3xl text-xs text-slate-500">
          {PUBLIC_PORTFOLIO_INCOMPLETE_NOTE}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
          <div>
            {!hasMessages ? (
              <div className="rounded-xl border border-dashed border-slate-200 bg-white p-6 text-center shadow-sm">
                <p className="text-sm text-slate-500">
                  Ask a question about public projects, skills, experience, or
                  career focus.
                </p>
                <div className="mt-4 flex flex-wrap justify-center gap-2">
                  {PUBLIC_PORTFOLIO_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      onClick={() => void submitQuestion(prompt)}
                      disabled={isSending}
                      className="rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message) => (
                  <ChatMessageBubble
                    key={message.id}
                    message={message}
                    collectionId={null}
                    onFeedbackSubmitted={() => undefined}
                    insufficientContextNote={PUBLIC_INSUFFICIENT_CONTEXT_NOTE}
                    citationsPresentation="collapsed"
                  />
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <div className="hidden lg:block">
            <HowItWorksSection />
          </div>
        </div>

        {!hasMessages && (
          <div className="mx-auto mt-6 max-w-5xl lg:hidden">
            <HowItWorksSection />
          </div>
        )}
      </div>

      <div className="border-t border-slate-200 bg-white px-6 py-4">
        {hasMessages && (
          <div className="mx-auto mb-3 flex max-w-3xl flex-wrap gap-2">
            {PUBLIC_PORTFOLIO_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => void submitQuestion(prompt)}
                disabled={isSending}
                className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>
        )}

        <div className="mx-auto flex max-w-3xl items-end gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
          <textarea
            ref={textareaRef}
            rows={2}
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about public projects, skills, or experience..."
            disabled={isSending}
            className="flex-1 resize-none bg-transparent text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none disabled:cursor-not-allowed"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={isSending || !inputValue.trim()}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Send question"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
