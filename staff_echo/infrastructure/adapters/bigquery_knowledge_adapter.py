from __future__ import annotations
"""
BigQuery Knowledge Adapter — implements KnowledgeRepositoryPort.

Architectural Intent:
- Queries BigQuery for product specs, pricing, and FAQ knowledge
- Maps BigQuery rows to domain KnowledgeEntry entities
- Graceful degradation if SDK not installed
"""

from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.pricing_info import PricingInfo, PricingSource

try:
    from google.cloud import bigquery

    _HAS_BQ = True
except ImportError:
    _HAS_BQ = False


class BigQueryKnowledgeAdapter:

    def __init__(self, project_id: str = "", dataset: str = "staff_echo"):
        self._project_id = project_id
        self._dataset = dataset
        self._client = None
        if _HAS_BQ and project_id:
            self._client = bigquery.Client(project=project_id)

    async def save(self, entry: KnowledgeEntry) -> None:
        if not self._client:
            return
        table = f"{self._project_id}.{self._dataset}.knowledge_entries"
        row = {
            "id": entry.id,
            "category": entry.category.value,
            "content": entry.content,
            "source_transcript_id": entry.source_transcript_id,
            "relevance_score": entry.relevance_score,
            "created_at": entry.created_at.isoformat(),
        }
        if entry.pricing_info:
            row["pricing_amount"] = entry.pricing_info.amount
            row["pricing_currency"] = entry.pricing_info.currency
            row["pricing_product_id"] = entry.pricing_info.product_id
            row["pricing_source"] = entry.pricing_info.source.value
        self._client.insert_rows_json(table, [row])

    async def search(
        self,
        query: str,
        category: KnowledgeCategory | None = None,
        limit: int = 10,
    ) -> list[KnowledgeEntry]:
        if not self._client:
            return []
        table = f"`{self._project_id}.{self._dataset}.knowledge_entries`"
        where = "WHERE SEARCH(content, @query)"
        if category:
            where += " AND category = @category"
        sql = f"SELECT * FROM {table} {where} LIMIT @limit"

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("query", "STRING", query),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
            + (
                [bigquery.ScalarQueryParameter("category", "STRING", category.value)]
                if category
                else []
            )
        )
        results = self._client.query(sql, job_config=job_config).result()
        return [self._row_to_entry(row) for row in results]

    async def get_pricing(self, product_id: str) -> list[PricingInfo]:
        if not self._client:
            return []
        table = f"`{self._project_id}.{self._dataset}.knowledge_entries`"
        sql = f"""
            SELECT pricing_amount, pricing_currency, pricing_product_id, pricing_source
            FROM {table}
            WHERE category = 'pricing' AND LOWER(pricing_product_id) LIKE @product_pattern
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(
                    "product_pattern", "STRING", f"%{product_id.lower()}%"
                ),
            ]
        )
        results = self._client.query(sql, job_config=job_config).result()
        return [
            PricingInfo(
                amount=row["pricing_amount"],
                currency=row["pricing_currency"],
                product_id=row["pricing_product_id"],
                source=PricingSource(row["pricing_source"]),
            )
            for row in results
            if row.get("pricing_amount") is not None
        ]

    def _row_to_entry(self, row) -> KnowledgeEntry:
        pricing = None
        if row.get("pricing_amount") is not None:
            pricing = PricingInfo(
                amount=row["pricing_amount"],
                currency=row.get("pricing_currency", "USD"),
                product_id=row.get("pricing_product_id", ""),
                source=PricingSource(row.get("pricing_source", "unverified")),
            )
        return KnowledgeEntry(
            id=row["id"],
            category=KnowledgeCategory(row["category"]),
            content=row["content"],
            source_transcript_id=row.get("source_transcript_id"),
            pricing_info=pricing,
            relevance_score=row.get("relevance_score", 0.0),
        )
