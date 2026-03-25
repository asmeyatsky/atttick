"""
Staff-Echo Application Layer

Architectural Intent:
- Use cases orchestrate domain objects via ports
- One use case per class, injectable with ports
- DAG orchestration for multi-step workflows
- Depends only on the domain layer
"""
