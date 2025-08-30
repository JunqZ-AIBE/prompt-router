"""
Prompt Router - Sistema de otimização e roteamento de prompts para múltiplos LLMs
Desenvolvido para otimizar prompts direcionados para Claude, OpenAI e Cursor

Autor: Arquiteto de Software
Data: 30/08/2025
Versão: 1.0.0 MVP

Este arquivo é o ponto de entrada principal do sistema.
Gerencia o roteamento de prompts e a integração com diferentes LLMs.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Adiciona o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent))

from config.settings import Settings
from chains.prompt_optimizer import PromptOptimizer
from chains.llm_router import LLMRouter
from utils.logger import setup_logger

def main():
    """
    Função principal do Prompt Router
    Orquestra todo o fluxo de otimização e roteamento de prompts
    """
    print("🚀 Iniciando Prompt Router v1.0.0")
    
    # Configura logging
    logger = setup_logger()
    
    # Carrega configurações
    settings = Settings()
    
    # Inicializa componentes principais
    optimizer = PromptOptimizer(settings)
    router = LLMRouter(settings)
    
    # Parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Prompt Router - Sistema de otimização de prompts')
    parser.add_argument('--input', '-i', required=True, help='Prompt de entrada')
    parser.add_argument('--target', '-t', choices=['claude', 'openai', 'cursor', 'universal'], 
                       default='universal', help='LLM de destino')
    parser.add_argument('--optimize', '-o', action='store_true', 
                       help='Aplicar otimização no prompt')
    parser.add_argument('--send', '-s', action='store_true', 
                       help='Enviar diretamente para o LLM (funcionalidade futura)')
    
    args = parser.parse_args()
    
    try:
        print(f"📝 Prompt de entrada: {args.input[:50]}...")
        print(f"🎯 Destino: {args.target}")
        
        # Otimiza o prompt se solicitado
        if args.optimize:
            print("🔧 Otimizando prompt...")
            optimized_prompt = optimizer.optimize(args.input, target_llm=args.target)
        else:
            optimized_prompt = args.input
            
        # Roteia para o LLM apropriado
        print("🔄 Roteando prompt...")
        result = router.route_prompt(optimized_prompt, target=args.target)
        
        # Exibe resultado
        print("\n" + "="*60)
        print("📤 PROMPT OTIMIZADO E ROTEADO:")
        print("="*60)
        print(result['formatted_prompt'])
        print("\n" + "="*60)
        print(f"ℹ️  Informações do roteamento:")
        print(f"   - LLM de destino: {result['target_llm']}")
        print(f"   - Template usado: {result['template_used']}")
        print(f"   - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Funcionalidade de envio direto (placeholder para futuras implementações)
        if args.send:
            print("\n🚧 Funcionalidade de envio direto em desenvolvimento...")
            print("   Por enquanto, copie e cole o prompt otimizado manualmente.")
            
    except Exception as e:
        logger.error(f"Erro durante execução: {str(e)}")
        print(f"❌ Erro: {str(e)}")
        sys.exit(1)
    
    print("\n✅ Prompt Router executado com sucesso!")

if __name__ == "__main__":
    if "--interactive" in sys.argv:
        from ui.interactive_cli import InteractiveCLI
        cli = InteractiveCLI()
        cli.run()
        sys.exit(0)
    main()
