"""
Configurações do Prompt Router
Define todas as configurações centralizadas do sistema

Este módulo carrega variáveis de ambiente e define constantes
para o funcionamento do sistema de roteamento de prompts.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

class Settings:
    """
    Classe central de configurações do Prompt Router
    Carrega e gerencia todas as configurações do sistema
    """
    
    def __init__(self):
        """Inicializa as configurações carregando variáveis de ambiente"""
        self._load_environment()
        self._setup_paths()
        self._configure_llm_settings()
    
    def _load_environment(self):
        """Carrega variáveis do arquivo .env"""
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
    def _setup_paths(self):
        """Define caminhos importantes do projeto"""
        self.PROJECT_ROOT = Path(__file__).parent.parent
        self.TEMPLATES_DIR = self.PROJECT_ROOT / 'templates'
        self.CHAINS_DIR = self.PROJECT_ROOT / 'chains'
        self.LOGS_DIR = self.PROJECT_ROOT / 'logs'
        
        # Cria diretório de logs se não existir
        self.LOGS_DIR.mkdir(exist_ok=True)
    
    def _configure_llm_settings(self):
        """Configura settings específicos para cada LLM"""
        
        # Configurações do Claude (Anthropic)
        self.CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        self.CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
        self.CLAUDE_MAX_TOKENS = int(os.getenv('CLAUDE_MAX_TOKENS', '4000'))
        
        # Configurações do OpenAI
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
        
        # Configurações do Cursor (placeholder para futura implementação)
        self.CURSOR_API_KEY = os.getenv('CURSOR_API_KEY')
        self.CURSOR_ENDPOINT = os.getenv('CURSOR_ENDPOINT', 'localhost:8080')
        
        # Configurações gerais
        self.DEFAULT_TEMPERATURE = float(os.getenv('DEFAULT_TEMPERATURE', '0.7'))
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    def get_llm_config(self, llm_name: str) -> Dict[str, Any]:
        """
        Retorna configuração específica para um LLM
        
        Args:
            llm_name: Nome do LLM (claude, openai, cursor)
            
        Returns:
            Dict com configurações do LLM
        """
        configs = {
            'claude': {
                'api_key': self.CLAUDE_API_KEY,
                'model': self.CLAUDE_MODEL,
                'max_tokens': self.CLAUDE_MAX_TOKENS,
                'temperature': self.DEFAULT_TEMPERATURE,
                'endpoint': 'https://api.anthropic.com/v1/messages'
            },
            'openai': {
                'api_key': self.OPENAI_API_KEY,
                'model': self.OPENAI_MODEL,
                'max_tokens': self.OPENAI_MAX_TOKENS,
                'temperature': self.DEFAULT_TEMPERATURE,
                'endpoint': 'https://api.openai.com/v1/chat/completions'
            },
            'cursor': {
                'api_key': self.CURSOR_API_KEY,
                'endpoint': self.CURSOR_ENDPOINT,
                'model': 'cursor-default',  # Placeholder
                'max_tokens': 4000,
                'temperature': self.DEFAULT_TEMPERATURE
            }
        }
        
        return configs.get(llm_name.lower(), {})
    
    def validate_config(self) -> bool:
        """
        Valida se as configurações obrigatórias estão presentes
        
        Returns:
            True se configurações válidas, False caso contrário
        """
        required_vars = []
        
        # Verifica se pelo menos uma API key está configurada
        if not any([self.CLAUDE_API_KEY, self.OPENAI_API_KEY, self.CURSOR_API_KEY]):
            required_vars.append("Pelo menos uma API key deve estar configurada")
        
        if required_vars:
            print("❌ Configurações obrigatórias em falta:")
            for var in required_vars:
                print(f"   - {var}")
            return False
            
        return True
    
    @property
    def available_llms(self) -> list:
        """Retorna lista de LLMs configurados e disponíveis"""
        available = []
        
        if self.CLAUDE_API_KEY:
            available.append('claude')
        if self.OPENAI_API_KEY:
            available.append('openai')
        if self.CURSOR_API_KEY:
            available.append('cursor')
            
        return available
