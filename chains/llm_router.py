"""
Roteador de LLMs do Prompt Router
Responsável por rotear prompts otimizados para diferentes LLMs

Este módulo gerencia o roteamento inteligente de prompts para Claude, OpenAI e Cursor,
aplicando templates específicos e formatação adequada para cada modelo.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from utils.logger import LoggerMixin, log_execution_time

class LLMRouter(LoggerMixin):
    """
    Classe responsável por rotear prompts para diferentes LLMs
    
    Gerencia templates, formatação e preparação de prompts
    para envio para Claude, OpenAI, Cursor ou formato universal.
    """
    
    def __init__(self, settings):
        """
        Inicializa o roteador de LLMs
        
        Args:
            settings: Instância de Settings com configurações do sistema
        """
        super().__init__()
        self.settings = settings
        self.templates_dir = settings.TEMPLATES_DIR
        
        # Cache de templates carregados
        self._template_cache = {}
        
        # Carrega configurações de roteamento
        self._load_routing_rules()
        
        self.logger.info("LLMRouter inicializado")
    
    def _load_routing_rules(self):
        """Carrega regras de roteamento para diferentes tipos de prompt"""
        
        self.routing_rules = {
            # Regras para detecção automática de melhor LLM
            'claude_indicators': [
                'análise detalhada', 'pensamento crítico', 'contexto complexo',
                'raciocínio', 'argumentação', 'análise profunda'
            ],
            'openai_indicators': [
                'creative writing', 'brainstorm', 'ideias criativas',
                'storytelling', 'marketing', 'copywriting'
            ],
            'cursor_indicators': [
                'código', 'programação', 'debug', 'função', 'class',
                'algoritmo', 'refatoração', 'code review'
            ]
        }
    
    @log_execution_time
    def route_prompt(self, prompt: str, target: str = 'auto') -> Dict[str, Any]:
        """
        Roteia um prompt para o LLM apropriado
        
        Args:
            prompt: Prompt otimizado para roteamento
            target: LLM de destino ('claude', 'openai', 'cursor', 'universal', 'auto')
            
        Returns:
            Dicionário com prompt formatado e metadados de roteamento
        """
        
        self.logger.info(f"Iniciando roteamento para target: {target}")
        
        # Determina o target automaticamente se solicitado
        if target == 'auto':
            target = self._determine_best_llm(prompt)
            self.logger.info(f"Target determinado automaticamente: {target}")
        
        # Aplica template específico do LLM
        template_name = f"{target}_template"
        template = self._load_template(template_name)
        
        if template:
            formatted_prompt = self._apply_template(template, prompt)
        else:
            # Fallback para formatação básica
            formatted_prompt = self._format_basic(prompt, target)
        
        # Prepara resultado com metadados
        result = {
            'formatted_prompt': formatted_prompt,
            'target_llm': target,
            'template_used': template_name if template else 'basic_format',
            'timestamp': datetime.now().isoformat(),
            'prompt_length': len(formatted_prompt),
            'original_length': len(prompt),
            'metadata': self._generate_metadata(prompt, target)
        }
        
        self.logger.info(f"Roteamento concluído para {target}")
        return result
    
    def _determine_best_llm(self, prompt: str) -> str:
        """
        Determina automaticamente o melhor LLM baseado no conteúdo do prompt
        
        Args:
            prompt: Prompt para análise
            
        Returns:
            Nome do LLM mais adequado
        """
        
        prompt_lower = prompt.lower()
        
        # Conta indicadores para cada LLM
        claude_score = sum(1 for indicator in self.routing_rules['claude_indicators'] 
                          if indicator in prompt_lower)
        openai_score = sum(1 for indicator in self.routing_rules['openai_indicators'] 
                          if indicator in prompt_lower)
        cursor_score = sum(1 for indicator in self.routing_rules['cursor_indicators'] 
                          if indicator in prompt_lower)
        
        # Determina o LLM com maior score
        scores = {
            'claude': claude_score,
            'openai': openai_score,
            'cursor': cursor_score
        }
        
        best_llm = max(scores, key=scores.get)
        
        # Se nenhum indicador específico, usa Claude como padrão
        if scores[best_llm] == 0:
            best_llm = 'claude'
        
        self.logger.debug(f"Scores de roteamento: {scores}, escolhido: {best_llm}")
        return best_llm
    
    def _load_template(self, template_name: str) -> Optional[str]:
        """
        Carrega um template do diretório de templates
        
        Args:
            template_name: Nome do template (sem extensão)
            
        Returns:
            Conteúdo do template ou None se não encontrado
        """
        
        # Verifica cache primeiro
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        # Procura arquivo de template
        template_file = self.templates_dir / f"{template_name}.txt"
        
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Cache o template
                self._template_cache[template_name] = template_content
                self.logger.debug(f"Template {template_name} carregado")
                return template_content
                
            except Exception as e:
                self.logger.error(f"Erro ao carregar template {template_name}: {e}")
                return None
        
        self.logger.warning(f"Template {template_name} não encontrado")
        return None
    
    def _apply_template(self, template: str, prompt: str) -> str:
        """
        Aplica um template ao prompt
        
        Args:
            template: Conteúdo do template
            prompt: Prompt a ser inserido no template
            
        Returns:
            Prompt formatado com template
        """
        
        # Substitui placeholders no template
        formatted = template.format(
            prompt=prompt,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            date=datetime.now().strftime('%Y-%m-%d'),
            time=datetime.now().strftime('%H:%M:%S')
        )
        
        return formatted
    
    def _format_basic(self, prompt: str, target: str) -> str:
        """
        Formatação básica quando não há template específico
        
        Args:
            prompt: Prompt a ser formatado
            target: LLM de destino
            
        Returns:
            Prompt formatado basicamante
        """
        
        # Formatações básicas por LLM
        if target == 'claude':
            return f"""<instructions>
{prompt}
</instructions>

