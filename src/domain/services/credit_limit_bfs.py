"""
Domain Service: Credit Limit Calculator (BFS - Breadth First Search)
Calcula limite de crédito usando exploração em largura do espaço de valores/parcela
"""
from collections import deque
from typing import Dict, List, Tuple
from src.domain.entities.credit_request import CreditRequest, ProductType


class CreditLimitBFS:
    """
    Calculadora de Limite de Crédito usando BFS
    Explora diferentes fatores em camadas para determinar o limite
    """

    # Configuração de produtos de crédito para listagem na API
    PRODUCT_CONFIG: Dict[ProductType, Dict[str, float | int]] = {
        ProductType.PERSONAL_LOAN: {
            "min_amount": 1000.0,
            "max_amount": 50000.0,
            "max_installments": 48,
            "base_rate": 0.025,
        },
        ProductType.CREDIT_CARD: {
            "min_amount": 500.0,
            "max_amount": 10000.0,
            "max_installments": 24,
            "base_rate": 0.035,
        },
        ProductType.AUTO_LOAN: {
            "min_amount": 5000.0,
            "max_amount": 150000.0,
            "max_installments": 72,
            "base_rate": 0.018,
        },
        ProductType.HOME_LOAN: {
            "min_amount": 50000.0,
            "max_amount": 1000000.0,
            "max_installments": 360,
            "base_rate": 0.012,
        },
    }
    
    def calculate_limit(
        self,
        request: CreditRequest,
        persona_limits: Dict[str, float],
    ) -> tuple[float, Dict[str, float]]:
        """
        Calcula o limite usando BFS real sobre estados (valor, parcelas).
        """
        profile = request.customer_profile
        product_cfg = self.PRODUCT_CONFIG[request.product_type]

        income_limit = self._calculate_income_based_limit(
            profile.income,
            persona_limits["income_multiplier"],
        )
        score_factor = self._calculate_score_factor(profile.credit_score)
        employment_factor = self._calculate_employment_factor(profile.employment_status)
        history_factor = self._calculate_history_factor(
            profile.num_existing_loans > 0,
            profile.debt_to_income_ratio,
        )

        factor_limit = income_limit * score_factor * employment_factor * history_factor
        search_cap = min(
            persona_limits["max_limit"],
            product_cfg["max_amount"],
            factor_limit,
        )

        min_amount = max(product_cfg["min_amount"], persona_limits["min_limit"])
        step = float(product_cfg.get("step", 500.0))

        best_amount = 0.0
        best_installments = 0
        best_payment = 0.0

        start_installments = min(request.requested_installments, product_cfg["max_installments"])
        start_state = (min_amount, max(1, start_installments))

        queue: deque[Tuple[float, int]] = deque([start_state])
        visited = set()

        while queue:
            amount, installments = queue.popleft()
            state_key = (round(amount, 2), installments)
            if state_key in visited:
                continue
            visited.add(state_key)

            if amount > search_cap:
                continue

            monthly_payment = self._pmt(
                product_cfg["base_rate"],
                installments,
                amount,
            )

            if monthly_payment <= profile.income * 0.3:
                if amount > best_amount:
                    best_amount = amount
                    best_installments = installments
                    best_payment = monthly_payment

                next_amount = amount + step
                if next_amount <= search_cap:
                    queue.append((next_amount, installments))

            # Explorar variações de prazo para aliviar parcela
            if installments < product_cfg["max_installments"]:
                queue.append((amount, installments + 1))

        if best_amount == 0.0:
            best_amount = min_amount
            best_installments = start_state[1]
            best_payment = self._pmt(product_cfg["base_rate"], best_installments, best_amount)

        factors = {
            "income_limit": income_limit,
            "score_factor": score_factor,
            "employment_factor": employment_factor,
            "history_factor": history_factor,
            "search_cap": search_cap,
            "best_installments": best_installments,
            "monthly_payment": best_payment,
        }

        return round(best_amount, 2), factors
    
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

    def _pmt(self, rate: float, installments: int, amount: float) -> float:
        """Calcula parcela mensal para avaliar estados do BFS."""
        n = max(1, installments)
        if rate <= 0:
            return amount / n
        factor = (1 + rate) ** n
        return amount * (rate * factor) / (factor - 1)
