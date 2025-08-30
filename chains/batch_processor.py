"""
Sistema de Batch Processing do Prompt Router
Processamento em lote de múltiplos prompts

Este módulo permite:
- Processamento em lote de prompts
- Paralelização de otimizações
- Processamento de arquivos CSV/JSON
- Relatórios de batch
- Progress tracking
"""

import asyncio
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import threading
from queue import Queue
import time

from utils.logger import LoggerMixin, log_execution_time
from chains.prompt_optimizer import PromptOptimizer
from chains.llm_router import LLMRouter
from analytics.prompt_analyzer import PromptAnalyzer, AnalyticsStorage
from cache.prompt_cache import get_cache_instance

@dataclass
class BatchItem:
    """
    Item individual de um batch
    """
    id: str
    prompt: str
    target_llm: str = 'universal'
    optimization_type: str = 'default'
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class BatchResult:
    """
    Resultado do processamento de um item do batch
    """
    item_id: str
    original_prompt: str
    optimized_prompt: str
    formatted_prompt: str
    target_llm: str
    processing_time_seconds: float
    success: bool
    error_message: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    routing_metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)

@dataclass
class BatchReport:
    """
    Relatório completo de um batch processing
    """
    batch_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    total_items: int
    processed_items: int
    successful_items: int
    failed_items: int
    total_time_seconds: float
    average_time_per_item: float
    results: List[BatchResult]
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        # Converte datetime para string
        data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data

class ProgressTracker:
    """
    Tracker de progresso para batch processing
    """
    
    def __init__(self, total_items: int):
        self.total_items = total_items
        self.completed_items = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def update(self, completed: int = 1):
        """Atualiza progresso"""
        with self.lock:
            self.completed_items += completed
    
    def get_progress(self) -> Dict[str, Any]:
        """Retorna status atual do progresso"""
        with self.lock:
            elapsed_time = time.time() - self.start_time
            progress_percent = (self.completed_items / self.total_items) * 100
            
            if self.completed_items > 0:
                avg_time_per_item = elapsed_time / self.completed_items
                eta_seconds = avg_time_per_item * (self.total_items - self.completed_items)
            else:
                avg_time_per_item = 0
                eta_seconds = 0
            
            return {
                'total_items': self.total_items,
                'completed_items': self.completed_items,
                'progress_percent': round(progress_percent, 2),
                'elapsed_time_seconds': round(elapsed_time, 2),
                'eta_seconds': round(eta_seconds, 2),
                'avg_time_per_item': round(avg_time_per_item, 3)
            }

