"""
Domain Service: Persona Filter (DFS - Depth First Search)
Identifica o perfil do cliente usando busca em profundidade
"""
from typing import Dict, Optional
from src.domain.entities.credit_request import CreditRequest


class PersonaFilterDFS:
    """
    Filtro de Persona usando DFS
    Classifica clientes em diferentes personas baseado em características
    """
    
    def __init__(self):
        self.personas = {
            "premium": {
                "min_income": 10000,
                "min_credit_score": 750,
                "employment": ["employed", "self_employed"]
            },
            "standard": {
                "min_income": 3000,
                "min_credit_score": 650,
                "employment": ["employed", "self_employed"]
            },
            "basic": {
                "min_income": 1500,
                "min_credit_score": 550,
                "employment": ["employed", "self_employed", "retired"]
            }
        }
    
    def identify_persona(self, request: CreditRequest) -> tuple[Optional[str], float]:
        """
        Identifica a persona do cliente usando DFS
        
        Returns:
            tuple[persona, confidence]: Nome da persona e confiança da classificação
        """
        # DFS através das personas (da mais restritiva para menos)
        for persona_name in ["premium", "standard", "basic"]:
            persona_rules = self.personas[persona_name]
            
            if self._matches_persona(request, persona_rules):
                confidence = self._calculate_confidence(request, persona_rules)
                return persona_name, confidence
        
        # Se não se encaixar em nenhuma persona
        return None, 0.0
    
    def _matches_persona(self, request: CreditRequest, rules: Dict) -> bool:
        """Verifica se o request atende aos critérios da persona"""
        profile = request.customer_profile

        if profile.income < rules["min_income"]:
            return False
        
        if profile.credit_score and profile.credit_score < rules["min_credit_score"]:
            return False
        
        if profile.employment_status not in rules["employment"]:
            return False
        
        return True
    
    def _calculate_confidence(self, request: CreditRequest, rules: Dict) -> float:
        """Calcula a confiança da classificação (0-1)"""
        confidence = 0.0
        
        # Confiança baseada na renda (até 0.4)
        income_ratio = profile.income / (rules["min_income"] * 2)
        confidence += min(income_ratio, 0.4)
        
        # Confiança baseada no credit score (até 0.4)
        if profile.credit_score:
            score_ratio = profile.credit_score / 850  # Score máximo
            confidence += min(score_ratio * 0.4, 0.4)
        else:
            confidence += 0.2  # Confiança parcial se não tiver score
        
        # Confiança baseada no emprego (até 0.2)
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
