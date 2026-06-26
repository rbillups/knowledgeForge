import { mockChatMessages, suggestedPrompts } from "@/data/mock/chat";
import { ChatMessageBubble } from "@/components/chat/ChatMessageBubble";

export function ChatInterface() {
  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-6 overflow-y-auto px-6 py-6">
        {mockChatMessages.map((message) => (
          <ChatMessageBubble key={message.id} message={message} />
        ))}
      </div>

      <div className="border-t border-slate-200 bg-white px-6 py-4">
        <div className="mb-3 flex flex-wrap gap-2">
          {suggestedPrompts.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50"
            >
              {prompt}
            </button>
          ))}
        </div>
        <div className="flex items-end gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
          <textarea
            rows={2}
            placeholder="Ask a question about your knowledge base..."
            disabled
            className="flex-1 resize-none bg-transparent text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none disabled:cursor-not-allowed"
          />
          <button
            type="button"
            disabled
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white disabled:opacity-50"
            aria-label="Send message"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
            </svg>
          </button>
        </div>
        <p className="mt-2 text-center text-xs text-slate-400">
          Chat is not yet connected. Responses shown are mock data with source citations.
        </p>
      </div>
    </div>
  );
}
