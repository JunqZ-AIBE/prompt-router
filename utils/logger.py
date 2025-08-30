"""
Sistema de Logging do Prompt Router
Configura e gerencia logs do sistema

Este módulo setup o sistema de logging para toda a aplicação,
permitindo rastrear operações e debugar problemas.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str = "prompt_router",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configura e retorna um logger personalizado
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Arquivo para salvar logs (opcional)
        
    Returns:
        Logger configurado
    """
    
    # Cria logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        # Cria diretório de logs se não existir
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Log padrão no diretório logs/
        logs_dir = Path(__file__).parent.parent / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        log_filename = f"prompt_router_{datetime.now().strftime('%Y%m%d')}.log"
        log_file_path = logs_dir / log_filename
        
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.info(f"Logger '{name}' configurado com sucesso")
    return logger

class LoggerMixin:
    """
    Mixin para adicionar funcionalidade de logging a qualquer classe
    
    Exemplo de uso:
        class MinhaClasse(LoggerMixin):
            def __init__(self):
                super().__init__()
                self.logger.info("Classe inicializada")
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = setup_logger(self.__class__.__name__)

def log_execution_time(func):
    """
    Decorator para logar tempo de execução de funções
    
    Args:
        func: Função a ser decorada
        
    Returns:
        Função decorada com logging de tempo
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("prompt_router")
        start_time = datetime.now()
        
        try:
            logger.debug(f"Iniciando execução: {func.__name__}")
            result = func(*args, **kwargs)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.debug(f"Função {func.__name__} executada em {execution_time:.2f}s")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.error(f"Erro em {func.__name__} após {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper
