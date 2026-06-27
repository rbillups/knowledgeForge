"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { ChatMessageBubble } from "@/components/chat/ChatMessageBubble";
import { chatWithKnowledgeBase, getCollections } from "@/lib/api";
import {
  formatChatTimestamp,
  getChatErrorMessage,
  SUGGESTED_PROMPTS,
} from "@/lib/chat";
import type { Collection } from "@/types/collection";
import type { ChatMessage } from "@/types/chat";

const PORTFOLIO_SLUG = "portfolio";
const DEFAULT_RETRIEVAL_LIMIT = 5;

function createMessageId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function ChatInterface() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [selectedCollectionId, setSelectedCollectionId] = useState<number | null>(
    null,
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoadingCollections, setIsLoadingCollections] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);

  const loadCollections = useCallback(async () => {
    setIsLoadingCollections(true);
    setPageError(null);

    try {
      const nextCollections = await getCollections();
      setCollections(nextCollections);

      setSelectedCollectionId((current) => {
        if (
          current &&
          nextCollections.some((collection) => collection.id === current)
        ) {
          return current;
        }

        const portfolioCollection = nextCollections.find(
          (collection) => collection.slug === PORTFOLIO_SLUG,
        );

        return portfolioCollection?.id ?? nextCollections[0]?.id ?? null;
      });
    } catch {
      setPageError(
        "We could not load knowledge collections. Make sure the KnowledgeForge API is running and refresh the page.",
      );
    } finally {
      setIsLoadingCollections(false);
    }
  }, []);

  useEffect(() => {
    void loadCollections();
  }, [loadCollections]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const submitQuestion = async (question: string) => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isSending || !selectedCollectionId) {
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
      content: "Searching the knowledge base...",
      timestamp: formatChatTimestamp(),
    };

    setMessages((current) => [...current, userMessage, loadingMessage]);
    setInputValue("");
    setIsSending(true);

    try {
      const response = await chatWithKnowledgeBase(
        selectedCollectionId,
        trimmedQuestion,
        DEFAULT_RETRIEVAL_LIMIT,
      );

      const assistantMessage: ChatMessage = {
        id: createMessageId(),
        role: "assistant",
        content: response.answer,
        timestamp: formatChatTimestamp(),
        citations: response.citations,
        insufficientContext: response.insufficient_context,
      };

      setMessages((current) => [
        ...current.filter((message) => message.id !== loadingMessage.id),
        assistantMessage,
      ]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: createMessageId(),
        role: "assistant",
        content: getChatErrorMessage(error),
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

  const handleSuggestionClick = (prompt: string) => {
    setInputValue(prompt);
    void submitQuestion(prompt);
  };

  const selectedCollection = collections.find(
    (collection) => collection.id === selectedCollectionId,
  );

  const hasMessages = messages.length > 0;

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 bg-white px-6 py-4">
        <label className="block max-w-md">
          <span className="mb-1.5 block text-sm font-medium text-slate-700">
            Knowledge collection
          </span>
          <select
            value={selectedCollectionId ?? ""}
            onChange={(event) => setSelectedCollectionId(Number(event.target.value))}
            disabled={isLoadingCollections || collections.length === 0 || isSending}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition-colors focus:border-slate-400 disabled:cursor-not-allowed disabled:bg-slate-50"
          >
            {collections.length === 0 ? (
              <option value="">No collections available</option>
            ) : (
              collections.map((collection) => (
                <option key={collection.id} value={collection.id}>
                  {collection.name}
                </option>
              ))
            )}
          </select>
        </label>
        {selectedCollection?.description && (
          <p className="mt-2 max-w-2xl text-sm text-slate-500">
            {selectedCollection.description}
          </p>
        )}
      </div>

      {pageError && (
        <div className="border-b border-red-200 bg-red-50 px-6 py-3 text-sm text-red-700">
          {pageError}
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-6 py-6">
        {!hasMessages ? (
          <div className="mx-auto flex h-full max-w-2xl flex-col justify-center">
            <div className="rounded-xl border border-dashed border-slate-200 bg-white p-6 text-center shadow-sm">
              <h2 className="text-base font-semibold text-slate-900">
                Ask your knowledge base
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-500">
                Questions are answered using only the documents indexed in your
                selected collection, with source citations you can review.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {SUGGESTED_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => handleSuggestionClick(prompt)}
                    disabled={isSending || !selectedCollectionId}
                    className="rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-6">
            {messages.map((message) => (
              <ChatMessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="border-t border-slate-200 bg-white px-6 py-4">
        {hasMessages && (
          <div className="mb-3 flex flex-wrap gap-2">
            {SUGGESTED_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => handleSuggestionClick(prompt)}
                disabled={isSending || !selectedCollectionId}
                className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>
        )}

        <div className="flex items-end gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
          <textarea
            ref={textareaRef}
            rows={2}
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your knowledge base..."
            disabled={isSending || !selectedCollectionId || isLoadingCollections}
            className="flex-1 resize-none bg-transparent text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none disabled:cursor-not-allowed"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={
              isSending ||
              !selectedCollectionId ||
              isLoadingCollections ||
              !inputValue.trim()
            }
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Send message"
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
        <p className="mt-2 text-center text-xs text-slate-400">
          Press Enter to send · Shift+Enter for a new line
        </p>
      </div>
    </div>
  );
}
