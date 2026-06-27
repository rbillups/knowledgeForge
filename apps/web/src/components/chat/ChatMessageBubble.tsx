import { CitationCard } from "@/components/chat/CitationCard";
import { INSUFFICIENT_CONTEXT_NOTE, POLICY_BLOCKED_NOTE } from "@/lib/chat";
import type { ChatMessage } from "@/types/chat";

type ChatMessageBubbleProps = {
  message: ChatMessage;
};

export function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
  const isUser = message.role === "user";
  const isLoading = message.role === "loading";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl ${isUser ? "items-end" : "items-start"} flex flex-col gap-2`}
      >
        <div className="flex items-center gap-2 px-1">
          <span className="text-xs font-medium text-slate-500">
            {isUser ? "You" : "KnowledgeForge"}
          </span>
          <span className="text-xs text-slate-400">{message.timestamp}</span>
        </div>

        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "bg-slate-900 text-white"
              : message.isError
                ? "border border-red-200 bg-red-50 text-red-700"
                : "border border-slate-200 bg-white text-slate-800"
          }`}
          aria-live={isLoading ? "polite" : undefined}
        >
          {isLoading ? (
            <span className="inline-flex items-center gap-2 text-slate-600">
              <span className="inline-flex gap-1" aria-hidden="true">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-400" />
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-400 [animation-delay:150ms]" />
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-400 [animation-delay:300ms]" />
              </span>
              {message.content}
            </span>
          ) : (
            message.content
          )}
        </div>

        {message.policyBlocked && !message.isError && (
          <p className="px-1 text-xs text-slate-500">{POLICY_BLOCKED_NOTE}</p>
        )}

        {message.insufficientContext && !message.isError && !message.policyBlocked && (
          <p className="px-1 text-xs text-slate-500">{INSUFFICIENT_CONTEXT_NOTE}</p>
        )}

        {message.citations &&
          message.citations.length > 0 &&
          !message.policyBlocked && (
          <div className="w-full space-y-2 pt-1">
            <p className="px-1 text-xs font-medium uppercase tracking-wide text-slate-400">
              Sources
            </p>
            {message.citations.map((citation, index) => (
              <CitationCard
                key={`${citation.filename}-${citation.chunk_index}-${index}`}
                citation={citation}
                index={index + 1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
