"""
Prompt Router Advanced - Sistema completo de otimização e roteamento de prompts
Versão 2.0 com Analytics, Cache, Batch Processing e muito mais

Autor: Arquiteto de Software
Data: 30/08/2025
Versão: 2.0.0 Advanced
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
import time

# Adiciona o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent))

from config.settings import Settings
from chains.prompt_optimizer import PromptOptimizer
from chains.llm_router import LLMRouter
from chains.batch_processor import BatchProcessor, BatchItem
from analytics.prompt_analyzer import PromptAnalyzer, PromptComparator
from cache.prompt_cache import get_cache_instance
from utils.logger import setup_logger

def print_banner():
    """Exibe banner do Prompt Router Advanced"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                   🚀 PROMPT ROUTER ADVANCED v2.0             ║
║               Sistema Inteligente de Otimização de Prompts    ║
║                                                               ║
║  ✨ Analytics Avançado    🚀 Batch Processing                 ║
║  🧠 Cache Inteligente     📊 Comparação de Prompts           ║
║  🎯 Roteamento Multi-LLM  📈 Métricas Detalhadas             ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Função principal do Prompt Router Advanced"""
    
    print_banner()
    
    # Configura logging
    logger = setup_logger()
    
    # Carrega configurações
    settings = Settings()
    
    # Parser de argumentos avançado
    parser = argparse.ArgumentParser(
        description='Prompt Router Advanced - Sistema completo de otimização de prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Básico - otimização simples
  python main.py --input "Explique machine learning" --optimize
  
  # Com análise detalhada
  python main.py --input "Crie uma função Python" --target cursor --analyze
  
  # Comparação de prompts
  python main.py --compare "prompt1.txt" "prompt2.txt" --target claude
  
  # Batch processing de CSV
  python main.py --batch-csv "prompts.csv" --enable-cache
  
  # Analytics e estatísticas
  python main.py --stats --cache-stats --batch-summary
  
  # Limpeza de cache
  python main.py --clear-cache
        """
    )
    
    # Argumentos básicos
    parser.add_argument('--input', '-i', help='Prompt de entrada')
    parser.add_argument('--target', '-t', 
                       choices=['claude', 'openai', 'cursor', 'universal', 'auto'], 
                       default='auto', help='LLM de destino')
    parser.add_argument('--optimize', '-o', action='store_true', 
                       help='Aplicar otimização no prompt')
    
    # Funcionalidades avançadas
    parser.add_argument('--analyze', action='store_true',
                       help='Análise detalhada do prompt')
    parser.add_argument('--compare', nargs=2, metavar=('PROMPT1', 'PROMPT2'),
                       help='Compara dois prompts')
    
    # Batch processing
    parser.add_argument('--batch-csv', help='Arquivo CSV para batch processing')
    parser.add_argument('--batch-json', help='Arquivo JSON para batch processing')
    parser.add_argument('--batch-workers', type=int, default=4,
                       help='Número de workers para batch processing')
    
    # Cache
    parser.add_argument('--enable-cache', action='store_true',
                       help='Habilita cache inteligente')
    parser.add_argument('--cache-stats', action='store_true',
                       help='Mostra estatísticas do cache')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Limpa todo o cache')
    
    # Analytics e relatórios
    parser.add_argument('--stats', action='store_true',
                       help='Mostra estatísticas gerais')
    parser.add_argument('--batch-summary', action='store_true',
                       help='Resumo de batches processados')
    
    # Output
    parser.add_argument('--output', '-out', help='Arquivo de saída (JSON)')
    parser.add_argument('--format', choices=['text', 'json', 'markdown'], 
                       default='text', help='Formato de saída')
    
    args = parser.parse_args()
    
    # Validação básica de configuração
    if not settings.validate_config():
        logger.error("Configuração inválida. Verifique o arquivo .env")
        sys.exit(1)
    
    try:
        # Inicializa componentes principais
        optimizer = PromptOptimizer(settings)
        router = LLMRouter(settings)
        
        # Cache (opcional)
        cache = None
        if args.enable_cache or args.cache_stats or args.clear_cache:
            cache = get_cache_instance(settings)
        
        # === FUNCIONALIDADES AVANÇADAS ===
        
        # Limpeza de cache
        if args.clear_cache:
            if cache:
                cache.clear_all()
                print("✅ Cache limpo com sucesso!")
            else:
                print("❌ Cache não inicializado")
            return
        
        # Estatísticas de cache
        if args.cache_stats:
            if cache:
                stats = cache.get_stats()
                print("\n📊 ESTATÍSTICAS DO CACHE:")
                print("=" * 40)
                print(f"Total de entradas: {stats['total_entries']}")
                print(f"Tamanho total: {stats['total_size_mb']} MB")
                print(f"Utilização: {stats['utilization_percent']}%")
                print(f"Total de acessos: {stats['total_accesses']}")
                print(f"Média de acessos: {stats['avg_accesses']}")
                print(f"Taxa de acerto: {stats['hit_ratio']:.2%}")
                
                if stats['top_entries']:
                    print(f"\n🏆 Entradas mais acessadas:")
                    for entry in stats['top_entries']:
                        print(f"  - {entry['key']}: {entry['accesses']} acessos")
                
                if stats['tag_distribution']:
                    print(f"\n🏷️  Distribuição por tags:")
                    for tag, count in stats['tag_distribution'].items():
                        print(f"  - {tag}: {count}")
            else:
                print("❌ Cache não inicializado")
            return
        
        # Resumo de batches
        if args.batch_summary:
            batch_processor = BatchProcessor(settings)
            summary = batch_processor.get_batch_summary(days=7)
            
            print("\n📈 RESUMO DE BATCH PROCESSING (7 dias):")
            print("=" * 50)
            
            if 'message' in summary:
                print(summary['message'])
            else:
                print(f"Total de batches: {summary['total_batches']}")
                print(f"Items processados: {summary['total_items_processed']}")
                print(f"Taxa de sucesso: {summary['success_rate_percent']}%")
                print(f"Tempo médio por item: {summary['average_item_time_seconds']:.3f}s")
                
                if summary['llm_distribution']:
                    print(f"\n🎯 Distribuição por LLM:")
                    for llm, count in summary['llm_distribution'].items():
                        print(f"  - {llm}: {count} items")
            return
        
        # Estatísticas gerais
        if args.stats:
            print("\n📊 ESTATÍSTICAS GERAIS:")
            print("=" * 30)
            print(f"LLMs disponíveis: {', '.join(settings.available_llms)}")
            print(f"Templates disponíveis: {len(router.get_available_templates())}")
            print(f"Diretório de templates: {settings.TEMPLATES_DIR}")
            print(f"Modo debug: {settings.DEBUG_MODE}")
            
            # Estatísticas de analytics (se disponível)
            try:
                from analytics.prompt_analyzer import AnalyticsStorage
                analytics_storage = AnalyticsStorage(settings)
                analytics_summary = analytics_storage.get_analytics_summary(days=30)
                
                if 'message' not in analytics_summary:
                    print(f"\n📈 Analytics (30 dias):")
                    print(f"  - Análises realizadas: {analytics_summary['total_analyses']}")
                    print(f"  - Score médio de clareza: {analytics_summary['average_scores']['clarity_score']:.3f}")
                    print(f"  - Score médio de complexidade: {analytics_summary['average_scores']['complexity_score']:.3f}")
            except Exception as e:
                logger.debug(f"Analytics não disponível: {e}")
            
            return
        
        # Batch processing de CSV
        if args.batch_csv:
            print(f"\n🔄 Processando batch CSV: {args.batch_csv}")
            
            batch_processor = BatchProcessor(settings, max_workers=args.batch_workers)
            
            def progress_callback(progress):
                print(f"\rProgresso: {progress['progress_percent']:.1f}% "
                      f"({progress['completed_items']}/{progress['total_items']}) "
                      f"ETA: {progress['eta_seconds']:.0f}s", end='')
            
            report = batch_processor.process_from_csv(
                args.batch_csv,
                enable_cache=args.enable_cache,
                progress_callback=progress_callback
            )
            
            print(f"\n\n✅ Batch concluído!")
            print(f"   - Sucessos: {report.successful_items}/{report.total_items}")
            print(f"   - Tempo total: {report.total_time_seconds:.2f}s")
            print(f"   - Tempo médio por item: {report.average_time_per_item:.3f}s")
            
            if args.output:
                output_path = Path(args.output)
                if output_path.suffix.lower() == '.csv':
                    batch_processor.export_results_to_csv(report, args.output)
                    print(f"   - Resultados exportados para: {args.output}")
                else:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
                    print(f"   - Relatório salvo em: {args.output}")
            
            return
        
        # Batch processing de JSON
        if args.batch_json:
            print(f"\n🔄 Processando batch JSON: {args.batch_json}")
            
            batch_processor = BatchProcessor(settings, max_workers=args.batch_workers)
            report = batch_processor.process_from_json(
                args.batch_json,
                enable_cache=args.enable_cache
            )
            
            print(f"✅ Batch JSON concluído: {report.successful_items}/{report.total_items} sucessos")
            return
        
        # Comparação de prompts
        if args.compare:
            print(f"\n🔍 Comparando prompts...")
            
            # Carrega prompts
            prompt1_path, prompt2_path = args.compare
            
            try:
                with open(prompt1_path, 'r', encoding='utf-8') as f:
                    prompt1 = f.read().strip()
            except:
                prompt1 = prompt1_path  # Trata como texto direto
            
            try:
                with open(prompt2_path, 'r', encoding='utf-8') as f:
                    prompt2 = f.read().strip()
            except:
                prompt2 = prompt2_path  # Trata como texto direto
            
            comparator = PromptComparator(settings)
            comparison = comparator.compare_prompts(prompt1, prompt2, args.target)
            
            print("\n" + "="*60)
            print("📊 COMPARAÇÃO DE PROMPTS:")
            print("="*60)
            
            print(f"\n🥇 Vencedor: {comparison['winner'].upper()}")
            print(f"💡 Recomendação: {comparison['recommendation']}")
            
            print(f"\n📈 Melhorias:")
            for metric, improvement in comparison['improvements'].items():
                if improvement != 0:
                    symbol = "📈" if improvement > 0 else "📉"
                    print(f"   {symbol} {metric}: {improvement:+.1f}%")
            
            # Salva comparação se solicitado
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(comparison, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Comparação salva em: {args.output}")
            
            return
        
        # === PROCESSAMENTO INDIVIDUAL ===
        
        if not args.input:
            print("❌ Erro: --input é obrigatório para processamento individual")
            parser.print_help()
            sys.exit(1)
        
        print(f"📝 Processando prompt: {args.input[:50]}...")
        print(f"🎯 Destino: {args.target}")
        
        start_time = time.time()
        
        # Verifica cache primeiro
        cached_result = None
        if args.enable_cache and cache:
            cached_result = cache.get(args.input, args.target)
            if cached_result:
                print("⚡ Cache hit - usando resultado armazenado")
        
        if not cached_result:
            # Otimiza o prompt se solicitado
            if args.optimize:
                print("🔧 Otimizando prompt...")
                optimized_prompt = optimizer.optimize(args.input, target_llm=args.target)
            else:
                optimized_prompt = args.input
                
            # Roteia para o LLM apropriado
            print("🔄 Roteando prompt...")
            result = router.route_prompt(optimized_prompt, target=args.target)
            
            # Armazena no cache se habilitado
            if args.enable_cache and cache:
                cache_data = {
                    'optimized_prompt': optimized_prompt,
                    'formatted_prompt': result['formatted_prompt'],
                    'routing_metadata': result
                }
                cache.set(args.input, args.target, cache_data, tags=['individual'])
        else:
            # Usa resultado do cache
            optimized_prompt = cached_result.get('optimized_prompt', args.input)
            result = {
                'formatted_prompt': cached_result.get('formatted_prompt'),
                'target_llm': args.target,
                'template_used': 'cached',
                'timestamp': datetime.now().isoformat()
            }
        
        processing_time = time.time() - start_time
        
        # Análise detalhada se solicitada
        analysis = None
        if args.analyze:
            print("🔍 Analisando prompt...")
            analyzer = PromptAnalyzer(settings)
            analysis = analyzer.analyze(args.input, args.target)
        
        # === EXIBIÇÃO DE RESULTADOS ===
        
        if args.format == 'json':
            # Formato JSON
            output_data = {
                'input_prompt': args.input,
                'optimized_prompt': optimized_prompt,
                'formatted_prompt': result['formatted_prompt'],
                'target_llm': result['target_llm'],
                'template_used': result['template_used'],
                'processing_time_seconds': processing_time,
                'analysis': analysis.to_dict() if analysis else None,
                'timestamp': result['timestamp']
            }
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                print(f"💾 Resultado salvo em: {args.output}")
            else:
                print(json.dumps(output_data, indent=2, ensure_ascii=False))
                
        elif args.format == 'markdown':
            # Formato Markdown
            md_output = f"""
# Resultado do Prompt Router

## Configuração
- **LLM de destino:** {result['target_llm']}
- **Template usado:** {result['template_used']}
- **Tempo de processamento:** {processing_time:.3f}s

## Prompt Original
```
{args.input}
```

## Prompt Otimizado
```
{optimized_prompt}
```

## Prompt Formatado
```
{result['formatted_prompt']}
```
"""
            
            if analysis:
                md_output += f"""
## Análise Detalhada
- **Complexidade:** {analysis.complexity_score:.3f}
- **Clareza:** {analysis.clarity_score:.3f}
- **Completude:** {analysis.completeness_score:.3f}
- **Idioma detectado:** {analysis.language}
- **Contagem de palavras:** {analysis.word_count}
"""
                
                if analysis.suggested_improvements:
                    md_output += "\n### Sugestões de Melhoria\n"
                    for improvement in analysis.suggested_improvements:
                        md_output += f"- {improvement}\n"
            
            md_output += f"\n---\n*Gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(md_output)
                print(f"💾 Resultado salvo em: {args.output}")
            else:
                print(md_output)
        
        else:
            # Formato texto padrão
            print("\n" + "="*60)
            print("📤 RESULTADO DO PROMPT ROUTER:")
            print("="*60)
            print(result['formatted_prompt'])
            print("\n" + "="*60)
            print(f"ℹ️  Informações:")
            print(f"   - LLM de destino: {result['target_llm']}")
            print(f"   - Template usado: {result['template_used']}")
            print(f"   - Tempo de processamento: {processing_time:.3f}s")
            print(f"   - Timestamp: {result['timestamp']}")
            
            # Mostra análise se disponível
            if analysis:
                print(f"\n🔍 Análise:")
                print(f"   - Complexidade: {analysis.complexity_score:.3f}")
                print(f"   - Clareza: {analysis.clarity_score:.3f}")
                print(f"   - Completude: {analysis.completeness_score:.3f}")
                print(f"   - Idioma: {analysis.language}")
                print(f"   - Palavras: {analysis.word_count}")
                
                if analysis.suggested_improvements:
                    print(f"   - Sugestões: {len(analysis.suggested_improvements)} melhorias identificadas")
                    for i, improvement in enumerate(analysis.suggested_improvements[:3], 1):
                        print(f"     {i}. {improvement}")
                    
                    if len(analysis.suggested_improvements) > 3:
                        print(f"     ... e mais {len(analysis.suggested_improvements) - 3} sugestões")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Operação interrompida pelo usuário")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Erro durante execução: {str(e)}")
        print(f"❌ Erro: {str(e)}")
        
        if settings.DEBUG_MODE:
            import traceback
            print("\n🐛 Debug trace:")
            traceback.print_exc()
        
        sys.exit(1)
    
    print("\n✅ Prompt Router Advanced executado com sucesso!")

if __name__ == "__main__":
    main()
