"""
Demo Seed Data — populates the knowledge base with realistic staff-sourced content.

Simulates Attraction Tickets (attractiontickets.com), the UK's No.1 attraction
ticket provider, whose staff phone recordings have been transcribed, processed,
and loaded into the knowledge base.
Each entry references the source transcript it was extracted from.
"""

import asyncio
from datetime import datetime, UTC

from staff_echo.domain.entities.knowledge_entry import KnowledgeEntry, KnowledgeCategory
from staff_echo.domain.value_objects.pricing_info import PricingInfo, PricingSource
from staff_echo.domain.value_objects.tone_profile import ToneProfile
from staff_echo.infrastructure.repositories.in_memory_knowledge_repo import InMemoryKnowledgeRepository


DEFAULT_TONE_PROFILE = ToneProfile(
    greeting_style="Hi there! Welcome to Attraction Tickets.",
    formality_level="friendly",
    common_phrases=(
        "brilliant",
        "no worries at all",
        "sorted for you",
        "you're all set",
        "happy to help",
        "let me check that for you",
    ),
    analogies=(
        "Think of it like a fast pass — you skip the ticket queue entirely",
        "It's like booking a flight — the earlier you lock in, the better the price",
    ),
)


SEED_ENTRIES = [
    # ── Product Specs (from staff recordings) ──
    KnowledgeEntry(
        id="transcript-2024-11-emma-disney-world",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "Our Walt Disney World tickets give you access to all four theme parks — "
            "Magic Kingdom, EPCOT, Hollywood Studios, and Animal Kingdom. "
            "We offer single-day and multi-day options from 2 to 14 days. "
            "Multi-day tickets include the Park Hopper option so you can visit "
            "multiple parks in the same day. All tickets are gate-ready digital tickets "
            "so you can go straight to the entrance — no queuing at the ticket booth."
        ),
        source_transcript_id="call-2024-11-08-emma-wilson",
    ),
    KnowledgeEntry(
        id="transcript-2024-10-james-universal-orlando",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "Universal Orlando tickets cover Universal Studios Florida, "
            "Islands of Adventure, and the new Universal Epic Universe. "
            "We have 1-day to 5-day options, with Park-to-Park access available "
            "so you can ride the Hogwarts Express between parks. "
            "Our tickets include 14 days of flexibility from first use, "
            "so you don't need to visit on consecutive days."
        ),
        source_transcript_id="call-2024-10-22-james-taylor",
    ),
    KnowledgeEntry(
        id="transcript-2024-09-emma-disneyland-paris",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "Our Disneyland Paris tickets cover both Disneyland Park and "
            "Walt Disney Studios Park. We offer 1-day single park, 1-day dual park, "
            "and multi-day options up to 4 days. "
            "Dated tickets guarantee entry on your chosen day, which is important "
            "during peak season when the parks can reach capacity. "
            "We also sell hotel + ticket packages with on-site Disney hotels."
        ),
        source_transcript_id="call-2024-09-15-emma-wilson",
    ),
    KnowledgeEntry(
        id="transcript-2024-12-james-london",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "Our London attractions range includes The London Eye, Madame Tussauds, "
            "SEA LIFE London Aquarium, The London Dungeon, and Shrek's Adventure. "
            "We sell individual tickets and combo passes — the Merlin's Magical London "
            "pass bundles 5 attractions together at a big saving versus buying separately. "
            "All tickets are mobile-friendly so customers just show their phone at the gate."
        ),
        source_transcript_id="call-2024-12-03-james-taylor",
    ),
    KnowledgeEntry(
        id="transcript-2025-01-emma-dubai",
        category=KnowledgeCategory.PRODUCT_SPEC,
        content=(
            "For Dubai, we sell tickets for IMG Worlds of Adventure, Atlantis Aquaventure, "
            "Burj Khalifa At The Top, Dubai Frame, and the Desert Safari experiences. "
            "IMG Worlds is the world's largest indoor theme park — great for families "
            "wanting to escape the heat. Aquaventure is brilliant for thrill-seekers "
            "with over 100 slides and attractions. All our Dubai tickets include "
            "skip-the-line entry where available."
        ),
        source_transcript_id="call-2025-01-10-emma-wilson",
    ),

    # ── Pricing (verified from BigQuery) ──
    KnowledgeEntry(
        id="pricing-disney-world-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Walt Disney World ticket pricing: 1-day base ticket from £109 per adult, "
            "£104 per child (ages 3-9). Multi-day tickets offer much better value — "
            "a 7-day Ultimate ticket is from £399 per adult, which works out to about "
            "£57 per day. 14-day Ultimate tickets start from £459 per adult. "
            "Park Hopper upgrade adds approximately £70 to any base ticket."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=109.00,
            currency="GBP",
            product_id="disney-world-1day",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),
    KnowledgeEntry(
        id="pricing-universal-orlando-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Universal Orlando ticket pricing: 1-day single park from £119 per adult, "
            "£114 per child. 2-day Park-to-Park tickets from £229 per adult — "
            "this is the most popular option as it lets you ride the Hogwarts Express. "
            "3-park Explorer tickets covering Epic Universe start from £279 per adult. "
            "All multi-day tickets include 14 consecutive days of flexibility."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=119.00,
            currency="GBP",
            product_id="universal-orlando-1day",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),
    KnowledgeEntry(
        id="pricing-disneyland-paris-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Disneyland Paris ticket pricing: 1-day 1-park dated ticket from £52 per adult, "
            "£47 per child (ages 3-11). 1-day dual-park access from £77 per adult. "
            "Multi-day tickets (2-4 days) start from £119 per adult for a 2-day hopper. "
            "Peak season dates (school holidays, Christmas) carry a supplement of £10-£20."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=52.00,
            currency="GBP",
            product_id="disneyland-paris-1day",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),
    KnowledgeEntry(
        id="pricing-london-combo-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "London attractions pricing: London Eye standard from £32 per adult, "
            "£27 per child. Madame Tussauds from £35 per adult. "
            "Merlin's Magical London pass (5 attractions) from £65 per adult — "
            "that's a saving of over 50% versus buying individually. "
            "SEA LIFE London Aquarium from £28 per adult. "
            "The London Dungeon from £27 per adult."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=65.00,
            currency="GBP",
            product_id="london-merlin-combo",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),
    KnowledgeEntry(
        id="pricing-dubai-bq-verified",
        category=KnowledgeCategory.PRICING,
        content=(
            "Dubai attractions pricing: Burj Khalifa At The Top from £33 per adult, "
            "£26 per child (ages 4-12). Atlantis Aquaventure from £62 per adult. "
            "IMG Worlds of Adventure from £58 per adult. Dubai Frame from £12 per adult. "
            "Desert Safari with BBQ dinner from £39 per person. "
            "We often run bundle deals for families visiting multiple Dubai attractions."
        ),
        source_transcript_id="bigquery-pricing-sync-2025-02",
        pricing_info=PricingInfo(
            amount=33.00,
            currency="GBP",
            product_id="burj-khalifa-at-the-top",
            source=PricingSource.BIGQUERY_VERIFIED,
            verified_at=datetime(2025, 2, 1, tzinfo=UTC),
        ),
    ),

    # ── FAQs (from staff phone conversations) ──
    KnowledgeEntry(
        id="transcript-2024-11-james-delivery",
        category=KnowledgeCategory.FAQ,
        content=(
            "All our tickets are delivered digitally — you'll get a confirmation email "
            "with your e-tickets within a few minutes of booking. For some products "
            "like Walt Disney World, you get a booking reference that you link to "
            "the My Disney Experience app. For most other attractions, you just show "
            "the QR code on your phone at the gate. No printing needed."
        ),
        source_transcript_id="call-2024-11-20-james-taylor",
    ),
    KnowledgeEntry(
        id="transcript-2024-10-emma-cancellation",
        category=KnowledgeCategory.FAQ,
        content=(
            "We offer free cancellation on most bookings up to 48 hours before "
            "your visit date. You'll get a full refund back to your original payment method. "
            "For dated Disney and Universal tickets, we offer a date change option "
            "up to 24 hours before. If you booked a non-refundable deal, "
            "that's clearly marked at checkout — those are final sale."
        ),
        source_transcript_id="call-2024-10-05-emma-wilson",
    ),
    KnowledgeEntry(
        id="transcript-2025-01-james-payment",
        category=KnowledgeCategory.FAQ,
        content=(
            "We accept all major credit and debit cards — Visa, Mastercard, Amex. "
            "We also offer Buy Now Pay Later through Klarna for orders over £50 — "
            "you can split it into 3 interest-free payments. There's also a low deposit "
            "option on qualifying orders: put down £50 per person to secure your booking "
            "and pay the rest later. All payments are processed securely through our site."
        ),
        source_transcript_id="call-2025-01-18-james-taylor",
    ),
    KnowledgeEntry(
        id="transcript-2024-12-emma-groups",
        category=KnowledgeCategory.FAQ,
        content=(
            "For groups of 10 or more, we offer special group rates on most attractions. "
            "The discount is typically 10-15% off the standard advance price. "
            "Groups get a dedicated booking coordinator and flexible payment terms. "
            "We handle school trips, corporate events, and large family bookings. "
            "Just fill in the group enquiry form on our website or call our groups team directly."
        ),
        source_transcript_id="call-2024-12-12-emma-wilson",
    ),

    # ── General Info (from staff conversations) ──
    KnowledgeEntry(
        id="transcript-2024-09-james-about",
        category=KnowledgeCategory.GENERAL,
        content=(
            "Attraction Tickets is the UK's number 1 attraction ticket provider. "
            "We've been going since 2002 and have sold over 10 million tickets worldwide. "
            "We're official partners with Walt Disney World, Universal Orlando, "
            "Disneyland Paris, Merlin Entertainments, and loads more. "
            "We're based in Hove, East Sussex, and our team of over 150 travel experts "
            "are all real people who've visited the parks and attractions we sell."
        ),
        source_transcript_id="call-2024-09-28-james-taylor",
    ),
    KnowledgeEntry(
        id="transcript-2025-02-emma-contact",
        category=KnowledgeCategory.GENERAL,
        content=(
            "Our customer service team is available Monday to Friday 9 AM to 5:30 PM "
            "and Saturday 10 AM to 4 PM. We're closed on Sundays and bank holidays. "
            "You can reach us by phone, email, or live chat on our website. "
            "We typically respond to emails within 4 hours during business hours. "
            "For urgent travel queries on the day, phone is always quickest."
        ),
        source_transcript_id="call-2025-02-04-emma-wilson",
    ),
]


async def seed_knowledge_base(repo: InMemoryKnowledgeRepository) -> None:
    for entry in SEED_ENTRIES:
        await repo.save(entry)
