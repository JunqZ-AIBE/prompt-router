"""
Testes unitários para o Prompt Router
Executa testes abrangentes de todas as funcionalidades

Execute: python -m pytest tests/ -v
"""

import unittest
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from chains.prompt_optimizer import PromptOptimizer
from chains.llm_router import LLMRouter
from chains.api_client import APIClient, DirectSender

class TestPromptOptimizer(unittest.TestCase):
    """Testes para o PromptOptimizer"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.settings = Settings()
        self.optimizer = PromptOptimizer(self.settings)
        self.test_prompt = "Explique machine learning de forma simples"
    
    def test_general_optimizations(self):
        """Testa otimizações gerais"""
        messy_prompt = "  Este   é  um   teste  \n\n\n  com  espaços extras  "
        optimized = self.optimizer._apply_general_optimizations(messy_prompt)
        
        self.assertNotIn("  ", optimized)  # Não deve ter espaços duplos
        self.assertFalse(optimized.startswith(" "))  # Não deve começar com espaço
        self.assertFalse(optimized.endswith(" "))  # Não deve terminar com espaço
        self.assertTrue(optimized.endswith("."))  # Deve terminar com ponto
    
    def test_claude_optimization(self):
        """Testa otimização específica para Claude"""
        optimized = self.optimizer.optimize(self.test_prompt, target_llm="claude")
        
        # Claude deve usar tags XML
        self.assertIn("<instructions>", optimized)
        self.assertIn("<thinking>", optimized)
    
    def test_openai_optimization(self):
        """Testa otimização específica para OpenAI"""
        optimized = self.optimizer.optimize(self.test_prompt, target_llm="openai")
        
        # OpenAI deve ter context de role
        self.assertIn("assistente", optimized.lower())
    
    def test_cursor_optimization(self):
        """Testa otimização específica para Cursor"""
        code_prompt = "Crie uma função Python para calcular fibonacci"
        optimized = self.optimizer.optimize(code_prompt, target_llm="cursor")
        
        # Cursor deve ter contexto de desenvolvimento
        self.assertIn("desenvolvimento", optimized.lower())
    
    def test_universal_optimization(self):
        """Testa otimização universal"""
        optimized = self.optimizer.optimize(self.test_prompt, target_llm="universal")
        
        # Universal deve ter estrutura básica
        self.assertIn("analise", optimized.lower())
        self.assertIn("detalhada", optimized.lower())
    
    def test_optimization_stats(self):
        """Testa geração de estatísticas de otimização"""
        original = "teste simples"
        optimized = "teste simples otimizado."
        
        stats = self.optimizer.get_optimization_stats(original, optimized)
        
        self.assertIn('original_length', stats)
        self.assertIn('optimized_length', stats)
        self.assertIn('improvement_ratio', stats)
        self.assertEqual(stats['original_words'], 2)

class TestLLMRouter(unittest.TestCase):
    """Testes para o LLMRouter"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.settings = Settings()
        self.router = LLMRouter(self.settings)
        self.test_prompt = "Teste de roteamento"
    
    def test_determine_best_llm(self):
        """Testa determinação automática do melhor LLM"""
        # Prompt voltado para Claude
        claude_prompt = "Faça uma análise detalhada e crítica"
        best_llm = self.router._determine_best_llm(claude_prompt)
        self.assertEqual(best_llm, "claude")
        
        # Prompt voltado para programação (Cursor)
        code_prompt = "Debug este código Python e refatore"
        best_llm = self.router._determine_best_llm(code_prompt)
        self.assertEqual(best_llm, "cursor")
    
    def test_route_prompt_claude(self):
        """Testa roteamento para Claude"""
        result = self.router.route_prompt(self.test_prompt, target="claude")
        
        self.assertEqual(result['target_llm'], 'claude')
        self.assertIn('formatted_prompt', result)
        self.assertIn('timestamp', result)
        self.assertIn('metadata', result)
    
    def test_route_prompt_openai(self):
        """Testa roteamento para OpenAI"""
        result = self.router.route_prompt(self.test_prompt, target="openai")
        
        self.assertEqual(result['target_llm'], 'openai')
        self.assertIsInstance(result['prompt_length'], int)
    
    def test_route_prompt_auto(self):
        """Testa roteamento automático"""
        result = self.router.route_prompt(self.test_prompt, target="auto")
        
        # Deve escolher um LLM válido
        self.assertIn(result['target_llm'], ['claude', 'openai', 'cursor'])
    
    def test_metadata_generation(self):
        """Testa geração de metadados"""
        metadata = self.router._generate_metadata(self.test_prompt, "claude")
        
        self.assertIn('word_count', metadata)
        self.assertIn('complexity_score', metadata)
        self.assertIn('language_detected', metadata)
        self.assertIsInstance(metadata['routing_confidence'], float)

class TestSettings(unittest.TestCase):
    """Testes para Settings"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.settings = Settings()
    
    def test_settings_initialization(self):
        """Testa inicialização das configurações"""
        self.assertIsNotNone(self.settings.PROJECT_ROOT)
        self.assertIsNotNone(self.settings.TEMPLATES_DIR)
        self.assertEqual(self.settings.CLAUDE_MODEL, 'claude-sonnet-4-20250514')
    
    def test_llm_config(self):
        """Testa configurações específicas dos LLMs"""
        claude_config = self.settings.get_llm_config('claude')
        
        self.assertIn('model', claude_config)
        self.assertIn('max_tokens', claude_config)
        self.assertEqual(claude_config['model'], 'claude-sonnet-4-20250514')
    
    def test_available_llms(self):
        """Testa detecção de LLMs disponíveis"""
        available = self.settings.available_llms
        self.assertIsInstance(available, list)

class TestAPIClient(unittest.TestCase):
    """Testes para APIClient (placeholder)"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.settings = Settings()
        self.client = APIClient(self.settings)
    
    def test_api_key_validation(self):
        """Testa validação das chaves de API"""
        validation = self.client.validate_api_keys()
        
        self.assertIn('claude', validation)
        self.assertIn('openai', validation)
        self.assertIn('cursor', validation)
        self.assertIsInstance(validation['claude'], bool)

class TestIntegration(unittest.TestCase):
    """Testes de integração entre componentes"""
    
    def setUp(self):
        """Setup para testes de integração"""
        self.settings = Settings()
        self.optimizer = PromptOptimizer(self.settings)
        self.router = LLMRouter(self.settings)
    
    def test_full_pipeline(self):
        """Testa pipeline completo: otimização + roteamento"""
        original_prompt = "Explique inteligência artificial"
        
        # Otimiza
        optimized = self.optimizer.optimize(original_prompt, target_llm="claude")
        
        # Roteia
        result = self.router.route_prompt(optimized, target="claude")
        
        # Verifica resultado final
        self.assertIn('formatted_prompt', result)
        self.assertEqual(result['target_llm'], 'claude')
        self.assertGreater(len(result['formatted_prompt']), len(original_prompt))
    
    def test_auto_routing_pipeline(self):
        """Testa pipeline com roteamento automático"""
        code_prompt = "Crie uma classe Python para gerenciar usuários"
        
        # Otimiza
        optimized = self.optimizer.optimize(code_prompt, target_llm="auto")
        
        # Roteia automaticamente
        result = self.router.route_prompt(optimized, target="auto")
        
        # Deve rotear para Cursor devido ao contexto de código
        self.assertEqual(result['target_llm'], 'cursor')

if __name__ == '__main__':
    # Configura o runner de testes
    unittest.main(verbosity=2)
