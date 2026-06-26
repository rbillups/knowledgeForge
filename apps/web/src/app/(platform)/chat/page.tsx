import { ChatInterface } from "@/components/chat/ChatInterface";

export default function ChatPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 bg-white px-6 py-5">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Chat
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Ask questions and explore answers with source citations
        </p>
      </div>
      <div className="min-h-0 flex-1">
        <ChatInterface />
      </div>
    </div>
  );
}
