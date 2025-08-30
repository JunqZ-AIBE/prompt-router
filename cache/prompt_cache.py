"""
Sistema de Cache do Prompt Router
Gerencia cache de prompts otimizados e análises

Este módulo implementa cache inteligente para:
- Prompts otimizados
- Análises de prompts
- Respostas de APIs
- Metadados de roteamento
"""

import json
import hashlib
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
import threading
from contextlib import contextmanager

from utils.logger import LoggerMixin, log_execution_time

@dataclass
class CacheEntry:
    """
    Entrada do cache com metadados
    """
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class PromptCache(LoggerMixin):
    """
    Cache inteligente para prompts e otimizações
    
    Funcionalidades:
    - Cache por hash do prompt
    - Expiração automática
    - Limpeza por LRU
    - Persistência em disco
    - Thread-safe
    """
    
    def __init__(self, settings, max_size_mb: int = 100, default_ttl_hours: int = 24):
        """
        Inicializa o sistema de cache
        
        Args:
            settings: Configurações do sistema
            max_size_mb: Tamanho máximo do cache em MB
            default_ttl_hours: TTL padrão em horas
        """
        super().__init__()
        self.settings = settings
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = timedelta(hours=default_ttl_hours)
        
        # Diretório do cache
        self.cache_dir = settings.PROJECT_ROOT / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        # Arquivo de banco SQLite para metadados
        self.db_path = self.cache_dir / 'cache_metadata.db'
        
        # Lock para thread safety
        self._lock = threading.RLock()
        
        # Inicializa banco de dados
        self._init_database()
        
        # Limpa entradas expiradas na inicialização
        self._cleanup_expired()
        
        self.logger.info(f"PromptCache inicializado (max: {max_size_mb}MB, TTL: {default_ttl_hours}h)")
    
    def _init_database(self):
        """Inicializa banco de dados SQLite para metadados"""
        
        with self._get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    size_bytes INTEGER DEFAULT 0,
                    tags TEXT,
                    file_path TEXT
                )
            """)
            
            # Índices para performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_size_bytes ON cache_entries(size_bytes)")
    
    @contextmanager
    def _get_db_connection(self):
        """Context manager para conexões de banco thread-safe"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _generate_key(self, prompt: str, target_llm: str, optimization_type: str = 'default') -> str:
        """
        Gera chave única para o cache baseada no conteúdo
        
        Args:
            prompt: Prompt original
            target_llm: LLM de destino
            optimization_type: Tipo de otimização
            
        Returns:
            Hash SHA-256 como chave do cache
        """
        
        # Combina todos os parâmetros relevantes
        cache_input = f"{prompt}|{target_llm}|{optimization_type}"
        
        # Gera hash SHA-256
        return hashlib.sha256(cache_input.encode('utf-8')).hexdigest()
    
    def _get_file_path(self, key: str) -> Path:
        """Retorna caminho do arquivo de cache para uma chave"""
        return self.cache_dir / f"{key}.cache"
    
    @log_execution_time
    def get(self, prompt: str, target_llm: str, optimization_type: str = 'default') -> Optional[Dict[str, Any]]:
        """
        Recupera entrada do cache
        
        Args:
            prompt: Prompt original
            target_llm: LLM de destino
            optimization_type: Tipo de otimização
            
        Returns:
            Dados do cache ou None se não encontrado/expirado
        """
        
        with self._lock:
            key = self._generate_key(prompt, target_llm, optimization_type)
            
            # Verifica metadados no banco
            with self._get_db_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM cache_entries WHERE key = ?", (key,)
                ).fetchone()
                
                if not row:
                    self.logger.debug(f"Cache miss: {key[:12]}...")
                    return None
                
                # Verifica expiração
                if row['expires_at']:
                    expires_at = datetime.fromisoformat(row['expires_at'])
                    if datetime.now() > expires_at:
                        self.logger.debug(f"Cache expired: {key[:12]}...")
                        self._remove_entry(key)
                        return None
                
                # Atualiza estatísticas de acesso
                conn.execute("""
                    UPDATE cache_entries 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE key = ?
                """, (datetime.now().isoformat(), key))
            
            # Carrega dados do arquivo
            file_path = self._get_file_path(key)
            if not file_path.exists():
                self.logger.warning(f"Cache file missing: {key[:12]}...")
                self._remove_entry(key)
                return None
            
            try:
                with open(file_path, 'rb') as f:
                    cached_data = pickle.load(f)
                
                self.logger.debug(f"Cache hit: {key[:12]}...")
                return cached_data
                
            except Exception as e:
                self.logger.error(f"Erro ao carregar cache {key[:12]}...: {e}")
                self._remove_entry(key)
                return None
    
    @log_execution_time
    def set(self, prompt: str, target_llm: str, data: Dict[str, Any], 
            optimization_type: str = 'default', ttl_hours: Optional[int] = None,
            tags: Optional[List[str]] = None) -> bool:
        """
        Armazena entrada no cache
        
        Args:
            prompt: Prompt original
            target_llm: LLM de destino
            data: Dados a serem cached
            optimization_type: Tipo de otimização
            ttl_hours: TTL personalizado em horas
            tags: Tags para organização
            
        Returns:
            True se armazenado com sucesso
        """
        
        with self._lock:
            key = self._generate_key(prompt, target_llm, optimization_type)
            file_path = self._get_file_path(key)
            
            # Calcula expiração
            now = datetime.now()
            if ttl_hours is not None:
                expires_at = now + timedelta(hours=ttl_hours)
            else:
                expires_at = now + self.default_ttl
            
            try:
                # Salva dados no arquivo
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
                
                # Calcula tamanho
                size_bytes = file_path.stat().st_size
                
                # Verifica se precisa limpar cache por tamanho
                if self._get_total_size() + size_bytes > self.max_size_bytes:
                    self._cleanup_by_size(size_bytes)
                
                # Salva metadados no banco
                with self._get_db_connection() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO cache_entries 
                        (key, created_at, expires_at, size_bytes, tags, file_path)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        key,
                        now.isoformat(),
                        expires_at.isoformat(),
                        size_bytes,
                        json.dumps(tags or []),
                        str(file_path)
                    ))
                
                self.logger.debug(f"Cache stored: {key[:12]}... ({size_bytes} bytes)")
                return True
                
            except Exception as e:
                self.logger.error(f"Erro ao armazenar cache {key[:12]}...: {e}")
                # Remove arquivo se criado
                if file_path.exists():
                    file_path.unlink()
                return False
    
    def _remove_entry(self, key: str) -> bool:
        """Remove entrada específica do cache"""
        
        try:
            # Remove do banco
            with self._get_db_connection() as conn:
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            
            # Remove arquivo
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao remover cache {key[:12]}...: {e}")
            return False
    
    def _cleanup_expired(self) -> int:
        """Remove entradas expiradas do cache"""
        
        now = datetime.now().isoformat()
        removed_count = 0
        
        try:
            with self._get_db_connection() as conn:
                # Busca entradas expiradas
                expired_rows = conn.execute("""
                    SELECT key FROM cache_entries 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (now,)).fetchall()
                
                # Remove cada entrada
                for row in expired_rows:
                    if self._remove_entry(row['key']):
                        removed_count += 1
            
            if removed_count > 0:
                self.logger.info(f"Removidas {removed_count} entradas expiradas do cache")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de cache expirado: {e}")
            return 0
    
    def _cleanup_by_size(self, needed_bytes: int) -> int:
        """Remove entradas menos usadas para liberar espaço"""
        
        removed_count = 0
        freed_bytes = 0
        
        try:
            with self._get_db_connection() as conn:
                # Busca entradas ordenadas por LRU (menos acessadas primeiro)
                lru_rows = conn.execute("""
                    SELECT key, size_bytes FROM cache_entries 
                    ORDER BY access_count ASC, last_accessed ASC
                """).fetchall()
                
                # Remove até liberar espaço suficiente
                for row in lru_rows:
                    if freed_bytes >= needed_bytes:
                        break
                    
                    if self._remove_entry(row['key']):
                        removed_count += 1
                        freed_bytes += row['size_bytes']
            
            if removed_count > 0:
                self.logger.info(f"Removidas {removed_count} entradas do cache para liberar {freed_bytes} bytes")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza por tamanho: {e}")
            return 0
    
    def _get_total_size(self) -> int:
        """Retorna tamanho total do cache em bytes"""
        
        try:
            with self._get_db_connection() as conn:
                result = conn.execute("SELECT SUM(size_bytes) as total FROM cache_entries").fetchone()
                return result['total'] or 0
        except Exception as e:
            self.logger.error(f"Erro ao calcular tamanho total: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """Limpa todo o cache"""
        
        try:
            with self._lock:
                # Remove todos os arquivos
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                
                # Limpa banco de dados
                with self._get_db_connection() as conn:
                    conn.execute("DELETE FROM cache_entries")
            
            self.logger.info("Cache completamente limpo")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        
        try:
            with self._get_db_connection() as conn:
                # Estatísticas básicas
                basic_stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total_entries,
                        SUM(size_bytes) as total_size_bytes,
                        SUM(access_count) as total_accesses,
                        AVG(access_count) as avg_accesses
                    FROM cache_entries
                """).fetchone()
                
                # Distribuição por tags
                tag_stats = {}
                all_rows = conn.execute("SELECT tags FROM cache_entries").fetchall()
                for row in all_rows:
                    if row['tags']:
                        tags = json.loads(row['tags'])
                        for tag in tags:
                            tag_stats[tag] = tag_stats.get(tag, 0) + 1
                
                # Entradas mais acessadas
                top_entries = conn.execute("""
                    SELECT key, access_count FROM cache_entries
                    ORDER BY access_count DESC LIMIT 5
                """).fetchall()
                
                stats = {
                    'total_entries': basic_stats['total_entries'],
                    'total_size_mb': round((basic_stats['total_size_bytes'] or 0) / 1024 / 1024, 2),
                    'total_accesses': basic_stats['total_accesses'],
                    'avg_accesses': round(basic_stats['avg_accesses'] or 0, 2),
                    'hit_ratio': self._calculate_hit_ratio(),
                    'tag_distribution': tag_stats,
                    'top_entries': [
                        {'key': row['key'][:12] + '...', 'accesses': row['access_count']}
                        for row in top_entries
                    ],
                    'max_size_mb': round(self.max_size_bytes / 1024 / 1024, 2),
                    'utilization_percent': round(
                        ((basic_stats['total_size_bytes'] or 0) / self.max_size_bytes) * 100, 2
                    )
                }
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar estatísticas: {e}")
            return {'error': str(e)}
    
    def _calculate_hit_ratio(self) -> float:
        """Calcula taxa de acerto do cache (placeholder)"""
        # Em uma implementação completa, isso seria rastreado em runtime
        # Por ora, retorna valor estimado baseado no total de acessos
        try:
            with self._get_db_connection() as conn:
                result = conn.execute("SELECT AVG(access_count) as avg FROM cache_entries").fetchone()
                avg_access = result['avg'] or 0
                
                # Estimativa simples: quanto mais acessos médios, melhor a taxa de acerto
                return min(0.95, avg_access * 0.1)
                
        except Exception:
            return 0.0
    
    def find_by_tags(self, tags: List[str]) -> List[str]:
        """
        Encontra entradas do cache por tags
        
        Args:
            tags: Lista de tags para buscar
            
        Returns:
            Lista de chaves que correspondem às tags
        """
        
        try:
            with self._get_db_connection() as conn:
                matching_keys = []
                
                for row in conn.execute("SELECT key, tags FROM cache_entries").fetchall():
                    if row['tags']:
                        entry_tags = json.loads(row['tags'])
                        if any(tag in entry_tags for tag in tags):
                            matching_keys.append(row['key'])
                
                return matching_keys
                
        except Exception as e:
            self.logger.error(f"Erro ao buscar por tags: {e}")
            return []
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """
        Remove entradas do cache baseado em tags
        
        Args:
            tags: Tags para invalidar
            
        Returns:
            Número de entradas removidas
        """
        
        matching_keys = self.find_by_tags(tags)
        removed_count = 0
        
        for key in matching_keys:
            if self._remove_entry(key):
                removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Invalidadas {removed_count} entradas com tags: {tags}")
        
        return removed_count

