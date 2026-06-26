import { CitationCard } from "@/components/chat/CitationCard";
import type { ChatMessage } from "@/types/chat";

type ChatMessageBubbleProps = {
  message: ChatMessage;
};

export function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
  const isUser = message.role === "user";

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
              : "border border-slate-200 bg-white text-slate-800"
          }`}
        >
          {message.content}
        </div>
        {message.citations && message.citations.length > 0 && (
          <div className="w-full space-y-2 pt-1">
            <p className="px-1 text-xs font-medium uppercase tracking-wide text-slate-400">
              Sources
            </p>
            {message.citations.map((citation, index) => (
              <CitationCard
                key={citation.id}
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
