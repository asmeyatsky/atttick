"""
Staff-Echo Domain Layer

Architectural Intent:
- Pure business logic with ZERO infrastructure dependencies
- All models are immutable (frozen dataclasses)
- Ports define contracts implemented by infrastructure adapters
- Domain services encapsulate cross-entity business rules
"""
