"""
Sistema de Analytics do Prompt Router
Análise avançada de prompts, métricas e performance

Este módulo fornece análise detalhada de prompts, incluindo:
- Análise de complexidade
- Detecção de padrões
- Métricas de otimização
- Comparação entre versões
- Relatórios de performance
"""

import json
import re
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

from utils.logger import LoggerMixin, log_execution_time

@dataclass
class PromptAnalysis:
    """
    Estrutura para análise completa de um prompt
    """
    # Informações básicas
    prompt: str
    timestamp: str
    target_llm: str
    
    # Métricas básicas
    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    
    # Análise de complexidade
    complexity_score: float
    readability_score: float
    technical_density: float
    
    # Análise linguística
    language: str
    sentiment_score: float
    question_ratio: float
    instruction_ratio: float
    
    # Análise estrutural
    has_structure: bool
    structure_type: str
    code_blocks: int
    lists_count: int
    
    # Métricas de qualidade
    clarity_score: float
    specificity_score: float
    completeness_score: float
    
    # Otimização
    optimization_potential: float
    suggested_improvements: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)

class PromptAnalyzer(LoggerMixin):
    """
    Analisador avançado de prompts
    
    Fornece análises detalhadas de qualidade, complexidade,
    e otimizações potenciais para prompts.
    """
    
    def __init__(self, settings):
        """
        Inicializa o analisador
        
        Args:
            settings: Configurações do sistema
        """
        super().__init__()
        self.settings = settings
        
        # Carrega dicionários e padrões para análise
        self._load_analysis_patterns()
        
        self.logger.info("PromptAnalyzer inicializado")
    
    def _load_analysis_patterns(self):
        """Carrega padrões para análise linguística e técnica"""
        
        # Palavras técnicas comuns
        self.technical_terms = {
            'programming': ['função', 'código', 'algoritmo', 'variável', 'classe', 'método', 'debug', 'api'],
            'ai_ml': ['machine learning', 'inteligência artificial', 'modelo', 'treinamento', 'dados'],
            'business': ['estratégia', 'roi', 'kpi', 'análise', 'mercado', 'vendas', 'marketing'],
            'academic': ['pesquisa', 'estudo', 'análise', 'teoria', 'hipótese', 'evidência']
        }
        
        # Padrões de instruções
        self.instruction_patterns = [
            r'(?:crie|faça|desenvolva|implemente|escreva|analise|explique|descreva)',
            r'(?:por favor|preciso|gostaria|poderia)',
            r'(?:passo a passo|detalhado|específico|claro)'
        ]
        
        # Padrões de perguntas
        self.question_patterns = [
            r'\?',
            r'(?:como|quando|onde|por que|o que|qual|quais)',
            r'(?:é possível|você pode|consegue)'
        ]
        
        # Indicadores de qualidade
        self.quality_indicators = {
            'clarity': ['claro', 'específico', 'detalhado', 'preciso'],
            'completeness': ['completo', 'abrangente', 'todos', 'incluir'],
            'structure': ['passo', 'etapa', 'primeiro', 'segundo', 'lista']
        }
    
    @log_execution_time
    def analyze(self, prompt: str, target_llm: str = 'universal') -> PromptAnalysis:
        """
        Realiza análise completa de um prompt
        
        Args:
            prompt: Prompt a ser analisado
            target_llm: LLM de destino
            
        Returns:
            PromptAnalysis com dados completos da análise
        """
        
        self.logger.info(f"Iniciando análise do prompt para {target_llm}")
        
        # Análises básicas
        basic_metrics = self._analyze_basic_metrics(prompt)
        
        # Análises de complexidade
        complexity_metrics = self._analyze_complexity(prompt)
        
        # Análises linguísticas
        linguistic_metrics = self._analyze_language(prompt)
        
        # Análises estruturais
        structure_metrics = self._analyze_structure(prompt)
        
        # Análises de qualidade
        quality_metrics = self._analyze_quality(prompt)
        
        # Análises de otimização
        optimization_metrics = self._analyze_optimization_potential(prompt, target_llm)
        
        # Cria objeto de análise completa
        analysis = PromptAnalysis(
            prompt=prompt,
            timestamp=datetime.now().isoformat(),
            target_llm=target_llm,
            
            # Métricas básicas
            **basic_metrics,
            
            # Complexidade
            **complexity_metrics,
            
            # Linguística
            **linguistic_metrics,
            
            # Estrutura
            **structure_metrics,
            
            # Qualidade
            **quality_metrics,
            
            # Otimização
            **optimization_metrics
        )
        
        self.logger.info("Análise concluída")
        return analysis
    
    def _analyze_basic_metrics(self, prompt: str) -> Dict[str, int]:
        """Análise de métricas básicas"""
        
        return {
            'char_count': len(prompt),
            'word_count': len(prompt.split()),
            'sentence_count': len(re.split(r'[.!?]+', prompt.strip())),
            'paragraph_count': len([p for p in prompt.split('\n\n') if p.strip()])
        }
    
    def _analyze_complexity(self, prompt: str) -> Dict[str, float]:
        """Análise de complexidade do prompt"""
        
        words = prompt.split()
        
        # Complexidade baseada em comprimento médio das palavras
        avg_word_length = statistics.mean([len(word) for word in words]) if words else 0
        
        # Densidade técnica (palavras técnicas / total)
        technical_count = sum(1 for word in words 
                            for term_list in self.technical_terms.values() 
                            for term in term_list 
                            if term.lower() in word.lower())
        
        technical_density = technical_count / len(words) if words else 0
        
        # Score de complexidade geral (0-1)
        complexity_factors = [
            min(len(prompt) / 1000, 1.0) * 0.3,  # Comprimento
            min(avg_word_length / 10, 1.0) * 0.3,  # Palavras complexas
            min(technical_density * 5, 1.0) * 0.2,  # Densidade técnica
            min(prompt.count(',') / 10, 1.0) * 0.1,  # Estrutura complexa
            min(prompt.count('(') / 5, 1.0) * 0.1   # Explicações em parênteses
        ]
        
        complexity_score = sum(complexity_factors)
        
        # Score de legibilidade (simplificado)
        sentences = re.split(r'[.!?]+', prompt.strip())
        avg_sentence_length = statistics.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0
        readability_score = max(0, 1 - (avg_sentence_length - 15) / 20)  # Ideal ~15 palavras por frase
        
        return {
            'complexity_score': round(complexity_score, 3),
            'readability_score': round(readability_score, 3),
            'technical_density': round(technical_density, 3)
        }
    
    def _analyze_language(self, prompt: str) -> Dict[str, Any]:
        """Análise linguística do prompt"""
        
        prompt_lower = prompt.lower()
        
        # Detecção de idioma (simplificada)
        portuguese_indicators = ['e ', 'o ', 'a ', 'de ', 'em ', 'para ', 'com ', 'não ', 'é ', 'do ', 'da ']
        english_indicators = ['the ', 'and ', 'a ', 'an ', 'of ', 'in ', 'for ', 'with ', 'is ', 'are ']
        
        pt_score = sum(1 for indicator in portuguese_indicators if indicator in prompt_lower)
        en_score = sum(1 for indicator in english_indicators if indicator in prompt_lower)
        
        language = 'pt' if pt_score > en_score else 'en' if en_score > 0 else 'unknown'
        
        # Análise de sentimento (simplificada)
        positive_words = ['bom', 'ótimo', 'excelente', 'melhor', 'good', 'great', 'excellent', 'best']
        negative_words = ['ruim', 'péssimo', 'pior', 'erro', 'bad', 'terrible', 'worst', 'error']
        
        positive_count = sum(1 for word in positive_words if word in prompt_lower)
        negative_count = sum(1 for word in negative_words if word in prompt_lower)
        
        sentiment_score = (positive_count - negative_count) / max(len(prompt.split()) / 10, 1)
        
        # Ratios de perguntas e instruções
        question_matches = sum(len(re.findall(pattern, prompt_lower)) for pattern in self.question_patterns)
        instruction_matches = sum(len(re.findall(pattern, prompt_lower)) for pattern in self.instruction_patterns)
        
        total_words = len(prompt.split())
        question_ratio = question_matches / max(total_words / 20, 1)
        instruction_ratio = instruction_matches / max(total_words / 20, 1)
        
        return {
            'language': language,
            'sentiment_score': round(max(-1, min(1, sentiment_score)), 3),
            'question_ratio': round(min(1, question_ratio), 3),
            'instruction_ratio': round(min(1, instruction_ratio), 3)
        }
    
    def _analyze_structure(self, prompt: str) -> Dict[str, Any]:
        """Análise estrutural do prompt"""
        
        # Detecta estruturas
        has_xml_tags = bool(re.search(r'<\w+>', prompt))
        has_markdown = bool(re.search(r'#{1,6}\s', prompt) or '```' in prompt)
        has_bullets = bool(re.search(r'^\s*[-*•]\s', prompt, re.MULTILINE))
        has_numbers = bool(re.search(r'^\s*\d+\.\s', prompt, re.MULTILINE))
        
        has_structure = any([has_xml_tags, has_markdown, has_bullets, has_numbers])
        
        # Determina tipo de estrutura
        if has_xml_tags:
            structure_type = 'xml'
        elif has_markdown:
            structure_type = 'markdown'
        elif has_bullets or has_numbers:
            structure_type = 'list'
        else:
            structure_type = 'plain'
        
        # Conta elementos estruturais
        code_blocks = prompt.count('```')
        lists_count = len(re.findall(r'^\s*[-*•\d+\.]\s', prompt, re.MULTILINE))
        
        return {
            'has_structure': has_structure,
            'structure_type': structure_type,
            'code_blocks': code_blocks,
            'lists_count': lists_count
        }
    
    def _analyze_quality(self, prompt: str) -> Dict[str, float]:
        """Análise de qualidade do prompt"""
        
        prompt_lower = prompt.lower()
        words = prompt.split()
        
        # Score de clareza (baseado em indicadores de clareza)
        clarity_indicators = self.quality_indicators['clarity']
        clarity_count = sum(1 for indicator in clarity_indicators if indicator in prompt_lower)
        clarity_score = min(1.0, clarity_count / 2)  # Máximo 2 indicadores normalizados
        
        # Score de especificidade (baseado em detalhes e números)
        numbers_count = len(re.findall(r'\d+', prompt))
        specific_words = ['específico', 'detalhado', 'exato', 'preciso', 'specific', 'detailed', 'exact']
        specificity_count = sum(1 for word in specific_words if word in prompt_lower)
        
        specificity_score = min(1.0, (numbers_count / 5 + specificity_count / 2) / 2)
        
        # Score de completude (baseado em indicadores de abrangência)
        completeness_indicators = self.quality_indicators['completeness']
        completeness_count = sum(1 for indicator in completeness_indicators if indicator in prompt_lower)
        
        # Penaliza prompts muito curtos
        length_factor = min(1.0, len(words) / 20)  # Ideal >= 20 palavras
        completeness_score = min(1.0, (completeness_count / 2 + length_factor) / 2)
        
        return {
            'clarity_score': round(clarity_score, 3),
            'specificity_score': round(specificity_score, 3),
            'completeness_score': round(completeness_score, 3)
        }
    
    def _analyze_optimization_potential(self, prompt: str, target_llm: str) -> Dict[str, Any]:
        """Análise de potencial de otimização"""
        
        improvements = []
        optimization_factors = []
        
        # Verifica comprimento
        words = prompt.split()
        if len(words) < 10:
            improvements.append("Prompt muito curto - adicione mais contexto e detalhes")
            optimization_factors.append(0.3)
        elif len(words) > 500:
            improvements.append("Prompt muito longo - considere dividir em partes menores")
            optimization_factors.append(0.2)
        else:
            optimization_factors.append(0.0)
        
        # Verifica estrutura para o LLM alvo
        if target_llm == 'claude' and '<instructions>' not in prompt:
            improvements.append("Para Claude: considere usar tags XML como <instructions>")
            optimization_factors.append(0.2)
        
        if target_llm == 'cursor' and not any(term in prompt.lower() 
                                             for term in ['código', 'função', 'programação', 'code']):
            if any(term in prompt.lower() for term in ['criar', 'desenvolver', 'implementar']):
                improvements.append("Para Cursor: seja mais específico sobre o contexto de programação")
                optimization_factors.append(0.15)
        
        # Verifica clareza
        if not any(word in prompt.lower() for word in ['por favor', 'preciso', 'gostaria']):
            if len(words) > 20:
                improvements.append("Considere adicionar linguagem mais cortês e específica")
                optimization_factors.append(0.1)
        
        # Verifica instruções específicas
        if '?' in prompt and 'como' not in prompt.lower():
            improvements.append("Para perguntas, considere ser mais específico sobre o tipo de resposta esperada")
            optimization_factors.append(0.15)
        
        # Calcula potencial geral
        optimization_potential = sum(optimization_factors) if optimization_factors else 0.0
        optimization_potential = min(1.0, optimization_potential)
        
        return {
            'optimization_potential': round(optimization_potential, 3),
            'suggested_improvements': improvements
        }

