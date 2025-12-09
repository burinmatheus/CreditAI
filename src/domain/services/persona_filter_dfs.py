"""
Domain Service: Persona Filter (DFS - Depth First Search)
Identifica o perfil do cliente usando busca em profundidade
"""
from typing import Dict, Optional, Callable, List, Tuple
from src.domain.entities.credit_request import CreditRequest


class PersonaFilterDFS:
    """
    Filtro de Persona usando DFS
    Classifica clientes em diferentes personas baseado em características
    """
    
    def __init__(self):
        # Árvore de decisão por persona. Cada nível é explorado em profundidade.
        self.persona_rules: Dict[str, List[Tuple[str, Callable]]] = {
            "premium": [
                ("Renda >= 10000", lambda p: p.income >= 10000),
                ("Score >= 750", lambda p: p.credit_score is not None and p.credit_score >= 750),
                ("Emprego qualificado", lambda p: p.employment_status in ["employed", "self_employed"]),
            ],
            "standard": [
                ("Renda >= 3000", lambda p: p.income >= 3000),
                ("Score >= 650", lambda p: p.credit_score is not None and p.credit_score >= 650),
                ("Emprego qualificado", lambda p: p.employment_status in ["employed", "self_employed"]),
            ],
            "basic": [
                ("Renda >= 1500", lambda p: p.income >= 1500),
                ("Score >= 550", lambda p: p.credit_score is not None and p.credit_score >= 550),
                ("Emprego qualificado ou aposentado", lambda p: p.employment_status in ["employed", "self_employed", "retired"]),
            ],
        }
    
    def identify_persona(self, request: CreditRequest) -> tuple[Optional[str], float]:
        """
        Identifica a persona do cliente usando DFS
        
        Returns:
            tuple[persona, confidence]: Nome da persona e confiança da classificação
        """
        profile = request.customer_profile

        # Busca em profundidade: percorre cada persona avaliando suas regras em sequência
        for persona_name in ["premium", "standard", "basic"]:
            rules = self.persona_rules[persona_name]
            matched, _ = self._dfs_rules(rules, profile, 0, [])
            if matched:
                confidence = self._calculate_confidence(profile, persona_name)
                return persona_name, confidence
        
        # Se não se encaixar em nenhuma persona
        return None, 0.0
    
    def _dfs_rules(
        self,
        rules: List[Tuple[str, Callable]],
        profile,
        idx: int,
        path: List[str],
    ) -> tuple[bool, List[str]]:
        """Percorre recursivamente as regras; para ao primeiro fracasso."""
        if idx >= len(rules):
            return True, path

        desc, predicate = rules[idx]
        current_path = path + [desc]
        if not predicate(profile):
            return False, current_path

        return self._dfs_rules(rules, profile, idx + 1, current_path)

    def _calculate_confidence(self, profile, persona_name: str) -> float:
        """Calcula confiança com base nas regras satisfeitas."""
        baseline = {
            "premium": {"min_income": 10000, "min_credit_score": 750},
            "standard": {"min_income": 3000, "min_credit_score": 650},
            "basic": {"min_income": 1500, "min_credit_score": 550},
        }

        rules = baseline[persona_name]
        confidence = 0.0

        income_ratio = profile.income / (rules["min_income"] * 2)
        confidence += min(income_ratio, 0.4)

        if profile.credit_score:
            score_ratio = profile.credit_score / 850
            confidence += min(score_ratio * 0.4, 0.4)
        else:
            confidence += 0.2

        if profile.employment_status in ["employed", "self_employed"]:
            confidence += 0.2
        else:
            confidence += 0.1

        return min(confidence, 1.0)
    
    def get_persona_limits(self, persona: str) -> Dict[str, float]:
        """Retorna os limites de crédito para cada persona"""
        limits = {
            "premium": {
                "max_limit": 100000,
                "min_limit": 10000,
                "income_multiplier": 5.0
            },
            "standard": {
                "max_limit": 50000,
                "min_limit": 3000,
                "income_multiplier": 3.0
            },
            "basic": {
                "max_limit": 20000,
                "min_limit": 1000,
                "income_multiplier": 2.0
            }
        }
        
        return limits.get(persona, limits["basic"])
