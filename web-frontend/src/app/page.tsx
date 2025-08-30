"use client";
import React, { useState } from "react";
import { PromptInput } from "../components/PromptInput";
import { OutputCard } from "../components/OutputCard";
import { PromptHistory } from "../components/PromptHistory";
import { LoadingIndicator } from "../components/LoadingIndicator";

interface HistoryItem {
  prompt: string;
  response: string;
}

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [error, setError] = useState("");

  // Simula chamada à IA (mock)
  const fetchAIResponse = async (prompt: string) => {
    setLoading(true);
    setError("");
    setOutput("");
    // Simula delay e resposta mockada
    await new Promise((res) => setTimeout(res, 1200));
    // Aqui, integrar com API real futuramente
    const mockResponse = `Resposta simulada para: "${prompt}"`;
    setOutput(mockResponse);
    setHistory([{ prompt, response: mockResponse }, ...history]);
    setLoading(false);
  };

  const handlePromptSubmit = (p: string) => {
    setPrompt("");
    fetchAIResponse(p);
  };

  const handleHistorySelect = (item: HistoryItem) => {
    setPrompt(item.prompt);
    setOutput(item.response);
  };

  const handleHistoryDelete = (idx: number) => {
    setHistory(history.filter((_, i) => i !== idx));
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex flex-col">
      <header className="w-full py-4 px-6 bg-white dark:bg-gray-950 shadow flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Prompt Router IA</h1>
        {/* Dark mode toggle pode ser adicionado aqui futuramente */}
      </header>
      <main className="flex-1 flex flex-col md:flex-row gap-6 p-4 md:p-8 max-w-7xl mx-auto w-full">
        <section className="md:w-1/4 w-full mb-4 md:mb-0">
          <PromptHistory history={history} onSelect={handleHistorySelect} onDelete={handleHistoryDelete} />
        </section>
        <section className="flex-1 flex flex-col gap-4">
          <PromptInput onSubmit={handlePromptSubmit} loading={loading} />
          {loading && <LoadingIndicator />}
          {output && (
            <OutputCard
              output={output}
              loading={loading}
              onCopy={() => {
                navigator.clipboard.writeText(output);
              }}
              onExpand={() => {}}
              onSave={() => {}}
            />
          )}
        </section>
      </main>
      <footer className="w-full py-2 text-center text-xs text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-950">
        Prompt Router &copy; {new Date().getFullYear()} &mdash; Powered by Next.js, TailwindCSS & FastAPI
      </footer>
    </div>
  );
}
