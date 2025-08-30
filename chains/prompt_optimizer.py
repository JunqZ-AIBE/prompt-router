"""
Otimizador de Prompts do Prompt Router
Responsável por otimizar prompts para diferentes LLMs

Este módulo contém a lógica de otimização de prompts baseada no LLM de destino,
aplicando as melhores práticas específicas de cada modelo.
"""

import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.logger import LoggerMixin, log_execution_time

class PromptOptimizer(LoggerMixin):
    """
    Classe responsável por otimizar prompts para diferentes LLMs
    
    Cada LLM tem suas próprias características e melhores práticas.
    Esta classe aplica otimizações específicas baseadas no destino.
    """
    
    def __init__(self, settings):
        """
        Inicializa o otimizador de prompts
        
        Args:
            settings: Instância de Settings com configurações do sistema
        """
        super().__init__()
        self.settings = settings
        self.templates_dir = settings.TEMPLATES_DIR
        
        # Carrega padrões de otimização
        self._load_optimization_patterns()
        
        self.logger.info("PromptOptimizer inicializado")
    
    def _load_optimization_patterns(self):
        """Carrega padrões de otimização para cada LLM"""
        
        # Padrões de otimização para Claude
        self.claude_patterns = {
            'prefer_structured': True,
            'use_xml_tags': True,
            'max_context_length': 200000,
            'temperature_range': (0.0, 1.0),
            'system_prompt_support': True,
            'function_calling': True
        }
        
        # Padrões de otimização para OpenAI
        self.openai_patterns = {
            'prefer_structured': True,
            'use_json_mode': True,
            'max_context_length': 128000,
            'temperature_range': (0.0, 2.0),
            'system_prompt_support': True,
            'function_calling': True
        }
        
        # Padrões de otimização para Cursor (placeholder)
        self.cursor_patterns = {
            'prefer_structured': True,
            'code_focused': True,
            'max_context_length': 32000,
            'temperature_range': (0.0, 1.0),
            'system_prompt_support': False,  # Placeholder
            'function_calling': False  # Placeholder
        }
    
    @log_execution_time
    def optimize(self, prompt: str, target_llm: str = 'universal') -> str:
        """
        Otimiza um prompt para o LLM especificado
        
        Args:
            prompt: Prompt original a ser otimizado
            target_llm: LLM de destino (claude, openai, cursor, universal)
            
        Returns:
            Prompt otimizado
        """
        
        self.logger.info(f"Iniciando otimização para {target_llm}")
        
        # Aplica otimizações gerais primeiro
        optimized_prompt = self._apply_general_optimizations(prompt)
        
        # Aplica otimizações específicas do LLM
        if target_llm.lower() == 'claude':
            optimized_prompt = self._optimize_for_claude(optimized_prompt)
        elif target_llm.lower() == 'openai':
            optimized_prompt = self._optimize_for_openai(optimized_prompt)
        elif target_llm.lower() == 'cursor':
            optimized_prompt = self._optimize_for_cursor(optimized_prompt)
        elif target_llm.lower() == 'universal':
            optimized_prompt = self._optimize_universal(optimized_prompt)
        
        self.logger.info(f"Otimização concluída. Tamanho: {len(optimized_prompt)} chars")
        return optimized_prompt
    
    def _apply_general_optimizations(self, prompt: str) -> str:
        """
        Aplica otimizações gerais válidas para todos os LLMs
        
        Args:
            prompt: Prompt original
            
        Returns:
            Prompt com otimizações gerais aplicadas
        """
        
        # Remove espaços extras e quebras de linha desnecessárias
        prompt = re.sub(r'\n\s*\n', '\n\n', prompt)  # Remove linhas em branco extras
        prompt = re.sub(r'[ \t]+', ' ', prompt)      # Remove espaços extras
        prompt = prompt.strip()                       # Remove espaços do início/fim
        
        # Garante que o prompt termine com um ponto final ou dois pontos
        if not prompt.endswith(('.', ':', '?', '!')):
            prompt += '.'
        
        return prompt
    
    def _optimize_for_claude(self, prompt: str) -> str:
        """
        Otimizações específicas para Claude/Anthropic
        
        Args:
            prompt: Prompt a ser otimizado
            
        Returns:
            Prompt otimizado para Claude
        """
        
        self.logger.debug("Aplicando otimizações para Claude")
        
        # Claude funciona bem com estrutura clara e tags XML
        if not any(tag in prompt.lower() for tag in ['<thinking>', '<instructions>', '<context>']):
            # Adiciona estrutura se não estiver presente
            structured_prompt = f"""<instructions>
{prompt}
</instructions>

<thinking>
Vou analisar esta solicitação cuidadosamente e fornecer uma resposta detalhada e útil.
</thinking>"""
            
            return structured_prompt
        
        return prompt
    
    def _optimize_for_openai(self, prompt: str) -> str:
        """
        Otimizações específicas para OpenAI GPT
        
        Args:
            prompt: Prompt a ser otimizado
            
        Returns:
            Prompt otimizado para OpenAI
        """
        
        self.logger.debug("Aplicando otimizações para OpenAI")
        
        # OpenAI funciona bem com prompts diretos e específicos
        # Adiciona contexto de role se não estiver presente
        if not prompt.lower().startswith(('você é', 'atue como', 'role:')):
            optimized = f"Você é um assistente especializado e útil. {prompt}"
            return optimized
        
        return prompt
    
    def _optimize_for_cursor(self, prompt: str) -> str:
        """
        Otimizações específicas para Cursor
        
        Args:
            prompt: Prompt a ser otimizado
            
        Returns:
            Prompt otimizado para Cursor
        """
        
        self.logger.debug("Aplicando otimizações para Cursor")
        
        # Cursor é focado em código - adiciona contexto de programação
        if not any(keyword in prompt.lower() for keyword in ['código', 'code', 'função', 'class', 'def']):
            # Se não é um prompt de código, mantém simples
            return prompt
        
        # Para prompts de código, adiciona contexto específico
        code_context = """Como um assistente de desenvolvimento experiente, considere:
- Melhores práticas de código
- Legibilidade e manutenibilidade
- Padrões da linguagem
- Comentários explicativos quando necessário

"""
        
        return code_context + prompt
    
    def _optimize_universal(self, prompt: str) -> str:
        """
        Otimizações para prompt universal (compatível com todos os LLMs)
        
        Args:
            prompt: Prompt a ser otimizado
            
        Returns:
            Prompt otimizado universalmente
        """
        
        self.logger.debug("Aplicando otimizações universais")
        
        # Adiciona estrutura básica que funciona bem com todos os LLMs
        universal_prompt = f"""Por favor, analise cuidadosamente a seguinte solicitação e forneça uma resposta detalhada, precisa e útil:

{prompt}

Responda de forma estruturada e clara, considerando o contexto e os detalhes fornecidos."""
        
        return universal_prompt
    
    def get_optimization_stats(self, original: str, optimized: str) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre a otimização realizada
        
        Args:
            original: Prompt original
            optimized: Prompt otimizado
            
        Returns:
            Dicionário com estatísticas da otimização
        """
        
        stats = {
            'original_length': len(original),
            'optimized_length': len(optimized),
            'length_change': len(optimized) - len(original),
            'original_words': len(original.split()),
            'optimized_words': len(optimized.split()),
            'words_change': len(optimized.split()) - len(original.split()),
            'has_structure': any(tag in optimized.lower() for tag in ['<', '```', '###', '---']),
            'improvement_ratio': len(optimized) / len(original) if len(original) > 0 else 1.0
        }
        
        return stats
