"""
Exemplo de uso do Prompt Router
Demonstração das funcionalidades principais

Execute este arquivo para ver o Prompt Router em ação:
python example_usage.py
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent))

def example_usage():
    """Exemplo de uso das principais funcionalidades"""
    
    print("🚀 Exemplo de Uso do Prompt Router")
    print("=" * 50)
    
    try:
        from config.settings import Settings
        from chains.prompt_optimizer import PromptOptimizer
        from chains.llm_router import LLMRouter
        
        # Inicializa configurações
        settings = Settings()
        
        # Cria instâncias dos componentes
        optimizer = PromptOptimizer(settings)
        router = LLMRouter(settings)
        
        # Exemplo de prompt
        example_prompt = "Explique como machine learning funciona de forma simples para iniciantes"
        
        print(f"📝 Prompt original: {example_prompt}")
        print()
        
        # Testa otimização para diferentes LLMs
        targets = ['claude', 'openai', 'cursor', 'universal']
        
        for target in targets:
            print(f"🎯 Testando para {target.upper()}:")
            print("-" * 30)
            
            # Otimiza o prompt
            optimized = optimizer.optimize(example_prompt, target_llm=target)
            
            # Roteia o prompt
            result = router.route_prompt(optimized, target=target)
            
            print(f"Template usado: {result['template_used']}")
            print(f"Tamanho final: {result['prompt_length']} caracteres")
            print("Prompt formatado:")
            print("```")
            print(result['formatted_prompt'][:200] + "..." if len(result['formatted_prompt']) > 200 else result['formatted_prompt'])
            print("```")
            print()
        
        print("✅ Exemplo executado com sucesso!")
        print("📖 Consulte o README.md para mais informações")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Certifique-se de instalar as dependências:")
        print("   pip install python-dotenv")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    example_usage()
