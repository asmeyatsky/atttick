"""
Demo Seed Data — populates the knowledge base with realistic staff-sourced content.

Simulates a home renovation company (HomeRevive) whose staff phone recordings
have been transcribed, processed, and loaded into the knowledge base.
Each entry references the source transcript it was extracted from.
"""

import asyncio
from datetime import datetime, UTC

from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.pricing_info import PricingInfo, PricingSource
from staff_echo.domain.value_objects.tone_profile import ToneProfile
from staff_echo.infrastructure.repositories.in_memory_knowledge_repo import InMemoryKnowledgeRepository


DEFAULT_TONE_PROFILE = ToneProfile(
    greeting_style="Hey there! Thanks for reaching out.",
    formality_level="casual",
    common_phrases=(
        "absolutely",
        "happy to help",
        "great question",
        "let me walk you through that",
        "no worries at all",
        "we've got you covered",
    ),
    analogies=(
        "Think of it like giving your home a fresh start",
        "It's kind of like choosing a new outfit for your house",
    ),
)


SEED_ENTRIES = [
    # ── Product Specs (from staff recordings) ──
    KnowledgeEntry(
        id="transcript-2024-11-sarah-kitchen",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "Our Kitchen Renovation package is our most popular service. "
            "It includes full cabinet replacement or refacing, countertop installation "
            "(granite, quartz, or marble), backsplash tiling, new fixtures and hardware, "
            "updated lighting, and optional appliance coordination. "
            "We handle everything from design to final walkthrough. "
            "Most kitchen projects take 3 to 5 weeks depending on scope."
        ),
        source_transcript_id="call-2024-11-08-sarah-johnson",
    ),
    KnowledgeEntry(
        id="transcript-2024-10-mike-bathroom",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "Our Bathroom Remodel service covers everything — "
            "new vanity and sink, shower or tub replacement, tile work for floors and walls, "
            "updated plumbing fixtures, new lighting, and ventilation upgrades. "
            "We also do accessibility modifications like walk-in showers and grab bars. "
            "A standard bathroom remodel takes about 2 to 3 weeks."
        ),
        source_transcript_id="call-2024-10-22-mike-chen",
    ),
    KnowledgeEntry(
        id="transcript-2024-09-sarah-painting",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "Our Interior Painting service includes wall prep, priming, two coats of premium paint, "
            "trim and baseboard painting, and full cleanup. "
            "We use Sherwin-Williams and Benjamin Moore paints exclusively. "
            "We also do accent walls, cabinet painting, and ceiling work. "
            "A typical room takes 1 to 2 days. Full home painting usually runs 5 to 8 days."
        ),
        source_transcript_id="call-2024-09-15-sarah-johnson",
    ),
    KnowledgeEntry(
        id="transcript-2024-12-mike-deck",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "Our Deck & Outdoor Living builds include custom composite or pressure-treated wood decks, "
            "pergolas, built-in seating, and outdoor lighting. "
            "We handle permits and HOA approvals. All decks come with a structural engineering review. "
            "Build time is typically 2 to 4 weeks depending on size and complexity."
        ),
        source_transcript_id="call-2024-12-03-mike-chen",
    ),
    KnowledgeEntry(
        id="transcript-2025-01-sarah-flooring",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "We install hardwood, engineered wood, luxury vinyl plank, and tile flooring. "
            "The service includes removal of old flooring, subfloor prep, installation, "
            "transitions, and quarter-round trim. We carry brands like Shaw, Mohawk, and Armstrong. "
            "Most single-room installs are done in a day. Full home flooring takes 3 to 5 days."
        ),
        source_transcript_id="call-2025-01-10-sarah-johnson",
    ),

    # ── Pricing (verified from BigQuery) ──
    KnowledgeEntry(
        id="pricing-kitchen-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Kitchen Renovation pricing: packages start at $15,000 for a basic refresh "
            "(cabinet refacing, new countertops, hardware update). "
            "Mid-range full remodels run $25,000 to $35,000. "
            "Premium kitchen renovations with custom cabinetry and high-end appliance coordination "
            "range from $35,000 to $45,000."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=15000.00,
            currency="USD",
            product_id="kitchen-renovation",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),
    KnowledgeEntry(
        id="pricing-bathroom-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Bathroom Remodel pricing: standard remodels start at $8,500. "
            "Mid-range projects with custom tile and fixtures run $12,000 to $18,000. "
            "Luxury master bath renovations range from $18,000 to $25,000. "
            "Accessibility modifications (walk-in shower conversion) start at $5,500."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=8500.00,
            currency="USD",
            product_id="bathroom-remodel",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),
    KnowledgeEntry(
        id="pricing-painting-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Interior Painting pricing: single room starts at $800. "
            "Most rooms average $800 to $1,500 depending on size and prep work. "
            "Full home interior painting (3-bed) runs $2,800 to $5,500. "
            "Larger homes (4-5 bed) run $5,500 to $9,000. "
            "Cabinet painting starts at $2,500 for a standard kitchen."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=800.00,
            currency="USD",
            product_id="interior-painting",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),
    KnowledgeEntry(
        id="pricing-deck-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Deck & Outdoor Living pricing: a standard 12x16 composite deck starts at $6,000. "
            "Larger multi-level decks with built-in features run $12,000 to $20,000. "
            "Pergola additions start at $3,500. "
            "Outdoor lighting packages start at $1,200."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=6000.00,
            currency="USD",
            product_id="deck-outdoor",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),
    KnowledgeEntry(
        id="pricing-flooring-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Flooring Installation pricing: luxury vinyl plank starts at $4.50 per square foot installed. "
            "Hardwood flooring runs $8 to $14 per square foot installed. "
            "Tile flooring starts at $6 per square foot installed. "
            "A typical 300 sqft room runs $1,350 to $4,200 depending on material."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=4.50,
            currency="USD",
            product_id="flooring-installation",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),

    # ── FAQs (from staff phone conversations) ──
    KnowledgeEntry(
        id="transcript-2024-11-mike-consult",
        category=KnowledgeCategory.FAQ,
        content=(
            "We offer free in-home consultations for all services. "
            "A project consultant visits your home, takes measurements, discusses your vision, "
            "and provides a detailed quote within 48 hours. No pressure, no obligation. "
            "Consultations typically take 30 to 45 minutes."
        ),
        source_transcript_id="call-2024-11-20-mike-chen",
    ),
    KnowledgeEntry(
        id="transcript-2024-10-sarah-payment",
        category=KnowledgeCategory.FAQ,
        content=(
            "We offer flexible payment options. For projects over $5,000, we have 12-month "
            "interest-free financing through GreenSky. We also accept credit cards, checks, "
            "and bank transfers. Standard terms are 30% deposit to reserve your spot, "
            "40% at project midpoint, and 30% on completion and final walkthrough."
        ),
        source_transcript_id="call-2024-10-05-sarah-johnson",
    ),
    KnowledgeEntry(
        id="transcript-2025-01-mike-warranty",
        category=KnowledgeCategory.FAQ,
        content=(
            "All our work comes with a 5-year workmanship warranty. "
            "That covers any installation defects or issues with our labor. "
            "Materials carry their own manufacturer warranties on top of that — "
            "most are 10 to 25 years. If something doesn't look right or isn't holding up, "
            "just call us and we'll make it right."
        ),
        source_transcript_id="call-2025-01-18-mike-chen",
    ),
    KnowledgeEntry(
        id="transcript-2024-12-sarah-timeline",
        category=KnowledgeCategory.FAQ,
        content=(
            "Project timelines depend on scope, but here's a rough guide: "
            "painting takes 1 to 8 days, bathroom remodels 2 to 3 weeks, "
            "kitchen renovations 3 to 5 weeks, and deck builds 2 to 4 weeks. "
            "We always give you a specific timeline before we start, "
            "and our project managers send daily progress updates."
        ),
        source_transcript_id="call-2024-12-12-sarah-johnson",
    ),

    # ── General Info (from staff conversations) ──
    KnowledgeEntry(
        id="transcript-2024-09-mike-about",
        category=KnowledgeCategory.GENERAL,
        content=(
            "HomeRevive has been serving the Greater Metro area for 12 years. "
            "We're fully licensed, bonded, and insured. Our team includes 35 full-time "
            "craftsmen and 4 project managers. We've completed over 2,500 projects "
            "with a 4.9-star rating across Google and Yelp."
        ),
        source_transcript_id="call-2024-09-28-mike-chen",
    ),
    KnowledgeEntry(
        id="transcript-2025-02-sarah-hours",
        category=KnowledgeCategory.GENERAL,
        content=(
            "Our office hours are Monday through Friday, 8 AM to 6 PM, "
            "and Saturday 9 AM to 2 PM. We're closed on Sundays. "
            "On-site work typically happens Monday through Saturday, 8 AM to 5 PM. "
            "For urgent issues, we have an after-hours line."
        ),
        source_transcript_id="call-2025-02-04-sarah-johnson",
    ),
]


async def seed_knowledge_base(repo: InMemoryKnowledgeRepository) -> None:
    for entry in SEED_ENTRIES:
        await repo.save(entry)
