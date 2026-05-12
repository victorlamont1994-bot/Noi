"use client";

import { FormEvent, useMemo, useState } from "react";

type Role = "user" | "assistant";
type ChatMessage = { role: Role; content: string };

const RECENT_HISTORY_LIMIT = 12;

export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSend = useMemo(() => input.trim().length > 0 && !isLoading, [input, isLoading]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!canSend) return;

    const userMessage: ChatMessage = { role: "user", content: input.trim() };
    const nextMessages = [...messages, userMessage];

    setMessages(nextMessages);
    setInput("");
    setError(null);
    setIsLoading(true);

    const assistantIndex = nextMessages.length;
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages.slice(-RECENT_HISTORY_LIMIT) }),
      });

      if (!response.ok || !response.body) {
        throw new Error("The assistant tripped over its own punchline. Please retry.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        if (!chunk) continue;

        setMessages((prev) => {
          const copy = [...prev];
          const current = copy[assistantIndex];
          if (!current) return prev;
          copy[assistantIndex] = { ...current, content: current.content + chunk };
          return copy;
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setMessages((prev) => prev.filter((_, index) => index !== assistantIndex));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-4 p-4">
      <h1 className="text-2xl font-semibold">Spontaneous Assistant</h1>

      <section className="flex-1 space-y-3 overflow-y-auto rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        {messages.length === 0 ? (
          <p className="text-slate-400">Say hi. It has opinions.</p>
        ) : (
          messages.map((message, idx) => (
            <article
              key={`${message.role}-${idx}`}
              className={`max-w-[90%] rounded-xl px-3 py-2 text-sm ${
                message.role === "user"
                  ? "ml-auto bg-indigo-500 text-white"
                  : "bg-slate-800 text-slate-100"
              }`}
            >
              {message.content || (message.role === "assistant" && isLoading ? "…" : "")}
            </article>
          ))
        )}
      </section>

      {error && <p className="rounded-md border border-red-600/40 bg-red-600/10 p-2 text-sm text-red-300">{error}</p>}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none ring-indigo-400 focus:ring-2"
        />
        <button
          type="submit"
          disabled={!canSend}
          className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Thinking…" : "Send"}
        </button>
      </form>
    </main>
  );
}
