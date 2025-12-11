"""
Serviço de Análise de Crédito
Orquestra as 4 etapas do pipeline de IA
"""
from datetime import datetime
from typing import Optional
from src.domain.entities.credit_request import CreditRequest
from src.domain.entities.credit_analysis import (
    CreditAnalysisResult, ApprovalStatus, RejectionReason,
    PersonaFilterResult, CreditLimit, RiskAssessment
)
from src.domain.services.persona_filter_dfs import PersonaFilterDFS
from src.domain.services.credit_limit_bfs import CreditLimitBFS
from src.domain.services.risk_fuzzy_logic import RiskFuzzyLogic
from src.domain.services.approval_neural_network import ApprovalNeuralNetwork


class CreditAnalysisService:
    """
    Pipeline de Análise de Crédito com 4 Técnicas de IA
    
    Etapa 1: Filtro por Persona (DFS - Busca em Profundidade)
    Etapa 2: Cálculo de Limite (BFS - Busca em Amplitude)
    Etapa 3: Avaliação de Risco (Lógica Fuzzy com scikit-fuzzy)
    Etapa 4: Decisão Final (Rede Neural com TensorFlow)
    """
    
    def __init__(self):
        # Inicializa os 4 componentes de IA
        self.persona_filter = PersonaFilterDFS()
        self.credit_limit_calculator = CreditLimitBFS()
        self.risk_evaluator = RiskFuzzyLogic()
        self.approval_network = ApprovalNeuralNetwork()
    
    def analyze(self, credit_request: CreditRequest) -> CreditAnalysisResult:
        """Executa análise completa de crédito em 4 etapas."""

        print(f"\n{'='*70}")
        print("PIPELINE DE ANÁLISE DE CRÉDITO COM IA")
        print(f"Cliente: {credit_request.customer_profile.name}")
        print(f"Valor Solicitado: R$ {credit_request.requested_amount:,.2f}")
        print(f"{'='*70}\n")

        # ===== ETAPA 1: DFS - FILTRO POR PERSONA =====
        print("🌳 ETAPA 1/4: Filtro por Persona (DFS - Depth First Search)")
        print("-" * 70)

        persona_name, persona_confidence = self.persona_filter.identify_persona(credit_request)
        persona_limits = self.persona_filter.get_persona_limits(persona_name) if persona_name else None

        if not persona_name:
            print("❌ Cliente não se enquadra em nenhuma persona")
            persona_result = PersonaFilterResult(
                passed=False,
                persona=None,
                confidence=0.0,
                reason="Cliente não atende aos critérios mínimos de nenhuma persona",
            )
            return CreditAnalysisResult(
                request_id=credit_request.request_id,
                customer_id=credit_request.customer_profile.customer_id,
                analysis_date=datetime.now(),
                persona_filter=persona_result,
                credit_limit=None,
                risk_assessment=None,
                approval_status=ApprovalStatus.REJECTED,
                rejection_reason=RejectionReason.PERSONA_FILTER,
                approval_confidence=0.0,
            )

        print(f"   Persona Identificada: {persona_name.upper()}")
        print(f"   Confiança: {persona_confidence*100:.1f}%")
        print(f"   Limite Máximo: R$ {persona_limits['max_limit']:,.2f}")

        persona_result = PersonaFilterResult(
            passed=True,
            persona=persona_name,
            confidence=persona_confidence,
            reason=f"Cliente classificado como {persona_name}",
        )

        print()

        # ===== ETAPA 2: BFS - CÁLCULO DE LIMITE =====
        print("🔢 ETAPA 2/4: Cálculo de Limite (BFS - Breadth First Search)")
        print("-" * 70)

        calculated_limit, limit_factors = self.credit_limit_calculator.calculate_limit(
            credit_request,
            persona_limits,
        )

        _, validation_msg = self.credit_limit_calculator.validate_requested_amount(
            credit_request.requested_amount,
            calculated_limit,
        )

        # Obter taxa de juros do produto
        product_config = self.credit_limit_calculator.PRODUCT_CONFIG[credit_request.product_type]
        interest_rate = product_config["base_rate"]
        max_installments = min(
            credit_request.requested_installments,
            product_config["max_installments"]
        )
        
        # Usar a parcela calculada pelo BFS (que já inclui juros)
        max_installment_value = limit_factors.get('monthly_payment', calculated_limit / max_installments)

        credit_limit_obj = CreditLimit(
            approved_amount=calculated_limit,
            max_installment_value=max_installment_value,
            max_installments=max_installments,
            interest_rate=interest_rate,
            factors=limit_factors,
        )

        # Calcular parcela prevista caso o cliente seja aprovado (estima com valores solicitados/capados)
        expected_installments = min(credit_request.requested_installments, max_installments)
        expected_amount = min(credit_request.requested_amount, calculated_limit)
        if interest_rate > 0:
            _factor = (1 + interest_rate) ** expected_installments
            expected_monthly = (
                expected_amount * (interest_rate * _factor) / (_factor - 1)
            )
        else:
            expected_monthly = expected_amount / max(expected_installments, 1)
        # Calcular markup simples para comparação (ex.: 25% como no seu cálculo manual)
        simple_markup_rate = 0.25
        simple_monthly = (expected_amount / max(expected_installments, 1)) * (1 + simple_markup_rate)

        # Anexar ao dicionário de fatores para reaproveitamento no resumo
        credit_limit_obj.factors['expected_monthly'] = expected_monthly

        print(f"   Limite Base (Renda): R$ {limit_factors['income_limit']:,.2f}")
        print(f"   Fator Score: {limit_factors['score_factor']:.2f}x")
        print(f"   Fator Emprego: {limit_factors['employment_factor']:.2f}x")
        print(f"   Fator Histórico: {limit_factors['history_factor']:.2f}x")
        print(f"   Limite Final Aprovado: R$ {calculated_limit:,.2f}")
        print(f"   Percentual de Juros mensal: {interest_rate * 100:.2f}% a.m.")
        print(f"   Validação: {validation_msg}")


        print()

        # ===== ETAPA 3: FUZZY LOGIC - AVALIAÇÃO DE RISCO =====
        print("🎲 ETAPA 3/4: Avaliação de Risco (Fuzzy Logic - scikit-fuzzy)")
        print("-" * 70)

        risk_assessment_obj = self.risk_evaluator.assess_risk(
            credit_request.customer_profile,
            credit_limit_obj.approved_amount,
            credit_request.requested_amount,
        )

        # ===== ETAPA 4: RNA (PyTorch) - DECISÃO FINAL =====
        print("\n")
        print("🧠 ETAPA 4/4: Decisão Final (Rede Neural - PyTorch)")
        print("-" * 70)

        status, confidence, reasons, probabilities = self.approval_network.decide_approval(
            credit_request.customer_profile,
            credit_limit_obj.approved_amount,
            credit_request.requested_amount,
            risk_assessment_obj,
        )

        approved_amount = 0.0
        approved_installments = 0
        approved_rate = credit_limit_obj.interest_rate
        monthly_payment = 0.0

        if status == ApprovalStatus.APPROVED:
            approved_amount = min(credit_request.requested_amount, credit_limit_obj.approved_amount)
            approved_installments = min(credit_request.requested_installments, credit_limit_obj.max_installments)
            factor = (1 + approved_rate) ** approved_installments
            monthly_payment = (
                approved_amount * (approved_rate * factor) / (factor - 1)
                if approved_rate > 0 else approved_amount / max(approved_installments, 1)
            )

        rejection_reason: Optional[RejectionReason] = None
        if status == ApprovalStatus.REJECTED:
            rejection_reason = (
                RejectionReason.HIGH_RISK
                if risk_assessment_obj.risk_score > 0.65
                else RejectionReason.OTHER
            )

        print(f"   Decisão Final: {status.value.upper()}")
        print(f"   Confiança: {confidence*100:.1f}%")
        print(f"   Motivos: {', '.join(reasons) if reasons else 'Outro'}")
        print("   Probabilidades RNA:")
        prob_display = [
            ("Aprovação", probabilities.get("approved", 0.0)),
            ("Pendente", probabilities.get("pending", 0.0)),
            ("Rejeição", probabilities.get("rejected", 0.0)),
        ]
        for status_name, probability in prob_display:
            print(f"      {status_name}: {probability*100:.1f}%")
        print(f"\n{'='*70}\n")

        return CreditAnalysisResult(
            request_id=credit_request.request_id,
            customer_id=credit_request.customer_profile.customer_id,
            analysis_date=datetime.now(),
            persona_filter=persona_result,
            credit_limit=credit_limit_obj,
            risk_assessment=risk_assessment_obj,
            approval_status=status,
            rejection_reason=rejection_reason,
            approval_confidence=confidence,
            neural_network_probabilities=probabilities,
            approved_amount=approved_amount,
            approved_installments=approved_installments,
            approved_interest_rate=approved_rate,
            monthly_payment=monthly_payment,
        )
    
    def get_analysis_summary(self, result: CreditAnalysisResult) -> str:
        """Retorna resumo textual da análise"""
        lines = [
            "="*60,
            "RESUMO DA ANÁLISE DE CRÉDITO",
            "="*60,
            f"ID da Solicitação: {result.request_id}",
            f"Cliente: {result.customer_id}",
            f"Data da Análise: {result.analysis_date.strftime('%d/%m/%Y %H:%M')}",
            "",
            "ETAPA 1 - Filtro por Persona (DFS):",
            f"  Status: {'Reprovado' if not result.persona_filter.passed else 'Aprovado'}",
        ]
        
        if not result.persona_filter.passed:
            lines.append(f"  Motivo: {result.persona_filter.reason}")
        
        if result.credit_limit:
            lines.extend([
                "",
                "ETAPA 2 - Limite de Crédito (BFS):",
                f"  Limite Aprovado: R$ {result.credit_limit.approved_amount:,.2f}",
                f"  Parcela Máxima: R$ {result.credit_limit.max_installment_value:,.2f}",
                f"  Parcela Prevista (se aprovado): R$ {result.credit_limit.factors.get('expected_monthly', result.monthly_payment):,.2f}",
                f"  Prazo Máximo: {result.credit_limit.max_installments}x",
                f"  Taxa de Juros Mensal: {result.credit_limit.interest_rate * 100:.2f}% a.m.",
            ])
        
        if result.risk_assessment:
            lines.extend([
                "",
                "ETAPA 3 - Avaliação de Risco (Fuzzy):",
                f"  Nível de Risco: {result.risk_assessment.risk_level.value.upper()}",
                f"  Score de Risco: {result.risk_assessment.risk_score:.3f}",
            ])
        
        lines.extend([
            "",
            "ETAPA 4 - Decisão Final (RNA):",
            f"  Status: {result.approval_status.value.upper()}",
            f"  Confiança: {result.neural_network_confidence * 100:.1f}%" if result.neural_network_confidence else "  Confiança: N/A",
        ])
        
        if result.is_approved():
            lines.extend([
                "",
                "CRÉDITO APROVADO:",
                f"  Valor: R$ {result.approved_amount:,.2f}",
                f"  Parcelas: {result.approved_installments}x",
                f"  Valor da Parcela: R$ {result.monthly_payment:,.2f}",
                f"  Taxa: {result.approved_interest_rate * 100:.2f}% a.m.",
            ])
        elif result.rejection_reason:
            lines.extend([
                "",
                "MOTIVO DA REJEIÇÃO:",
                f"  {result.get_rejection_description()}",
            ])
        
        lines.append("="*60)
        return "\n".join(lines)
