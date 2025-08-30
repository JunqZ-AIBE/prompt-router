"""
Script de Setup do Prompt Router
Automatiza a instalação e configuração inicial do projeto

Execute: python setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Instala as dependências necessárias"""
    
    print("📦 Instalando dependências...")
    
    # Lista das dependências essenciais para o MVP
    essential_deps = [
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        # Outras dependências serão instaladas conforme necessário
    ]
    
    for dep in essential_deps:
        try:
            print(f"   Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erro ao instalar {dep}: {e}")
            return False
    
    print("   ✅ Dependências instaladas!")
    return True

def setup_environment():
    """Configura o ambiente de desenvolvimento"""
    
    print("⚙️  Configurando ambiente...")
    
    # Cria diretório de logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("   📁 Diretório logs/ criado")
    
    # Verifica se .env existe e está configurado
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        if "your_anthropic_api_key_here" in env_content:
            print("   ⚠️  Configure suas chaves de API no arquivo .env")
            print("   📝 Edite o arquivo .env e substitua os placeholders pelas suas chaves reais")
        else:
            print("   ✅ Arquivo .env configurado")
    
    print("   ✅ Ambiente configurado!")

def run_tests():
    """Executa testes básicos do sistema"""
    
    print("🧪 Executando testes básicos...")
    
    try:
        # Testa importações
        from config.settings import Settings
        from chains.prompt_optimizer import PromptOptimizer
        from chains.llm_router import LLMRouter
        print("   ✅ Todas as importações funcionando")
        
        # Testa inicialização básica
        settings = Settings()
        optimizer = PromptOptimizer(settings)
        router = LLMRouter(settings)
        print("   ✅ Componentes inicializados corretamente")
        
        # Testa otimização simples
        test_prompt = "Este é um teste"
        optimized = optimizer.optimize(test_prompt, target_llm="universal")
        print("   ✅ Otimização funcionando")
        
        # Testa roteamento
        result = router.route_prompt(optimized, target="universal")
        print("   ✅ Roteamento funcionando")
        
        print("   🎉 Todos os testes básicos passaram!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nos testes: {e}")
        return False

def main():
    """Função principal do setup"""
    
    print("🚀 Setup do Prompt Router")
    print("=" * 40)
    
    success = True
    
    # Instala dependências
    if not install_dependencies():
        success = False
    
    # Configura ambiente
    setup_environment()
    
    # Executa testes
    if not run_tests():
        success = False
    
    print("\n" + "=" * 40)
    
    if success:
        print("✅ Setup concluído com sucesso!")
        print("\n📚 Próximos passos:")
        print("   1. Configure suas chaves de API no arquivo .env")
        print("   2. Execute: python main.py --help")
        print("   3. Teste: python example_usage.py")
        print("   4. Leia a documentação no README.md")
    else:
        print("❌ Setup falhou. Verifique os erros acima.")
        print("\n💡 Tente:")
        print("   - Instalar manualmente: pip install python-dotenv")
        print("   - Verificar versão do Python (3.8+)")
        print("   - Executar como administrador se necessário")

if __name__ == "__main__":
    main()