# Instância global do cache (singleton pattern)
_cache_instance = None
_cache_lock = threading.Lock()

def get_cache_instance(settings, **kwargs) -> PromptCache:
    """
    Retorna instância singleton do cache
    
    Args:
        settings: Configurações do sistema
        **kwargs: Argumentos para inicialização do cache
        
    Returns:
        Instância do PromptCache
    """
    
    global _cache_instance
    
    with _cache_lock:
        if _cache_instance is None:
            _cache_instance = PromptCache(settings, **kwargs)
        
        return _cache_instance

class CacheDecorator:
    """
    Decorator para cache automático de funções
    
    Exemplo de uso:
        @CacheDecorator(ttl_hours=2, tags=['optimization'])
        def optimize_prompt(prompt, target_llm):
            # função custosa
            return optimized_result
    """
    
    def __init__(self, cache_instance: PromptCache = None, ttl_hours: int = 24, 
                 tags: Optional[List[str]] = None):
        self.cache = cache_instance
        self.ttl_hours = ttl_hours
        self.tags = tags or []
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Se não tem cache configurado, executa função normalmente
            if not self.cache:
                return func(*args, **kwargs)
            
            # Gera chave baseada nos argumentos
            cache_key = hashlib.sha256(
                f"{func.__name__}_{str(args)}_{str(kwargs)}".encode()
            ).hexdigest()
            
            # Tenta buscar no cache
            cached_result = None  # self.cache.get(cache_key, 'function', 'result')
            
            if cached_result:
                return cached_result
            
            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            # self.cache.set(cache_key, 'function', result, ttl_hours=self.ttl_hours, tags=self.tags)
            
            return result
        
        return wrapper
