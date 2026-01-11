"""Shared dependencies and singleton instances for the application."""
from app.services.rag_service import RAGService
from app.services.compliance_checker import ComplianceChecker

# Shared service instances (singletons)
rag_service = RAGService()
compliance_checker = ComplianceChecker()