class PromptComparator(LoggerMixin):
    """
    Comparador de prompts para análise de melhorias
    
    Permite comparar diferentes versões de prompts e
    identificar qual versão é mais efetiva.
    """
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.analyzer = PromptAnalyzer(settings)
        self.logger.info("PromptComparator inicializado")
    
    @log_execution_time
    def compare_prompts(self, prompt_a: str, prompt_b: str, 
                       target_llm: str = 'universal') -> Dict[str, Any]:
        """
        Compara dois prompts e retorna análise detalhada
        
        Args:
            prompt_a: Primeiro prompt (geralmente original)
            prompt_b: Segundo prompt (geralmente otimizado)
            target_llm: LLM de destino
            
        Returns:
            Análise comparativa detalhada
        """
        
        self.logger.info("Iniciando comparação de prompts")
        
        # Analisa ambos os prompts
        analysis_a = self.analyzer.analyze(prompt_a, target_llm)
        analysis_b = self.analyzer.analyze(prompt_b, target_llm)
        
        # Calcula diferenças
        improvements = self._calculate_improvements(analysis_a, analysis_b)
        
        # Determina qual é melhor
        winner = self._determine_winner(analysis_a, analysis_b)
        
        comparison = {
            'prompt_a': {
                'text': prompt_a,
                'analysis': analysis_a.to_dict()
            },
            'prompt_b': {
                'text': prompt_b,
                'analysis': analysis_b.to_dict()
            },
            'improvements': improvements,
            'winner': winner,
            'recommendation': self._generate_recommendation(analysis_a, analysis_b, winner),
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Comparação concluída. Vencedor: {winner}")
        return comparison
    
    def _calculate_improvements(self, analysis_a: PromptAnalysis, 
                              analysis_b: PromptAnalysis) -> Dict[str, float]:
        """Calcula melhorias entre prompts"""
        
        metrics_to_compare = [
            'complexity_score', 'readability_score', 'clarity_score',
            'specificity_score', 'completeness_score'
        ]
        
        improvements = {}
        for metric in metrics_to_compare:
            value_a = getattr(analysis_a, metric)
            value_b = getattr(analysis_b, metric)
            
            if value_a > 0:
                improvement = ((value_b - value_a) / value_a) * 100
                improvements[metric] = round(improvement, 2)
            else:
                improvements[metric] = 0.0
        
        return improvements
    
    def _determine_winner(self, analysis_a: PromptAnalysis, 
                         analysis_b: PromptAnalysis) -> str:
        """Determina qual prompt é melhor baseado em métricas"""
        
        # Pontuação ponderada
        weights = {
            'clarity_score': 0.25,
            'specificity_score': 0.20,
            'completeness_score': 0.20,
            'readability_score': 0.15,
            'complexity_score': -0.10,  # Negativo - menos complexidade é melhor
            'optimization_potential': -0.10  # Negativo - menos potencial = já otimizado
        }
        
        score_a = sum(getattr(analysis_a, metric) * weight 
                     for metric, weight in weights.items())
        score_b = sum(getattr(analysis_b, metric) * weight 
                     for metric, weight in weights.items())
        
        if score_b > score_a:
            return 'prompt_b'
        elif score_a > score_b:
            return 'prompt_a'
        else:
            return 'tie'
    
    def _generate_recommendation(self, analysis_a: PromptAnalysis,
                               analysis_b: PromptAnalysis, winner: str) -> str:
        """Gera recomendação baseada na comparação"""
        
        if winner == 'prompt_b':
            return f"Recomendo usar o Prompt B. Melhorias principais: maior clareza ({analysis_b.clarity_score:.2f} vs {analysis_a.clarity_score:.2f}) e completude ({analysis_b.completeness_score:.2f} vs {analysis_a.completeness_score:.2f})."
        
        elif winner == 'prompt_a':
            return f"O Prompt A original já é superior. Mantém melhor equilíbrio entre clareza e simplicidade."
        
        else:
            return "Ambos os prompts têm qualidade similar. Escolha baseada na preferência pessoal ou contexto específico."

class AnalyticsStorage(LoggerMixin):
    """
    Sistema de armazenamento para analytics do Prompt Router
    
    Gerencia histórico de análises, métricas e comparações.
    """
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.analytics_dir = settings.PROJECT_ROOT / 'analytics'
        self.analytics_dir.mkdir(exist_ok=True)
        
        self.analyses_file = self.analytics_dir / 'prompt_analyses.jsonl'
        self.comparisons_file = self.analytics_dir / 'prompt_comparisons.jsonl'
        
        self.logger.info("AnalyticsStorage inicializado")
    
    def save_analysis(self, analysis: PromptAnalysis):
        """Salva análise de prompt"""
        
        with open(self.analyses_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(analysis.to_dict(), ensure_ascii=False) + '\n')
        
        self.logger.debug("Análise salva no histórico")
    
    def save_comparison(self, comparison: Dict[str, Any]):
        """Salva comparação de prompts"""
        
        with open(self.comparisons_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(comparison, ensure_ascii=False) + '\n')
        
        self.logger.debug("Comparação salva no histórico")
    
    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Retorna resumo de analytics dos últimos N dias
        
        Args:
            days: Número de dias para análise
            
        Returns:
            Resumo de métricas e tendências
        """
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Carrega análises recentes
        recent_analyses = []
        if self.analyses_file.exists():
            with open(self.analyses_file, 'r', encoding='utf-8') as f:
                for line in f:
                    analysis = json.loads(line)
                    analysis_date = datetime.fromisoformat(analysis['timestamp'].replace('Z', '+00:00'))
                    if analysis_date >= cutoff_date:
                        recent_analyses.append(analysis)
        
        if not recent_analyses:
            return {'message': 'Não há dados suficientes para gerar relatório'}
        
        # Calcula estatísticas
        summary = {
            'period_days': days,
            'total_analyses': len(recent_analyses),
            'average_scores': self._calculate_average_scores(recent_analyses),
            'top_llm_targets': self._get_top_targets(recent_analyses),
            'complexity_distribution': self._get_complexity_distribution(recent_analyses),
            'language_distribution': self._get_language_distribution(recent_analyses),
            'improvement_suggestions': self._get_common_improvements(recent_analyses),
            'generated_at': datetime.now().isoformat()
        }
        
        return summary
    
    def _calculate_average_scores(self, analyses: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula scores médios"""
        
        metrics = ['complexity_score', 'readability_score', 'clarity_score',
                  'specificity_score', 'completeness_score']
        
        averages = {}
        for metric in metrics:
            scores = [analysis[metric] for analysis in analyses if metric in analysis]
            if scores:
                averages[metric] = round(statistics.mean(scores), 3)
            else:
                averages[metric] = 0.0
        
        return averages
    
    def _get_top_targets(self, analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Retorna LLMs mais utilizados"""
        
        targets = [analysis['target_llm'] for analysis in analyses]
        return dict(Counter(targets).most_common())
    
    def _get_complexity_distribution(self, analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Distribição de complexidade"""
        
        distribution = {'low': 0, 'medium': 0, 'high': 0}
        
        for analysis in analyses:
            score = analysis.get('complexity_score', 0)
            if score < 0.3:
                distribution['low'] += 1
            elif score < 0.7:
                distribution['medium'] += 1
            else:
                distribution['high'] += 1
        
        return distribution
    
    def _get_language_distribution(self, analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Distribução de idiomas"""
        
        languages = [analysis.get('language', 'unknown') for analysis in analyses]
        return dict(Counter(languages))
    
    def _get_common_improvements(self, analyses: List[Dict[str, Any]]) -> List[str]:
        """Sugestões de melhoria mais comuns"""
        
        all_improvements = []
        for analysis in analyses:
            improvements = analysis.get('suggested_improvements', [])
            all_improvements.extend(improvements)
        
        # Retorna as 5 mais comuns
        return [item for item, count in Counter(all_improvements).most_common(5)]
