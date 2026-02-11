#!/usr/bin/env python3
"""
Main Article Processing Script
Processes articles from main_corpus through the event extraction pipeline

Features:
- Sequential processing (simple, easy to debug)
- Persistent (saves progress after each article)
- Resumable (can stop and restart anytime)
- Progress tracking and statistics
"""

import argparse
import os
import re
import signal
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from database_manager import DatabaseManager
from response_openai import ExtractInfoResponses
from noai_functions import DataFrameEnhancer
from location_agent import LocationAgent


class ArticleProcessor:
    """Main processor for extracting events from articles"""

    def __init__(self):
        """Initialize the processor with database and AI clients"""
        print("=" * 70)
        print("Jordan Events - Article Processing Pipeline")
        print("=" * 70)

        # Initialize database manager
        print("\nInitializing database connection...")
        self.db = DatabaseManager()

        # Initialize event extraction system with database
        print("Initializing AI extraction system...")
        self.processor = ExtractInfoResponses(db_manager=self.db)

        # Initialize location agent for geocoding (optional)
        print("Initializing location agent...")
        try:
            self.location_agent = LocationAgent()
            print("✓ Location agent initialized (GPS coordinates enabled)")
        except ValueError as e:
            # API key not configured - continue without geocoding
            self.location_agent = None
            print("⚠ Location agent disabled (set GOOGLE_MAPS_API_KEY to enable GPS coordinates)")

        # Processing statistics
        self.stats = {
            'start_time': None,
            'processed': 0,
            'succeeded': 0,
            'failed': 0,
            'consecutive_failures': 0,
            'events_created': 0,
            'duplicates_expanded': 0,
            'duplicate_clusters': 0
        }

        # Auto-stop threshold for consecutive failures
        self.max_consecutive_failures = 5

        # Filter parameters (set during run())
        self.filter_sources = None
        self.filter_year = None
        self.filter_month = None
        self.filter_start_date = None
        self.filter_end_date = None
        self.filter_article_ids = None

        # Graceful shutdown handler
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle graceful shutdown on Ctrl+C or SIGTERM"""
        print("\n\n⚠️  Shutdown signal received. Finishing current article...")
        print("   (The pipeline will resume from this point next time)")
        self.running = False

    def initialize_queue(self, sources=None, year=None, month=None,
                        start_date=None, end_date=None, article_ids=None):
        """
        Initialize processing queue from main_corpus
        Only adds new articles that haven't been processed yet

        Args:
            sources: Optional list of news sources to filter by
            year: Optional year to filter by
            month: Optional month to filter by
            start_date: Optional start date for range filter
            end_date: Optional end date for range filter
            article_ids: Optional list of specific article IDs to process
        """
        print("\n" + "-" * 70)
        print("INITIALIZING PROCESSING QUEUE")
        print("-" * 70)

        # Show active filters
        if sources or year or month or start_date or end_date or article_ids:
            print("\nActive filters:")
            if article_ids:
                print(f"  Articles: {', '.join(article_ids)}")
            if sources:
                print(f"  Sources: {', '.join(sources)}")
            if year and month:
                print(f"  Date: {year}-{str(month).zfill(2)}")
            elif year:
                print(f"  Year: {year}")
            elif start_date and end_date:
                print(f"  Date range: {start_date} to {end_date}")
            elif start_date:
                print(f"  From: {start_date}")
            elif end_date:
                print(f"  Until: {end_date}")

        count = self.db.initialize_processing_state(
            sources=sources,
            year=year,
            month=month,
            start_date=start_date,
            end_date=end_date,
            article_ids=article_ids
        )
        print(f"\n✓ Added {count:,} new articles to processing queue")

        # Show overall statistics
        stats = self.db.get_processing_stats()
        if stats:
            print(f"\nQueue Status:")
            print(f"  Total articles: {stats.get('total_articles', 0):,}")
            print(f"  Pending:        {stats.get('pending', 0):,}")
            print(f"  Completed:      {stats.get('completed', 0):,}")
            print(f"  Failed:         {stats.get('failed', 0):,}")
            if stats.get('total_articles', 0) > 0:
                print(f"  Progress:       {stats.get('percent_complete', 0):.1f}%")

        return stats.get('pending', 0)

    def process_next_article(self):
        """
        Process the next pending article using 3-table architecture
        Single-stage pipeline: extract → duplicate check → enrich → create event

        Returns:
            True if article was processed, False if no articles pending
        """
        article = self.db.get_next_article(
            year=self.filter_year,
            month=self.filter_month,
            sources=self.filter_sources,
            start_date=self.filter_start_date,
            end_date=self.filter_end_date,
            article_ids=self.filter_article_ids
        )

        if not article:
            return False

        article_id = article['article_id']
        text = article['source_text']
        date = article.get('source_date')

        date_str = date.strftime('%Y-%m-%d') if date else 'unknown'

        print(f"\n[{self.stats['processed'] + 1}] Processing: {article_id} (date: {date_str})")
        print(f"    Text length: {len(text):,} characters")

        # All enrichment assistants (13 assistants for ~95 fields)
        ALL_ENRICHMENT_ASSISTANTS = [
            "date_extractor",
            "location_extractor",
            "tactic_extractor",
            "event_classifier",
            "event_type",
            "commemorative_extractor",
            "multi_sited_extractor",
            "participants_extractor",
            "mediators_extractor",
            "organizers_extractor",
            "target_extractor",
            "demand_extractor",
            "violence_extractor"
        ]

        try:
            # Begin article-level transaction (all-or-nothing processing)
            with self.db.transaction():
                self.db.mark_article_started(article_id)

                # Extract events from article
                events = self.processor.extract_events(text)

                if not events:
                    print(f"  No events extracted from article {article_id}")
                    self.db.update_article_status(article_id, 'completed', events_extracted=0)
                    self.stats['processed'] += 1
                    self.stats['succeeded'] += 1
                    return True

                print(f"  Extracted {len(events)} events")

                # Process each event directly (no intermediate tables)
                for event_num, event_text in enumerate(events, 1):
                    print(f"  Processing event {event_num}/{len(events)}...")

                    # Step 1: Enrich with ALL fields at once
                    print(f"    Enriching with {len(ALL_ENRICHMENT_ASSISTANTS)} assistants...")
                    event_data = {
                        'event': event_text,
                        'date': date_str
                    }
                    enriched = self.processor.add_columns_to_df(event_data, ALL_ENRICHMENT_ASSISTANTS)

                    # Step 1.5: Post-process with non-AI functions (date normalization & calculations)
                    print(f"    Post-processing: normalizing dates and calculations...")

                    # Normalize date formats (DD-MM-YYYY -> YYYY-MM-DD)
                    enriched = DataFrameEnhancer.normalize_dates_in_dict(enriched)

                    # Date calculations
                    df_temp = pd.DataFrame([enriched])
                    df_temp = DataFrameEnhancer.fill_missing_start_dates(df_temp)
                    df_temp = DataFrameEnhancer.add_num_of_days(df_temp)
                    enriched = df_temp.iloc[0].to_dict()

                    # Step 1.75: Geocode locations to add GPS coordinates (if location_agent available)
                    if self.location_agent:
                        enriched = self._geocode_event_locations(enriched)

                    # Step 2: Check for duplicates (after enrichment to get dates/location)
                    print(f"    Checking for duplicates...")
                    is_duplicate = False
                    duplicate_ids = []

                    if enriched.get('start_date'):
                        # Get candidate duplicates using date-based SQL filtering
                        # Includes events with overlapping dates OR matching planned_event_date
                        candidates = self.db.get_events_by_date_range(
                            start_date=enriched['start_date'],
                            end_date=enriched.get('end_date', enriched['start_date']),
                            planned_date=enriched.get('planned_event_date')
                        )

                        if candidates:
                            # Use AI to check if any candidates are true duplicates
                            event_check = {
                                'event': event_text,
                                'start_date': enriched.get('start_date'),
                                'end_date': enriched.get('end_date', enriched.get('start_date')),
                                'Governorate': enriched.get('Governorate'),
                                'Town': enriched.get('Town')
                            }
                            dup_result = self.processor.duplicate_check_db(event_check, candidates)
                            is_duplicate = dup_result.get('is_duplicate', False)
                            duplicate_ids = dup_result.get('duplicate_events_ids', [])

                            if is_duplicate:
                                print(f"    Duplicate detected: {duplicate_ids}")

                    # Step 3: Build complete event data dict with all ~95 fields
                    # Convert any pandas Timestamps to strings for JSON serialization
                    enriched_clean = {}
                    for key, value in enriched.items():
                        if pd.notna(value) and hasattr(value, 'isoformat'):
                            # Convert Timestamp/datetime to ISO string
                            enriched_clean[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                        else:
                            enriched_clean[key] = value

                    complete_event_data = {
                        'event': event_text,
                        'event_number': event_num,
                        'is_duplicate': is_duplicate,
                        'duplicate_events_ids': duplicate_ids,

                        # Copy all enriched fields (cleaned)
                        **enriched_clean
                    }

                    # Step 4: Create event directly in events table
                    event_id = self.db.create_event(article_id, complete_event_data)
                    print(f"    Created event: {event_id}" + (" (duplicate)" if is_duplicate else ""))
                    self.stats['events_created'] += 1

                # Mark article as completed with event count (inside transaction)
                self.db.update_article_status(article_id, 'completed', events_extracted=len(events))

            # Transaction committed successfully
            self.stats['processed'] += 1
            self.stats['succeeded'] += 1
            self.stats['consecutive_failures'] = 0  # Reset on success
            return True

        except Exception as e:
            # Transaction rolled back automatically
            error_msg = str(e)
            print(f"  ✗ Error processing article {article_id}: {error_msg}")
            print(f"    All changes for this article have been rolled back")

            # Update failure status (outside transaction)
            try:
                self.db.update_article_status(article_id, 'failed', error_msg)
            except Exception as status_error:
                print(f"    Warning: Could not update article status: {status_error}")

            self.stats['processed'] += 1
            self.stats['failed'] += 1
            self.stats['consecutive_failures'] += 1  # Track consecutive failures
            return False

    def _geocode_event_locations(self, enriched: dict) -> dict:
        """
        Geocode event locations to add GPS coordinates using Google Maps API

        Args:
            enriched: Dictionary with enriched event data including location fields

        Returns:
            Dictionary with added coordinate fields (Latitude, Longitude, location_type)
        """
        print(f"    Geocoding locations...")

        # Helper function to build location query
        def build_location_query(prefix=""):
            """Build location query from available fields"""
            parts = []

            # Field priority: Name_of_location, Governorate, District, Town, Neighborhood
            name_field = f"{prefix}Name_of_location" if prefix else "Name_of_location"
            gov_field = f"{prefix}Governorate" if prefix else "Governorate"
            dist_field = f"{prefix}District" if prefix else "District"
            town_field = f"{prefix}Town" if prefix else "Town"
            neigh_field = f"{prefix}Neighborhood" if prefix else "Neighborhood"

            # If we have specific location name, use it with highest admin level
            if enriched.get(name_field):
                parts.append(str(enriched[name_field]).strip())
                # Add one admin level for context
                for field in [gov_field, dist_field, town_field]:
                    if enriched.get(field):
                        parts.append(str(enriched[field]).strip())
                        break
            else:
                # No specific location, combine admin levels
                for field in [gov_field, dist_field, town_field, neigh_field]:
                    if enriched.get(field):
                        parts.append(str(enriched[field]).strip())

            return ", ".join(parts) if parts else None

        # Helper function to fill missing admin levels from Google Maps response
        def fill_missing_admin_levels(enriched: dict, components: dict, prefix: str = "") -> dict:
            """Fill missing administrative levels from Google Maps API response"""
            # Map Google Maps components to our field names
            field_mapping = {
                'governorate': f"{prefix}Governorate" if prefix else "Governorate",
                'district': f"{prefix}District" if prefix else "District",
                'town': f"{prefix}Town" if prefix else "Town",
                'neighborhood': f"{prefix}Neighborhood" if prefix else "Neighborhood",
            }

            filled_fields = []
            for api_key, field_name in field_mapping.items():
                # Only fill if the field is missing/empty and API has a value
                current_value = enriched.get(field_name)
                is_empty = not current_value or (isinstance(current_value, str) and not current_value.strip())

                if is_empty and components.get(api_key):
                    enriched[field_name] = components[api_key]
                    filled_fields.append(field_name)

            if filled_fields:
                print(f"      ✓ Filled missing admin levels: {', '.join(filled_fields)}")

            return enriched

        # Process start location
        start_query = build_location_query()
        if start_query:
            try:
                result = self.location_agent.geocode_location(start_query, country_code="JO")
                if result.get('latitude') and result.get('longitude'):
                    enriched['Latitude'] = result['latitude']
                    enriched['Longitude'] = result['longitude']
                    enriched['location_type'] = result.get('location_type')
                    enriched['geometric_center'] = 'true' if result.get('location_type') in ['GEOMETRIC_CENTER', 'APPROXIMATE'] else 'false'
                    print(f"      ✓ Start location geocoded: {result['latitude']:.4f}, {result['longitude']:.4f}")

                    # Fill missing administrative levels from Google Maps response
                    if result.get('components'):
                        enriched = fill_missing_admin_levels(enriched, result['components'], prefix="")
                else:
                    print(f"      ⚠ Could not geocode start location: {start_query}")
            except Exception as e:
                print(f"      ⚠ Error geocoding start location: {e}")

        # Process end location (for marches/multi-site events)
        end_query = build_location_query(prefix="end_")
        if end_query:
            try:
                result = self.location_agent.geocode_location(end_query, country_code="JO")
                if result.get('latitude') and result.get('longitude'):
                    enriched['end_Latitude'] = result['latitude']
                    enriched['end_Longitude'] = result['longitude']
                    enriched['end_location_type'] = result.get('location_type')
                    enriched['end_geometric_center'] = 'true' if result.get('location_type') in ['GEOMETRIC_CENTER', 'APPROXIMATE'] else 'false'
                    print(f"      ✓ End location geocoded: {result['latitude']:.4f}, {result['longitude']:.4f}")

                    # Fill missing administrative levels from Google Maps response
                    if result.get('components'):
                        enriched = fill_missing_admin_levels(enriched, result['components'], prefix="end_")
                else:
                    print(f"      ⚠ Could not geocode end location: {end_query}")
            except Exception as e:
                print(f"      ⚠ Error geocoding end location: {e}")

        return enriched

    def run(self, batch_size: int = None, sources=None, year=None, month=None,
            start_date=None, end_date=None, article_ids=None):
        """
        Run the processing pipeline

        Args:
            batch_size: Number of articles to process (None = process all)
            sources: Optional list of news sources to filter by
            year: Optional year to filter by
            month: Optional month to filter by
            start_date: Optional start date for range filter
            end_date: Optional end date for range filter
            article_ids: Optional list of specific article IDs to process
        """
        self.stats['start_time'] = time.time()

        # Store filter parameters for use in process_next_article()
        self.filter_sources = sources
        self.filter_year = year
        self.filter_month = month
        self.filter_start_date = start_date
        self.filter_end_date = end_date
        self.filter_article_ids = article_ids

        # Initialize processing queue
        pending_count = self.initialize_queue(
            sources=sources,
            year=year,
            month=month,
            start_date=start_date,
            end_date=end_date,
            article_ids=article_ids
        )

        if pending_count == 0:
            print("\n✓ No pending articles to process!")
            return

        # Determine how many to process
        to_process = batch_size if batch_size else pending_count
        print(f"\n{'=' * 70}")
        print(f"PROCESSING {to_process:,} ARTICLES")
        print(f"{'=' * 70}")

        # Process articles
        while self.running:
            # Process next article
            has_more = self.process_next_article()

            if not has_more:
                print("\n✓ No more articles to process!")
                break

            # Check for consecutive failures (auto-stop safety mechanism)
            if self.stats['consecutive_failures'] >= self.max_consecutive_failures:
                print(f"\n⚠️  AUTO-STOP: {self.max_consecutive_failures} consecutive article failures detected!")
                print(f"   This may indicate a systematic issue (API errors, database problems, etc.)")
                print(f"   Please check the error messages above and resolve the issue.")
                print(f"   The pipeline will resume from this point when you restart.")
                break

            # Check if we've hit batch size
            if batch_size and self.stats['processed'] >= batch_size:
                print(f"\n✓ Batch size ({batch_size}) reached!")
                break

            # Print progress every 10 articles
            if self.stats['processed'] % 10 == 0:
                self.print_progress()

        # Expand transitive duplicate relationships if any events were created
        if self.stats['events_created'] > 0:
            print("\nExpanding transitive duplicate relationships...")
            try:
                expansion_stats = self.processor.expand_transitive_duplicates()
                self.stats['duplicates_expanded'] = expansion_stats.get('events_updated', 0)
                self.stats['duplicate_clusters'] = expansion_stats.get('clusters_found', 0)
            except Exception as e:
                print(f"Warning: Could not expand transitive duplicates: {e}")

        # Final statistics
        self.print_final_stats()

    def print_progress(self):
        """Print processing progress"""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['processed'] / elapsed if elapsed > 0 else 0

        print(f"\n  Progress: {self.stats['processed']} articles | "
              f"Success: {self.stats['succeeded']} | "
              f"Failed: {self.stats['failed']} | "
              f"Rate: {rate:.2f} articles/sec")

    def print_final_stats(self):
        """Print final processing statistics"""
        elapsed = time.time() - self.stats['start_time']
        hours = elapsed / 3600
        rate = self.stats['processed'] / elapsed if elapsed > 0 else 0

        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Articles processed: {self.stats['processed']:,}")
        print(f"Succeeded:          {self.stats['succeeded']:,}")
        print(f"Failed:             {self.stats['failed']:,}")
        print(f"Events created:     {self.stats['events_created']:,}")
        if self.stats['duplicate_clusters'] > 0:
            print(f"Duplicate clusters: {self.stats['duplicate_clusters']:,}")
            print(f"Events expanded:    {self.stats['duplicates_expanded']:,}")
        if self.stats['consecutive_failures'] >= self.max_consecutive_failures:
            print(f"⚠️  Consecutive failures: {self.stats['consecutive_failures']} (AUTO-STOPPED)")
        print(f"Duration:           {hours:.2f} hours")
        print(f"Rate:               {rate:.2f} articles/sec")

        # Get overall database statistics
        print("\n" + "-" * 70)
        print("DATABASE STATISTICS")
        print("-" * 70)

        stats = self.db.get_processing_stats()
        if stats:
            print(f"Total articles:     {stats.get('total_articles', 0):,}")
            print(f"Pending:            {stats.get('pending', 0):,}")
            print(f"Completed:          {stats.get('completed', 0):,}")
            print(f"Failed:             {stats.get('failed', 0):,}")
            print(f"Overall progress:   {stats.get('percent_complete', 0):.1f}%")

        # Show recent errors if any
        if self.stats['failed'] > 0:
            print("\n" + "-" * 70)
            print("RECENT ERRORS")
            print("-" * 70)
            errors = self.db.get_recent_errors(limit=5)
            for err in errors:
                print(f"\nArticle: {err['article_id']}")
                print(f"Error:   {err['error_message']}")
                print(f"Time:    {err['updated_at']}")

        print("=" * 70)

    def cleanup(self):
        """Cleanup resources"""
        print("\nClosing database connections...")
        self.db.close()
        print("✓ Cleanup complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Process articles through event extraction pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all pending articles
  python src/process_articles.py

  # Process 100 articles
  python src/process_articles.py --batch 100

  # Process specific articles by ID
  python src/process_articles.py --articles ammannet_4816 alrai_254290

  # Process articles from specific source(s)
  python src/process_articles.py --sources "Al Ghad" "Jordan Times"

  # Process articles from a specific year
  python src/process_articles.py --year 2024

  # Process articles from a specific month
  python src/process_articles.py --year 2024 --month 3

  # Process articles in a date range
  python src/process_articles.py --start-date 2024-01-01 --end-date 2024-03-31

  # Combine filters
  python src/process_articles.py --sources "Al Ghad" --year 2024 --batch 100

  # Initialize queue only (don't process)
  python src/process_articles.py --init-only

The pipeline is resumable - you can stop it (Ctrl+C) and restart anytime.
Progress is saved after each article.
        """
    )

    parser.add_argument(
        '--batch',
        type=int,
        help='Number of articles to process (default: all pending)'
    )

    parser.add_argument(
        '--articles',
        nargs='+',
        help='Specific article ID(s) to process (space-separated list)'
    )

    parser.add_argument(
        '--sources',
        nargs='+',
        help='News source(s) to process (space-separated list, e.g., "Al Ghad" "Jordan Times")'
    )

    parser.add_argument(
        '--year',
        type=int,
        help='Year to process (e.g., 2024)'
    )

    parser.add_argument(
        '--month',
        type=int,
        choices=range(1, 13),
        help='Month to process (1-12, requires --year)'
    )

    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for range filter (YYYY-MM-DD format)'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for range filter (YYYY-MM-DD format)'
    )

    parser.add_argument(
        '--init-only',
        action='store_true',
        help='Only initialize the processing queue, do not process'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.month and not args.year:
        parser.error("--month requires --year to be specified")

    if (args.year or args.month) and (args.start_date or args.end_date):
        parser.error("Cannot use --year/--month with --start-date/--end-date")

    # Validate date formats
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if args.start_date and not date_pattern.match(args.start_date):
        parser.error("--start-date must be in YYYY-MM-DD format")
    if args.end_date and not date_pattern.match(args.end_date):
        parser.error("--end-date must be in YYYY-MM-DD format")

    # Create processor
    processor = ArticleProcessor()

    try:
        if args.init_only:
            # Just initialize queue
            processor.initialize_queue(
                sources=args.sources,
                year=args.year,
                month=args.month,
                start_date=args.start_date,
                end_date=args.end_date,
                article_ids=args.articles
            )
        else:
            # Run processing
            processor.run(
                batch_size=args.batch,
                sources=args.sources,
                year=args.year,
                month=args.month,
                start_date=args.start_date,
                end_date=args.end_date,
                article_ids=args.articles
            )

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Always cleanup
        processor.cleanup()


if __name__ == "__main__":
    main()
