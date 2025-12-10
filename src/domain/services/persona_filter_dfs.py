from typing import Callable, Optional, Dict, Any
from src.domain.entities.credit_request import CreditRequest


class DecisionNode:
    """
    Nó de árvore de decisão.
    """
    def __init__(
        self,
        description: str,
        condition: Optional[Callable[[Any], bool]] = None,
        true_branch: Optional["DecisionNode"] = None,
        false_branch: Optional["DecisionNode"] = None,
        persona: Optional[str] = None
    ):
        self.description = description
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.persona = persona

    def is_leaf(self) -> bool:
        return self.persona is not None


class PersonaFilterDFS:
    """
    Filtro de persona com Árvore de Decisão usando DFS.
    """

    def __init__(self):
        self.root = self._build_tree()

    def _build_tree(self) -> DecisionNode:
        """Constrói a árvore de decisão completa."""

        # --- BASIC branch ---
        basic_leaf = DecisionNode("Basic Persona", persona="basic")

        basic_score = DecisionNode(
            "Score >= 0?",
            condition=lambda p: p.credit_score is not None and p.credit_score >= 0,
            true_branch=basic_leaf,
            false_branch=None,
        )

        basic_employment = DecisionNode(
            "Emprego qualificado ou aposentado?",
            condition=lambda p: p.employment_status in ["employed", "self_employed", "retired"],
            true_branch=basic_score,
            false_branch=None
        )

        basic_income = DecisionNode(
            "Renda >= 0?",
            condition=lambda p: p.income >= 0,
            true_branch=basic_employment,
            false_branch=None
        )

        # --- STANDARD branch ---
        standard_leaf = DecisionNode("Standard Persona", persona="standard")

        standard_score = DecisionNode(
            "Score >= 550?",
            condition=lambda p: p.credit_score is not None and p.credit_score >= 550,
            true_branch=standard_leaf,
            false_branch=None,
        )

        standard_employment = DecisionNode(
            "Emprego qualificado?",
            condition=lambda p: p.employment_status in ["employed", "self_employed"],
            true_branch=standard_score,
            false_branch=None,
        )

        standard_income = DecisionNode(
            "Renda >= 2000?",
            condition=lambda p: p.income >= 2000,
            true_branch=standard_employment,
            false_branch=basic_income,  # fallback
        )

        # --- PREMIUM branch ---
        premium_leaf = DecisionNode("Premium Persona", persona="premium")

        premium_score = DecisionNode(
            "Score >= 750?",
            condition=lambda p: p.credit_score is not None and p.credit_score >= 750,
            true_branch=premium_leaf,
            false_branch=standard_income,
        )

        premium_employment = DecisionNode(
            "Emprego qualificado?",
            condition=lambda p: p.employment_status in ["employed", "self_employed"],
            true_branch=premium_score,
            false_branch=standard_income
        )

        premium_income = DecisionNode(
            "Renda >= 10000?",
            condition=lambda p: p.income >= 10000,
            true_branch=premium_employment,
            false_branch=standard_income
        )

        return premium_income

    # ---------------- DFS REAL ---------------- #

    def identify_persona(self, request: CreditRequest) -> tuple[Optional[str], float]:
        """
        Executa DFS na árvore de decisão para encontrar a persona.
        """
        profile = request.customer_profile
        persona = self._dfs(self.root, profile)
        confidence = self._calculate_confidence(profile, persona) if persona else 0.0
        return persona, confidence

    def _dfs(self, node: DecisionNode, profile) -> Optional[str]:
        """
        DFS real: percorre árvore de decisão em profundidade.
        """
        if node.is_leaf():
            return node.persona

        # Caso a condição seja falsa e exista um false_branch, seguimos por ele
        if not node.condition(profile):
            return self._dfs(node.false_branch, profile) if node.false_branch else None

        # Caso verdadeiro, seguimos o true_branch
        return self._dfs(node.true_branch, profile)

    # ------------------------------------------ #

    def _calculate_confidence(self, profile, persona_name: Optional[str]) -> float:
        if persona_name is None:
            return 0.0

        baseline = {
            "premium": {"min_income": 10000, "min_credit_score": 750},
            "standard": {"min_income": 2000, "min_credit_score": 550},
            "basic": {"min_income": 0, "min_credit_score": 0},
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
        limits = {
            "premium": {"max_limit": 100000, "min_limit": 10000, "income_multiplier": 5.0},
            "standard": {"max_limit": 50000, "min_limit": 3000, "income_multiplier": 3.0},
            "basic": {"max_limit": 20000, "min_limit": 1000, "income_multiplier": 2.0},
        }
        return limits.get(persona, limits["basic"])