class BatchProcessor(LoggerMixin):
    """
    Processador principal para batch processing
    
    Gerencia processamento paralelo de múltiplos prompts
    com otimização, roteamento e análise.
    """
    
    def __init__(self, settings, max_workers: int = 4):
        """
        Inicializa o batch processor
        
        Args:
            settings: Configurações do sistema
            max_workers: Número máximo de workers paralelos
        """
        super().__init__()
        self.settings = settings
        self.max_workers = max_workers
        
        # Componentes principais
        self.optimizer = PromptOptimizer(settings)
        self.router = LLMRouter(settings)
        self.analyzer = PromptAnalyzer(settings)
        self.analytics_storage = AnalyticsStorage(settings)
        self.cache = get_cache_instance(settings)
        
        # Diretório para relatórios de batch
        self.reports_dir = settings.PROJECT_ROOT / 'batch_reports'
        self.reports_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"BatchProcessor inicializado com {max_workers} workers")
    
    @log_execution_time
    def process_batch(self, batch_items: List[BatchItem], 
                     batch_id: Optional[str] = None,
                     enable_analysis: bool = True,
                     enable_cache: bool = True,
                     progress_callback: Optional[Callable] = None) -> BatchReport:
        """
        Processa um batch de prompts
        
        Args:
            batch_items: Lista de itens para processar
            batch_id: ID do batch (gerado automaticamente se None)
            enable_analysis: Se deve fazer análise detalhada
            enable_cache: Se deve usar cache
            progress_callback: Callback para atualizações de progresso
            
        Returns:
            BatchReport com resultados completos
        """
        
        if not batch_id:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Iniciando batch {batch_id} com {len(batch_items)} itens")
        
        # Inicializa relatório
        report = BatchReport(
            batch_id=batch_id,
            started_at=datetime.now(),
            completed_at=None,
            total_items=len(batch_items),
            processed_items=0,
            successful_items=0,
            failed_items=0,
            total_time_seconds=0,
            average_time_per_item=0,
            results=[],
            errors=[]
        )
        
        # Tracker de progresso
        progress = ProgressTracker(len(batch_items))
        
        # Processamento paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submete todos os jobs
            future_to_item = {
                executor.submit(
                    self._process_single_item, 
                    item, 
                    enable_analysis, 
                    enable_cache
                ): item 
                for item in batch_items
            }
            
            # Coleta resultados conforme completam
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                
                try:
                    result = future.result()
                    report.results.append(result)
                    
                    if result.success:
                        report.successful_items += 1
                    else:
                        report.failed_items += 1
                        if result.error_message:
                            report.errors.append(f"Item {item.id}: {result.error_message}")
                    
                    report.processed_items += 1
                    progress.update()
                    
                    # Callback de progresso
                    if progress_callback:
                        progress_callback(progress.get_progress())
                    
                except Exception as e:
                    error_msg = f"Erro crítico no item {item.id}: {str(e)}"
                    self.logger.error(error_msg)
                    report.errors.append(error_msg)
                    report.failed_items += 1
        
        # Finaliza relatório
        report.completed_at = datetime.now()
        report.total_time_seconds = (report.completed_at - report.started_at).total_seconds()
        
        if report.processed_items > 0:
            report.average_time_per_item = report.total_time_seconds / report.processed_items
        
        # Salva relatório
        self._save_batch_report(report)
        
        self.logger.info(
            f"Batch {batch_id} concluído: {report.successful_items}/{report.total_items} sucessos "
            f"em {report.total_time_seconds:.2f}s"
        )
        
        return report
    
    def _process_single_item(self, item: BatchItem, 
                           enable_analysis: bool, 
                           enable_cache: bool) -> BatchResult:
        """
        Processa um item individual do batch
        
        Args:
            item: Item a ser processado
            enable_analysis: Se deve fazer análise
            enable_cache: Se deve usar cache
            
        Returns:
            BatchResult com resultado do processamento
        """
        
        start_time = time.time()
        
        try:
            # Verifica cache primeiro
            cached_result = None
            if enable_cache:
                cached_result = self.cache.get(item.prompt, item.target_llm, item.optimization_type)
            
            if cached_result:
                self.logger.debug(f"Cache hit para item {item.id}")
                return BatchResult(
                    item_id=item.id,
                    original_prompt=item.prompt,
                    optimized_prompt=cached_result.get('optimized_prompt', item.prompt),
                    formatted_prompt=cached_result.get('formatted_prompt', item.prompt),
                    target_llm=item.target_llm,
                    processing_time_seconds=time.time() - start_time,
                    success=True,
                    analysis=cached_result.get('analysis'),
                    routing_metadata=cached_result.get('routing_metadata')
                )
            
            # Otimiza o prompt
            optimized_prompt = self.optimizer.optimize(item.prompt, target_llm=item.target_llm)
            
            # Roteia o prompt
            routing_result = self.router.route_prompt(optimized_prompt, target=item.target_llm)
            
            # Análise (opcional)
            analysis_result = None
            if enable_analysis:
                analysis = self.analyzer.analyze(item.prompt, item.target_llm)
                analysis_result = analysis.to_dict()
                
                # Salva análise no storage
                self.analytics_storage.save_analysis(analysis)
            
            # Resultado do processamento
            result_data = {
                'optimized_prompt': optimized_prompt,
                'formatted_prompt': routing_result['formatted_prompt'],
                'analysis': analysis_result,
                'routing_metadata': routing_result['metadata']
            }
            
            # Armazena no cache
            if enable_cache:
                self.cache.set(
                    item.prompt, 
                    item.target_llm, 
                    result_data,
                    optimization_type=item.optimization_type,
                    tags=['batch', item.target_llm]
                )
            
            return BatchResult(
                item_id=item.id,
                original_prompt=item.prompt,
                optimized_prompt=optimized_prompt,
                formatted_prompt=routing_result['formatted_prompt'],
                target_llm=item.target_llm,
                processing_time_seconds=time.time() - start_time,
                success=True,
                analysis=analysis_result,
                routing_metadata=routing_result['metadata']
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao processar item {item.id}: {str(e)}")
            return BatchResult(
                item_id=item.id,
                original_prompt=item.prompt,
                optimized_prompt="",
                formatted_prompt="",
                target_llm=item.target_llm,
                processing_time_seconds=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def process_from_csv(self, csv_file: Union[str, Path], 
                        prompt_column: str = 'prompt',
                        target_llm_column: str = 'target_llm',
                        id_column: Optional[str] = None,
                        **kwargs) -> BatchReport:
        """
        Processa prompts de um arquivo CSV
        
        Args:
            csv_file: Caminho do arquivo CSV
            prompt_column: Nome da coluna com prompts
            target_llm_column: Nome da coluna com target LLM
            id_column: Nome da coluna com ID (opcional)
            **kwargs: Argumentos para process_batch
            
        Returns:
            BatchReport com resultados
        """
        
        csv_path = Path(csv_file)
        self.logger.info(f"Carregando batch de {csv_path}")
        
        batch_items = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    item_id = row.get(id_column, f"csv_row_{i}") if id_column else f"csv_row_{i}"
                    prompt = row.get(prompt_column, "").strip()
                    target_llm = row.get(target_llm_column, "universal").strip()
                    
                    if not prompt:
                        self.logger.warning(f"Linha {i}: prompt vazio, pulando")
                        continue
                    
                    # Adiciona outros campos como metadata
                    metadata = {k: v for k, v in row.items() 
                              if k not in [prompt_column, target_llm_column, id_column]}
                    
                    batch_items.append(BatchItem(
                        id=item_id,
                        prompt=prompt,
                        target_llm=target_llm,
                        metadata=metadata
                    ))
            
            self.logger.info(f"Carregados {len(batch_items)} itens do CSV")
            return self.process_batch(batch_items, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Erro ao processar CSV {csv_path}: {str(e)}")
            raise
    
    def process_from_json(self, json_file: Union[str, Path], **kwargs) -> BatchReport:
        """
        Processa prompts de um arquivo JSON
        
        Args:
            json_file: Caminho do arquivo JSON
            **kwargs: Argumentos para process_batch
            
        Returns:
            BatchReport com resultados
        """
        
        json_path = Path(json_file)
        self.logger.info(f"Carregando batch de {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            batch_items = []
            
            # Suporta diferentes formatos JSON
            if isinstance(data, list):
                # Lista de objetos
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        batch_items.append(BatchItem(
                            id=item.get('id', f"json_item_{i}"),
                            prompt=item.get('prompt', ''),
                            target_llm=item.get('target_llm', 'universal'),
                            optimization_type=item.get('optimization_type', 'default'),
                            metadata=item.get('metadata', {})
                        ))
                    else:
                        # Item é string (prompt simples)
                        batch_items.append(BatchItem(
                            id=f"json_item_{i}",
                            prompt=str(item),
                            target_llm='universal'
                        ))
            
            elif isinstance(data, dict):
                # Objeto com prompts
                if 'prompts' in data:
                    prompts_data = data['prompts']
                    if isinstance(prompts_data, list):
                        return self.process_from_json_list(prompts_data, **kwargs)
                
                # Trata como um único item
                batch_items.append(BatchItem(
                    id=data.get('id', 'json_single'),
                    prompt=data.get('prompt', ''),
                    target_llm=data.get('target_llm', 'universal'),
                    optimization_type=data.get('optimization_type', 'default'),
                    metadata=data.get('metadata', {})
                ))
            
            self.logger.info(f"Carregados {len(batch_items)} itens do JSON")
            return self.process_batch(batch_items, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Erro ao processar JSON {json_path}: {str(e)}")
            raise
    
    def _save_batch_report(self, report: BatchReport):
        """Salva relatório de batch em arquivo"""
        
        report_file = self.reports_dir / f"{report.batch_id}_report.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Relatório salvo em {report_file}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório: {str(e)}")
    
    def export_results_to_csv(self, report: BatchReport, output_file: Union[str, Path]):
        """
        Exporta resultados do batch para CSV
        
        Args:
            report: Relatório do batch
            output_file: Arquivo de saída CSV
        """
        
        output_path = Path(output_file)
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Cabeçalho
                writer.writerow([
                    'item_id', 'original_prompt', 'optimized_prompt', 
                    'target_llm', 'processing_time_seconds', 'success',
                    'error_message', 'word_count_original', 'word_count_optimized',
                    'complexity_score', 'clarity_score'
                ])
                
                # Dados
                for result in report.results:
                    # Dados básicos
                    row = [
                        result.item_id,
                        result.original_prompt,
                        result.optimized_prompt,
                        result.target_llm,
                        result.processing_time_seconds,
                        result.success,
                        result.error_message or ''
                    ]
                    
                    # Adiciona métricas de análise se disponíveis
                    if result.analysis:
                        row.extend([
                            result.analysis.get('word_count', ''),
                            len(result.optimized_prompt.split()) if result.optimized_prompt else '',
                            result.analysis.get('complexity_score', ''),
                            result.analysis.get('clarity_score', '')
                        ])
                    else:
                        row.extend(['', '', '', ''])
                    
                    writer.writerow(row)
            
            self.logger.info(f"Resultados exportados para {output_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar para CSV: {str(e)}")
    
    def get_batch_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Retorna resumo de batches processados nos últimos dias
        
        Args:
            days: Número de dias para análise
            
        Returns:
            Resumo dos batches processados
        """
        
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date -= timedelta(days=days)
        
        # Busca arquivos de relatório
        recent_reports = []
        for report_file in self.reports_dir.glob("*_report.json"):
            try:
                # Extrai data do nome do arquivo
                file_date_str = report_file.stem.split('_')[1]  # batch_YYYYMMDD_HHMMSS_report
                file_date = datetime.strptime(file_date_str, '%Y%m%d')
                
                if file_date >= cutoff_date:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                        recent_reports.append(report_data)
            except Exception as e:
                self.logger.warning(f"Erro ao processar relatório {report_file}: {e}")
                continue
        
        if not recent_reports:
            return {'message': f'Nenhum batch encontrado nos últimos {days} dias'}
        
        # Calcula estatísticas
        total_batches = len(recent_reports)
        total_items = sum(r.get('total_items', 0) for r in recent_reports)
        total_successful = sum(r.get('successful_items', 0) for r in recent_reports)
        total_failed = sum(r.get('failed_items', 0) for r in recent_reports)
        total_time = sum(r.get('total_time_seconds', 0) for r in recent_reports)
        
        # Success rate
        success_rate = (total_successful / total_items * 100) if total_items > 0 else 0
        
        # Average processing time
        avg_batch_time = total_time / total_batches if total_batches > 0 else 0
        avg_item_time = total_time / total_items if total_items > 0 else 0
        
        # Distribuição por target LLM
        llm_distribution = {}
        for report in recent_reports:
            for result in report.get('results', []):
                llm = result.get('target_llm', 'unknown')
                llm_distribution[llm] = llm_distribution.get(llm, 0) + 1
        
        return {
            'period_days': days,
            'total_batches': total_batches,
            'total_items_processed': total_items,
            'successful_items': total_successful,
            'failed_items': total_failed,
            'success_rate_percent': round(success_rate, 2),
            'total_processing_time_seconds': round(total_time, 2),
            'average_batch_time_seconds': round(avg_batch_time, 2),
            'average_item_time_seconds': round(avg_item_time, 3),
            'llm_distribution': llm_distribution,
            'generated_at': datetime.now().isoformat()
        }

class AsyncBatchProcessor(LoggerMixin):
    """
    Versão assíncrona do batch processor para melhor performance
    
    PLACEHOLDER para implementação futura com async/await
    """
    
    def __init__(self, settings, max_concurrent: int = 10):
        super().__init__()
        self.settings = settings
        self.max_concurrent = max_concurrent
        self.logger.info("AsyncBatchProcessor inicializado (PLACEHOLDER)")
    
    async def process_batch_async(self, batch_items: List[BatchItem]) -> BatchReport:
        """
        Processamento assíncrono de batch
        
        PLACEHOLDER para implementação futura
        """
        self.logger.info("🚧 Batch assíncrono - PLACEHOLDER")
        
        # Por enquanto, usa implementação síncrona
        sync_processor = BatchProcessor(self.settings)
        return sync_processor.process_batch(batch_items)
