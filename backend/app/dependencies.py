"""Shared dependencies and singleton instances for the application."""
from app.services.rag_service import RAGService
from app.services.compliance_checker import ComplianceChecker
from app.services.prompt_store import PromptStore
from app.services.evaluation_service import EvaluationService
from app.services.prompt_improver import PromptImproverService

rag_service = RAGService()
compliance_checker = ComplianceChecker()
prompt_store = PromptStore()
evaluation_service = EvaluationService(
    compliance_checker=compliance_checker,
)
prompt_improver = PromptImproverService(store=prompt_store, evaluation_service=evaluation_service)
evaluation_service.prompt_improver = prompt_improver
