"""
Domain Service: Credit Limit Calculator (BFS - Breadth First Search)
Calcula limite de crédito usando busca em largura
"""
from typing import Dict, List
from src.domain.entities.credit_request import CreditRequest


class CreditLimitBFS:
    """
    Calculadora de Limite de Crédito usando BFS
    Explora diferentes fatores em camadas para determinar o limite
    """
    
    def calculate_limit(
        self,
        request: CreditRequest,
        persona_limits: Dict[str, float]
    ) -> tuple[float, Dict[str, float]]:
        """
        Calcula o limite de crédito usando BFS
        
        Returns:
            tuple[limit, factors]: Limite calculado e fatores contributivos
        """
        # Camada 1: Limite base por renda
        income_limit = self._calculate_income_based_limit(
            request.monthly_income,
            persona_limits["income_multiplier"]
        )
        
        # Camada 2: Ajuste por credit score
        score_factor = self._calculate_score_factor(request.credit_score)
        
        # Camada 3: Ajuste por emprego
        employment_factor = self._calculate_employment_factor(request.employment_status)
        
        # Camada 4: Ajuste por histórico
        history_factor = self._calculate_history_factor(
            request.has_previous_loans,
            request.debt_to_income_ratio
        )
        
        # Combinar todos os fatores (BFS - processamento em camadas)
        base_limit = income_limit * score_factor * employment_factor * history_factor
        
        # Aplicar limites mínimo e máximo da persona
        final_limit = max(
            persona_limits["min_limit"],
            min(base_limit, persona_limits["max_limit"])
        )
        
        # Arredondar para múltiplo de 1000
        final_limit = round(final_limit / 1000) * 1000
        
        factors = {
            "income_limit": income_limit,
            "score_factor": score_factor,
            "employment_factor": employment_factor,
            "history_factor": history_factor,
            "final_limit": final_limit
        }
        
        return final_limit, factors
    
    def _calculate_income_based_limit(self, monthly_income: float, multiplier: float) -> float:
        """Camada 1: Calcula limite base por renda"""
        return monthly_income * multiplier
    
    def _calculate_score_factor(self, credit_score: int) -> float:
        """Camada 2: Fator de ajuste por credit score"""
        if credit_score is None:
            return 0.8  # Penalidade por falta de score
        
        if credit_score >= 800:
            return 1.2
        elif credit_score >= 750:
            return 1.1
        elif credit_score >= 700:
            return 1.0
        elif credit_score >= 650:
            return 0.9
        elif credit_score >= 600:
            return 0.8
        else:
            return 0.7
    
    def _calculate_employment_factor(self, employment_status: str) -> float:
        """Camada 3: Fator de ajuste por status de emprego"""
        factors = {
            "employed": 1.0,
            "self_employed": 0.95,
            "retired": 0.85,
            "unemployed": 0.5
        }
        return factors.get(employment_status, 0.7)
    
    def _calculate_history_factor(
        self,
        has_previous_loans: bool,
        debt_to_income_ratio: float
    ) -> float:
        """Camada 4: Fator de ajuste por histórico"""
        factor = 1.0
        
        # Bônus por ter histórico de empréstimos
        if has_previous_loans:
            factor *= 1.05
        else:
            factor *= 0.95
        
        # Penalidade por alto endividamento
        if debt_to_income_ratio is not None:
            if debt_to_income_ratio < 0.2:
                factor *= 1.1
            elif debt_to_income_ratio < 0.3:
                factor *= 1.0
            elif debt_to_income_ratio < 0.4:
                factor *= 0.9
            else:
                factor *= 0.7
        
        return factor
    
    def validate_requested_amount(
        self,
        requested_amount: float,
        calculated_limit: float
    ) -> tuple[bool, str]:
        """Valida se o valor solicitado está dentro do limite"""
        if requested_amount <= 0:
            return False, "Valor solicitado inválido"
        
        if requested_amount > calculated_limit:
            return False, f"Valor solicitado excede o limite aprovado de R$ {calculated_limit:,.2f}"
        
        if requested_amount < 500:
            return False, "Valor mínimo de solicitação é R$ 500,00"
        
        return True, "Valor aprovado"
