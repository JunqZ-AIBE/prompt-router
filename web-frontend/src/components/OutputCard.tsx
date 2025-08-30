import React from 'react';

interface OutputCardProps {
  output: string;
  loading?: boolean;
  error?: string;
  onCopy?: () => void;
  onExpand?: () => void;
  onSave?: () => void;
}

export const OutputCard: React.FC<OutputCardProps> = ({ output, loading, error, onCopy, onExpand, onSave }) => {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-4 mt-4 min-h-[100px] relative transition">
      {loading ? (
        <div className="flex items-center justify-center h-20">
          <span className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-2"></span>
          <span className="text-blue-600">Processando...</span>
        </div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-100 break-words">{output}</pre>
      )}
      <div className="absolute top-2 right-2 flex gap-2">
        <button onClick={onCopy} className="text-xs text-blue-600 hover:underline" title="Copiar">📋</button>
        <button onClick={onExpand} className="text-xs text-blue-600 hover:underline" title="Expandir">⤢</button>
        <button onClick={onSave} className="text-xs text-blue-600 hover:underline" title="Salvar">💾</button>
      </div>
    </div>
  );
};
