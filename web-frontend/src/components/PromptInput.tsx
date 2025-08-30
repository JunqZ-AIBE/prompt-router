import React, { useState, KeyboardEvent } from 'react';

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  loading?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({ onSubmit, loading }) => {
  const [value, setValue] = useState('');

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !loading) {
        onSubmit(value.trim());
        setValue('');
      }
    }
  };

  const handleSend = () => {
    if (value.trim() && !loading) {
      onSubmit(value.trim());
      setValue('');
    }
  };

  return (
    <div className="w-full flex flex-col gap-2">
      <textarea
        className="w-full p-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 transition min-h-[80px]"
        placeholder="Digite seu prompt aqui..."
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
        rows={3}
        aria-label="Prompt"
      />
      <div className="flex justify-end">
        <button
          className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
          onClick={handleSend}
          disabled={loading || !value.trim()}
        >
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
};