Por favor, processe esta solicitação de forma detalhada e estruturada."""
        
        elif target == 'openai':
            return f"""System: Você é um assistente AI útil e preciso.

User: {prompt}

Forneça uma resposta clara e detalhada."""
        
        elif target == 'cursor':
            return f"""# Cursor AI Assistant

**Prompt:**
{prompt}

**Instruções:**
- Foque em soluções práticas e eficientes
- Inclua exemplos de código quando relevante
- Explique o raciocínio por trás das sugestões"""
        
        else:  # universal
            return f"""**Prompt:**
{prompt}

**Instruções:**
- Analise cuidadosamente a solicitação
- Forneça uma resposta estruturada e detalhada
- Seja preciso e útil na resposta"""
    
    def _generate_metadata(self, prompt: str, target: str) -> Dict[str, Any]:
        """
        Gera metadados para o roteamento
        
        Args:
            prompt: Prompt original
            target: LLM de destino
            
        Returns:
            Dicionário com metadados
        """
        
        return {
            'word_count': len(prompt.split()),
            'char_count': len(prompt),
            'has_code': any(indicator in prompt.lower() 
                          for indicator in ['def ', 'function', 'class ', 'import ', '```']),
            'complexity_score': self._calculate_complexity(prompt),
            'language_detected': self._detect_language(prompt),
            'routing_confidence': self._calculate_routing_confidence(prompt, target)
        }
    
    def _calculate_complexity(self, prompt: str) -> float:
        """
        Calcula um score de complexidade do prompt (0-1)
        
        Args:
            prompt: Prompt para análise
            
        Returns:
            Score de complexidade
        """
        
        factors = {
            'length': min(len(prompt) / 1000, 1.0) * 0.3,  # Até 1000 chars = complexidade 0.3
            'technical_terms': len([word for word in prompt.split() 
                                  if len(word) > 8]) / len(prompt.split()) * 0.3,
            'structure': (prompt.count('\n') + prompt.count('.') + prompt.count(':')) / 50 * 0.2,
            'questions': prompt.count('?') / 10 * 0.2
        }
        
        return min(sum(factors.values()), 1.0)
    
    def _detect_language(self, prompt: str) -> str:
        """
        Detecta o idioma principal do prompt
        
        Args:
            prompt: Prompt para análise
            
        Returns:
            Código do idioma detectado
        """
        
        # Detector simples baseado em palavras comuns
        portuguese_words = ['e', 'o', 'a', 'de', 'em', 'para', 'com', 'não', 'um', 'uma']
        english_words = ['and', 'the', 'a', 'an', 'of', 'in', 'for', 'with', 'not', 'is']
        
        prompt_words = prompt.lower().split()
        
        pt_count = sum(1 for word in prompt_words if word in portuguese_words)
        en_count = sum(1 for word in prompt_words if word in english_words)
        
        if pt_count > en_count:
            return 'pt'
        elif en_count > pt_count:
            return 'en'
        else:
            return 'unknown'
    
    def _calculate_routing_confidence(self, prompt: str, target: str) -> float:
        """
        Calcula a confiança na decisão de roteamento
        
        Args:
            prompt: Prompt analisado
            target: LLM escolhido
            
        Returns:
            Score de confiança (0-1)
        """
        
        if target == 'auto':
            return 0.5  # Confiança média para auto
        
        # Verifica se o target tem indicadores no prompt
        indicators = self.routing_rules.get(f'{target}_indicators', [])
        matches = sum(1 for indicator in indicators if indicator in prompt.lower())
        
        if matches == 0:
            return 0.3  # Baixa confiança se não há indicadores
        elif matches <= 2:
            return 0.7  # Confiança média
        else:
            return 0.9  # Alta confiança
    
    def get_available_templates(self) -> list:
        """
        Retorna lista de templates disponíveis
        
        Returns:
            Lista de nomes de templates disponíveis
        """
        
        if not self.templates_dir.exists():
            return []
        
        templates = []
        for template_file in self.templates_dir.glob("*.txt"):
            templates.append(template_file.stem)
        
        return sorted(templates)
