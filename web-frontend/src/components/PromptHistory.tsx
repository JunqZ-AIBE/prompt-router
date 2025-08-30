import React from 'react';

interface HistoryItem {
  prompt: string;
  response: string;
}

interface PromptHistoryProps {
  history: HistoryItem[];
  onSelect: (item: HistoryItem) => void;
  onDelete: (idx: number) => void;
}

export const PromptHistory: React.FC<PromptHistoryProps> = ({ history, onSelect, onDelete }) => {
  return (
    <aside className="w-full md:w-64 bg-gray-50 dark:bg-gray-800 p-4 rounded-lg shadow h-full overflow-y-auto max-h-[60vh]">
      <h2 className="font-bold mb-2 text-gray-700 dark:text-gray-200">Histórico</h2>
      <ul className="space-y-2">
        {history.length === 0 && <li className="text-gray-400">Nenhum prompt enviado ainda.</li>}
        {history.map((item, idx) => (
          <li key={idx} className="flex flex-col gap-1 bg-white dark:bg-gray-900 rounded p-2 shadow-sm hover:shadow-md transition group">
            <div className="flex justify-between items-center">
              <button
                className="text-left flex-1 truncate hover:underline text-blue-700 dark:text-blue-300"
                onClick={() => onSelect(item)}
                title="Re-enviar prompt"
              >
                {item.prompt}
              </button>
              <button
                className="text-red-500 hover:text-red-700 ml-2 text-xs"
                onClick={() => onDelete(idx)}
                aria-label="Remover"
                title="Remover do histórico"
              >
                ×
              </button>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{item.response}</div>
          </li>
        ))}
      </ul>
    </aside>
  );
};
