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
        """
        Executa análise completa de crédito em 4 etapas
        
        Args:
            credit_request: Solicitação de crédito
            
        Returns:
            CreditAnalysisResult com decisão e detalhes
        """
        print(f"\n{'='*70}")
        print(f"PIPELINE DE ANÁLISE DE CRÉDITO COM IA")
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
                reason="Cliente não atende aos critérios mínimos de nenhuma persona"
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
                approval_confidence=0.0
            )
        
        print(f"✅ Persona Identificada: {persona_name.upper()}")
        print(f"   Confiança: {persona_confidence*100:.1f}%")
        print(f"   Limite Máximo: R$ {persona_limits['max_limit']:,.2f}")
        
        persona_result = PersonaFilterResult(
            passed=True,
            persona=persona_name,
            confidence=persona_confidence,
            reason=f"Cliente classificado como {persona_name}"
        )
        
        print()
        
        # ===== ETAPA 2: BFS - CÁLCULO DE LIMITE =====
        print("🔢 ETAPA 2/4: Cálculo de Limite (BFS - Breadth First Search)")
        print("-" * 70)
        
        calculated_limit, limit_factors = self.credit_limit_calculator.calculate_limit(
            credit_request,
            persona_limits
        )
        
        is_sufficient, validation_msg = self.credit_limit_calculator.validate_requested_amount(
            credit_request.requested_amount,
            calculated_limit
        )
        
        print(f"   Limite Base (Renda): R$ {limit_factors['income_limit']:,.2f}")
        print(f"   Fator Score: {limit_factors['score_factor']:.2f}x")
        print(f"   Fator Emprego: {limit_factors['employment_factor']:.2f}x")
        print(f"   Fator Histórico: {limit_factors['history_factor']:.2f}x")
        print(f"✅ Limite Final Aprovado: R$ {calculated_limit:,.2f}")
        print(f"   Validação: {validation_msg}")
        
        credit_limit_obj = CreditLimit(
            approved_amount=calculated_limit,
            max_installment_value=calculated_limit / 24,  # Assumindo 24 parcelas
            max_installments=24,
            interest_rate=0.05,  # 5% a.m. exemplo
            factors=limit_factors
        )
        
        print()
        
        # ===== ETAPA 3: FUZZY LOGIC - AVALIAÇÃO DE RISCO =====
        print("🎲 ETAPA 3/4: Avaliação de Risco (Fuzzy Logic - scikit-fuzzy)")
        print("-" * 70)
        
        risk_score, risk_level, risk_components = self.risk_evaluator.assess_risk(credit_request)
        
        print(f"   Componentes Fuzzy:")
        print(f"   - % Renda Comprometida: {risk_components.get('percent_income', 0):.1f}%")
        print(f"   - Score de Crédito: {risk_components.get('credit_score', 0):.0f}")
        print(f"   - Histórico Pagamentos: {risk_components.get('payment_history', 0):.1f}")
        print(f"   - Distância RS: {risk_components.get('distance', 0):.0f} km")
        print(f"   - Tempo Emprego: {risk_components.get('employment_time', 0):.0f} meses")
        print(f"   - Idade: {risk_components.get('age', 0):.0f} anos")
        print(f"   - Tentativas Crédito: {risk_components.get('credit_attempts', 0):.0f}")
        print(f"")
        print(f"✅ Score de Risco: {risk_score:.2f}/10")
        print(f"   Classificação: {risk_level.upper()}")
        
        risk_assessment_obj = RiskAssessment(
            risk_score=risk_score,
            risk_level=risk_level,
            components=risk_components
        )
        
        print()
        
        # ===== ETAPA 4: RNA - DECISÃO FINAL =====
        print("🧠 ETAPA 4/4: Decisão Final (RNA - Rede Neural TensorFlow)")
        print("-" * 70)
        
        approval_decision = self.approval_network.evaluate(
            credit_request,
            persona_result,
            credit_limit_obj,
            risk_assessment_obj
        )
        
        print(f"   Probabilidades:")
        print(f"   - Aprovação: {approval_decision.probabilities['approved']*100:.1f}%")
        print(f"   - Rejeição: {approval_decision.probabilities['rejected']*100:.1f}%")
        print(f"   - Pendente: {approval_decision.probabilities['pending']*100:.1f}%")
        print(f"")
        
        if approval_decision.status == ApprovalStatus.APPROVED:
            print(f"✅ DECISÃO FINAL: APROVADO")
            print(f"   Confiança: {approval_decision.confidence*100:.1f}%")
        elif approval_decision.status == ApprovalStatus.REJECTED:
            print(f"❌ DECISÃO FINAL: REJEITADO")
            print(f"   Motivo: {approval_decision.rejection_reason.value if approval_decision.rejection_reason else 'N/A'}")
            print(f"   Confiança: {approval_decision.confidence*100:.1f}%")
        else:
            print(f"⏳ DECISÃO FINAL: PENDENTE (Análise Manual Necessária)")
            print(f"   Confiança: {approval_decision.confidence*100:.1f}%")
        
        print(f"\n{'='*70}\n")
        
        # Retorna resultado completo
        return CreditAnalysisResult(
            request_id=credit_request.request_id,
            customer_id=credit_request.customer_profile.customer_id,
            analysis_date=datetime.now(),
            persona_filter=persona_result,
            credit_limit=credit_limit_obj,
            risk_assessment=risk_assessment_obj,
            approval_status=approval_decision.status,
            rejection_reason=approval_decision.rejection_reason,
            approval_confidence=approval_decision.confidence,
            neural_network_probabilities=approval_decision.probabilities
        )
        
        # ===== ETAPA 3: AVALIAÇÃO DE RISCO (LÓGICA FUZZY) =====
        print("⚠️  ETAPA 3: Avaliação de Risco (Lógica Fuzzy)")
        print("-" * 60)
        
        risk_assessment = self.risk_evaluator.evaluate(credit_request.customer_profile)
        
        print(f"Score de Crédito: {credit_request.customer_profile.credit_score}")
        print(f"Comprometimento de Renda: {credit_request.customer_profile.debt_to_income_ratio() * 100:.1f}%")
        print(f"Atrasos: {credit_request.customer_profile.late_payments_count}")
        print(f"Tempo de Emprego: {credit_request.customer_profile.employment_time_months} meses")
        print(f"Distância: {credit_request.customer_profile.distance_from_branch_km:.1f} km")
        print(f"\nRisco Calculado: {risk_assessment.risk_level.value.upper()}")
        print(f"Score de Risco: {risk_assessment.risk_score:.3f} (0=sem risco, 1=risco máximo)")
        print(f"Descrição: {risk_assessment.get_risk_description()}")
        
        # Detalhamento dos fatores
        print(f"\nDetalhamento dos Fatores:")
        print(f"  • Score de Crédito: {risk_assessment.credit_score_factor:.3f}")
        print(f"  • Endividamento: {risk_assessment.debt_ratio_factor:.3f}")
        print(f"  • Atrasos: {risk_assessment.late_payments_factor:.3f}")
        print(f"  • Emprego: {risk_assessment.employment_factor:.3f}")
        print(f"  • Distância: {risk_assessment.distance_factor:.3f}")
        print(f"  • Restrições BACEN: {risk_assessment.bacen_restrictions_factor:.3f}")
        print(f"  • Restrições Bureau: {risk_assessment.bureau_restrictions_factor:.3f}")
        print()
        
        # ===== ETAPA 4: DECISÃO FINAL (REDE NEURAL) =====
        print("🤖 ETAPA 4: Decisão Final (Rede Neural Artificial)")
        print("-" * 60)
        
        approval_decision = self.approval_network.evaluate(
            credit_request,
            persona_result,
            credit_limit,
            risk_assessment
        )
        
        print(f"Análise da Rede Neural:")
        print(f"  • Status: {approval_decision.status.value.upper()}")
        print(f"  • Confiança: {approval_decision.confidence * 100:.1f}%")
        
        if approval_decision.rejection_reason:
            print(f"  • Motivo: {approval_decision.rejection_reason.value}")
        
        # Determina valores aprovados
        approved_amount = 0.0
        approved_installments = 0
        approved_rate = credit_limit.interest_rate
        monthly_payment = 0.0
        
        if approval_decision.status == ApprovalStatus.APPROVED:
            # Aprova o menor entre solicitado e limite
            approved_amount = min(
                credit_request.requested_amount,
                credit_limit.approved_amount
            )
            approved_installments = min(
                credit_request.requested_installments,
                credit_limit.max_installments
            )
            
            # Recalcula parcela para valor aprovado
            if approved_rate > 0:
                factor = (1 + approved_rate) ** approved_installments
                monthly_payment = approved_amount * (approved_rate * factor) / (factor - 1)
            else:
                monthly_payment = approved_amount / approved_installments
            
            print(f"\n✅ CRÉDITO APROVADO!")
            print(f"  • Valor Aprovado: R$ {approved_amount:,.2f}")
            print(f"  • Parcelas: {approved_installments}x de R$ {monthly_payment:,.2f}")
            print(f"  • Total a Pagar: R$ {monthly_payment * approved_installments:,.2f}")
        
        elif approval_decision.status == ApprovalStatus.PENDING:
            print(f"\n⏸️  ANÁLISE PENDENTE")
            print(f"  • Requer análise manual adicional")
        
        else:
            print(f"\n❌ CRÉDITO REPROVADO")
        
        print(f"\n{'='*60}\n")
        
        # Monta resultado final
        return CreditAnalysisResult(
            request_id=credit_request.request_id,
            customer_id=credit_request.customer_profile.customer_id,
            analysis_date=datetime.now(),
            persona_filter=persona_result,
            credit_limit=credit_limit,
            risk_assessment=risk_assessment,
            approval_status=approval_decision.status,
            rejection_reason=approval_decision.rejection_reason,
            neural_network_confidence=approval_decision.confidence,
            approved_amount=approved_amount,
            approved_installments=approved_installments,
            approved_interest_rate=approved_rate,
            monthly_payment=monthly_payment
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
            f"  Status: {'Reprovado' if result.persona_filter.should_reject else 'Aprovado'}",
        ]
        
        if result.persona_filter.should_reject:
            lines.append(f"  Motivo: {result.persona_filter.reason}")
        
        if result.credit_limit:
            lines.extend([
                "",
                "ETAPA 2 - Limite de Crédito (BFS):",
                f"  Limite Aprovado: R$ {result.credit_limit.approved_amount:,.2f}",
                f"  Parcela Máxima: R$ {result.credit_limit.max_installment_value:,.2f}",
                f"  Prazo Máximo: {result.credit_limit.max_installments}x",
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
