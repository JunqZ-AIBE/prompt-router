import React from 'react';

export const LoadingIndicator: React.FC = () => (
  <div className="flex items-center justify-center h-12">
    <span className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></span>
    <span className="ml-2 text-blue-600">Processando...</span>
  </div>
);
