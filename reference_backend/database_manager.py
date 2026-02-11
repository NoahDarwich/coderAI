"""
Database Manager for Event Extraction Pipeline
Handles all database operations with connection pooling and error handling
"""

import psycopg2
from psycopg2 import pool, extras
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
import json
import hashlib
from datetime import datetime
from config import db_config


class DatabaseManager:
    """Manages database connections and operations for the event extraction pipeline"""

    def __init__(self, min_connections: int = 1, max_connections: int = 3):
        """
        Initialize database manager with connection pool

        Args:
            min_connections: Minimum number of connections in pool
            max_connections: Maximum number of connections in pool
        """
        try:
            params = db_config.get_psycopg2_params()
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                **params
            )
            self._transaction_conn = None  # Track active transaction connection
            print(f"✓ Database connection pool created ({min_connections}-{max_connections} connections)")
        except Exception as e:
            print(f"✗ Failed to create connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Automatically commits on success, rollbacks on error, and returns connection to pool

        If called within a transaction() context, uses the transaction's connection
        without committing (transaction handles commit/rollback)
        """
        # If we're inside a transaction, use that connection
        if self._transaction_conn is not None:
            yield self._transaction_conn
            return  # Don't commit/rollback - let transaction handle it

        # Otherwise, get a new connection and manage it
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    @contextmanager
    def transaction(self):
        """
        Transaction context manager for article-level operations
        Provides all-or-nothing semantics for multi-step processing

        Usage:
            with db.transaction():
                # All database operations here automatically use the same connection
                # Either all succeed (commit) or all fail (rollback)
                db.save_extractions(...)
                db.save_enrichment(...)
                db.finalize_event(...)
        """
        if self._transaction_conn is not None:
            raise RuntimeError("Nested transactions are not supported")

        conn = None
        try:
            conn = self.pool.getconn()
            self._transaction_conn = conn
            yield
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            self._transaction_conn = None
            if conn:
                self.pool.putconn(conn)

    # ============================================================
    # Processing State Management
    # ============================================================

    def initialize_processing_state(self,
                                    sources: Optional[List[str]] = None,
                                    year: Optional[int] = None,
                                    month: Optional[int] = None,
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    article_ids: Optional[List[str]] = None) -> int:
        """
        Initialize processing_state table from main_corpus
        Only adds articles that haven't been added yet

        Args:
            sources: Optional list of news sources to filter by (None = all sources)
            year: Optional year to filter by (e.g., 2024)
            month: Optional month to filter by (1-12, requires year to be set)
            start_date: Optional start date for range filter (YYYY-MM-DD format)
            end_date: Optional end date for range filter (YYYY-MM-DD format)
            article_ids: Optional list of specific article IDs to process

        Returns:
            Number of articles added to processing queue
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build WHERE clause for filters
            where_conditions = []
            params = []

            # Article ID filter (takes precedence)
            if article_ids:
                where_conditions.append("mc.article_id = ANY(%s)")
                params.append(article_ids)

            # Source filter
            if sources:
                where_conditions.append("mc.news_source = ANY(%s)")
                params.append(sources)

            # Date filters
            if year and month:
                # Specific month and year
                where_conditions.append("EXTRACT(YEAR FROM mc.date) = %s AND EXTRACT(MONTH FROM mc.date) = %s")
                params.extend([year, month])
            elif year:
                # Whole year
                where_conditions.append("EXTRACT(YEAR FROM mc.date) = %s")
                params.append(year)
            elif start_date and end_date:
                # Date range
                where_conditions.append("mc.date >= %s AND mc.date <= %s")
                params.extend([start_date, end_date])
            elif start_date:
                # Only start date
                where_conditions.append("mc.date >= %s")
                params.append(start_date)
            elif end_date:
                # Only end date
                where_conditions.append("mc.date <= %s")
                params.append(end_date)

            # Build the complete WHERE clause
            where_clause = ""
            if where_conditions:
                where_clause = "AND " + " AND ".join(where_conditions)

            # Insert articles from main_corpus that aren't already in processing_state
            query = f"""
                INSERT INTO processing_state (
                    article_id, source_text, source_date, source_link,
                    source_category, source_name, status
                )
                SELECT
                    mc.article_id,
                    mc.text,
                    mc.date,
                    mc.link,
                    mc.news_category,
                    mc.news_source,
                    'pending'
                FROM main_corpus mc
                WHERE NOT EXISTS (
                    SELECT 1 FROM processing_state ps
                    WHERE ps.article_id = mc.article_id
                )
                {where_clause}
            """

            cursor.execute(query, params)
            count = cursor.rowcount
            cursor.close()
            return count

    def get_next_article(self,
                         year: Optional[int] = None,
                         month: Optional[int] = None,
                         sources: Optional[List[str]] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         article_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get the next pending article to process, with optional filtering

        Args:
            year: Optional year to filter by
            month: Optional month to filter by (requires year)
            sources: Optional list of news sources to filter by
            start_date: Optional start date for range filter (YYYY-MM-DD)
            end_date: Optional end date for range filter (YYYY-MM-DD)
            article_ids: Optional list of specific article IDs to process

        Returns:
            Dictionary with article data, or None if no articles pending
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

            # Build WHERE clause for filters
            where_conditions = ["status = 'pending'"]
            params = []

            # Article ID filter
            if article_ids:
                where_conditions.append("article_id = ANY(%s)")
                params.append(article_ids)

            # Source filter
            if sources:
                where_conditions.append("source_name = ANY(%s)")
                params.append(sources)

            # Date filters
            if year and month:
                where_conditions.append("EXTRACT(YEAR FROM source_date) = %s AND EXTRACT(MONTH FROM source_date) = %s")
                params.extend([year, month])
            elif year:
                where_conditions.append("EXTRACT(YEAR FROM source_date) = %s")
                params.append(year)
            elif start_date and end_date:
                where_conditions.append("source_date >= %s AND source_date <= %s")
                params.extend([start_date, end_date])
            elif start_date:
                where_conditions.append("source_date >= %s")
                params.append(start_date)
            elif end_date:
                where_conditions.append("source_date <= %s")
                params.append(end_date)

            where_clause = " AND ".join(where_conditions)

            cursor.execute(f"""
                SELECT article_id, source_text, source_date, source_link
                FROM processing_state
                WHERE {where_clause}
                ORDER BY created_at
                LIMIT 1
            """, params)

            result = cursor.fetchone()
            cursor.close()

            return dict(result) if result else None

    def update_article_status(self, article_id: str, status: str,
                             error_message: Optional[str] = None,
                             events_extracted: Optional[int] = None) -> None:
        """
        Update the processing status of an article

        Args:
            article_id: Article ID
            status: New status (pending, extracted, enriched, completed, failed)
            error_message: Optional error message if status is 'failed'
            events_extracted: Number of events extracted (for completed status)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if status == 'failed':
                cursor.execute("""
                    UPDATE processing_state
                    SET status = %s, error_message = %s, updated_at = NOW()
                    WHERE article_id = %s
                """, (status, error_message, article_id))
            elif status == 'completed':
                # Update with events count (defaults to 0 if not provided)
                events_count = events_extracted if events_extracted is not None else 0
                cursor.execute("""
                    UPDATE processing_state
                    SET status = %s, completed_at = NOW(), updated_at = NOW(),
                        events_extracted = %s
                    WHERE article_id = %s
                """, (status, events_count, article_id))
            elif status in ['extracted', 'enriched']:
                cursor.execute("""
                    UPDATE processing_state
                    SET status = %s, updated_at = NOW()
                    WHERE article_id = %s
                """, (status, article_id))
            else:  # pending or other
                cursor.execute("""
                    UPDATE processing_state
                    SET status = %s, updated_at = NOW()
                    WHERE article_id = %s
                """, (status, article_id))

            cursor.close()

    def mark_article_started(self, article_id: str) -> None:
        """Mark an article as started processing"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE processing_state
                SET started_at = NOW(), updated_at = NOW()
                WHERE article_id = %s
            """, (article_id,))
            cursor.close()

    # ============================================================
    # Event Creation (Direct Insert to events table)
    # ============================================================

    def create_event(self, article_id: str, event_data: Dict[str, Any]) -> str:
        """
        Create event record directly in events table (3-table architecture)

        Args:
            article_id: Article ID
            event_data: Dictionary containing all event fields (82 columns):
                - event: Event narrative text (required)
                - event_number: Order within article (used for event_id generation)
                - is_duplicate: Whether event is duplicate
                - duplicate_events_ids: List of duplicate event IDs
                - All enrichment fields from 13 assistants

        Returns:
            event_id in format: {article_id}_{event_number:04d}
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Generate event_id (extract event_number for ID but don't store in DB)
            event_number = event_data.get('event_number', 1)
            event_id = f"{article_id}_{str(event_number).zfill(4)}"

            # Insert complete event with all ~82 columns
            cursor.execute("""
                INSERT INTO events (
                    event_id, article_id, event,

                    -- Event Classification
                    protest_event, threat_event, planned_event, planned_event_date,
                    commemorative, commemorative_name, multi_sited, multi_site_tag,
                    national_strike, is_recurring,

                    -- Duplicate Detection
                    is_duplicate, duplicate_events_ids,

                    -- Date & Time
                    start_date, end_date, num_of_days, time_of_day,

                    -- Start Location
                    Governorate, District, Town, Neighborhood, Name_of_location,
                    raw_extracted_location, government_building, Latitude, Longitude, geometric_center, location_type,

                    -- End Location
                    end_Governorate, end_District, end_Town, end_Neighborhood, end_Name_of_location,
                    raw_extracted_end_location, end_government_building, end_Latitude, end_Longitude, end_geometric_center, end_location_type,

                    -- Tactics
                    tactic_original_text, tactic_classification,

                    -- Participants
                    participants_type_original, Participant_type_1, Participant_type_2, Participant_type_3,
                    participants_num, participants_num_text, "Participating group",
                    sector, protesters_occupation, Work_space, Same_workspace, Work_space_name,

                    -- Organizers
                    organizing_actor, organizing_actor_local_class, organizing_actor_national_class,
                    spokesperson_name, organization_actor_type,

                    -- Mediators
                    mediators, mediators_type_one, mediators_type_two,

                    -- Targets
                    target, target_category, target_category2, target_level,

                    -- Demands
                    demands, demands_classification_one, demands_classification_two,
                    geographically_concentrated_demand, slogans, trigger_of_protest,
                    "pro-government_event", international_solidarity, solidarity_with_palestine,

                    -- Violence & Repression
                    repression, repression_reports, responding_actor, responding_actor_class,
                    protesters_violence, protesters_violence_reports, Obstruction_of_space
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                event_id, article_id, event_data.get('event'),

                # Event Classification
                event_data.get('protest_event'), event_data.get('threat_event'),
                event_data.get('planned_event'), event_data.get('planned_event_date'),
                event_data.get('commemorative'), event_data.get('commemorative_name'),
                event_data.get('multi_sited'), event_data.get('multi_site_tag'),
                event_data.get('national_strike'), event_data.get('is_recurring'),

                # Duplicate Detection
                event_data.get('is_duplicate', False),
                json.dumps(event_data.get('duplicate_events_ids', [])),

                # Date & Time
                event_data.get('start_date'), event_data.get('end_date'),
                event_data.get('num_of_days'), event_data.get('time_of_day'),

                # Start Location
                event_data.get('Governorate'), event_data.get('District'),
                event_data.get('Town'), event_data.get('Neighborhood'), event_data.get('Name_of_location'),
                event_data.get('raw_extracted_location'), event_data.get('government_building'),
                event_data.get('Latitude'), event_data.get('Longitude'),
                event_data.get('geometric_center'), event_data.get('location_type'),

                # End Location
                event_data.get('end_Governorate'), event_data.get('end_District'),
                event_data.get('end_Town'), event_data.get('end_Neighborhood'), event_data.get('end_Name_of_location'),
                event_data.get('raw_extracted_end_location'), event_data.get('end_government_building'),
                event_data.get('end_Latitude'), event_data.get('end_Longitude'),
                event_data.get('end_geometric_center'), event_data.get('end_location_type'),

                # Tactics
                json.dumps(event_data.get('tactic_original_text')) if event_data.get('tactic_original_text') else None,
                json.dumps(event_data.get('tactic_classification')) if event_data.get('tactic_classification') else None,

                # Participants
                json.dumps(event_data.get('participants_type_original')) if event_data.get('participants_type_original') else None,
                event_data.get('Participant_type_1'), event_data.get('Participant_type_2'), event_data.get('Participant_type_3'),
                event_data.get('participants_num'), event_data.get('participants_num_text'),
                json.dumps(event_data.get('Participating group')) if event_data.get('Participating group') else None,
                json.dumps(event_data.get('sector')) if event_data.get('sector') else None,
                json.dumps(event_data.get('protesters_occupation')) if event_data.get('protesters_occupation') else None,
                event_data.get('Work_space'), event_data.get('Same_workspace'),
                json.dumps(event_data.get('Work_space_name')) if event_data.get('Work_space_name') else None,

                # Organizers
                json.dumps(event_data.get('organizing_actor')) if event_data.get('organizing_actor') else None,
                event_data.get('organizing_actor_local_class'), event_data.get('organizing_actor_national_class'),
                event_data.get('spokesperson_name'),
                json.dumps(event_data.get('organization_actor_type')) if event_data.get('organization_actor_type') else None,

                # Mediators
                json.dumps(event_data.get('mediators')) if event_data.get('mediators') else None,
                json.dumps(event_data.get('mediators_type_one')) if event_data.get('mediators_type_one') else None,
                json.dumps(event_data.get('mediators_type_two')) if event_data.get('mediators_type_two') else None,

                # Targets
                event_data.get('target'), event_data.get('target_category'),
                event_data.get('target_category2'), event_data.get('target_level'),

                # Demands
                json.dumps(event_data.get('demands')) if event_data.get('demands') else None,
                json.dumps(event_data.get('demands_classification_one')) if event_data.get('demands_classification_one') else None,
                json.dumps(event_data.get('demands_classification_two')) if event_data.get('demands_classification_two') else None,
                event_data.get('geographically_concentrated_demand'),
                json.dumps(event_data.get('slogans')) if event_data.get('slogans') else None,
                event_data.get('trigger_of_protest'),
                event_data.get('pro-government_event'),
                event_data.get('international_solidarity'),
                event_data.get('solidarity_with_palestine'),

                # Violence & Repression
                event_data.get('repression'),
                json.dumps(event_data.get('repression_reports')) if event_data.get('repression_reports') else None,
                json.dumps(event_data.get('responding_actor')) if event_data.get('responding_actor') else None,
                json.dumps(event_data.get('responding_actor_class')) if event_data.get('responding_actor_class') else None,
                event_data.get('protesters_violence'),
                json.dumps(event_data.get('protesters_violence_reports')) if event_data.get('protesters_violence_reports') else None,
                event_data.get('Obstruction_of_space')
            ))

            cursor.close()
            return event_id

    # ============================================================
    # Duplicate Detection
    # ============================================================

    def get_events_by_date_range(self, start_date: str, end_date: Optional[str] = None,
                                  planned_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all events with overlapping date ranges for duplicate checking

        ACTIVE METHOD: This is the primary method used for duplicate detection in the
        current pipeline. It provides simple, efficient date-based filtering.
        The filtered candidates are then passed to duplicate_check_db() for AI-based
        comparison.

        Matches events where ANY of these conditions are true:
        1. Event date ranges overlap (start_date/end_date)
        2. Candidate's planned_event_date falls within our date range
        3. Our planned_event_date falls within candidate's date range

        Args:
            start_date: Start date of the event to check
            end_date: End date of the event to check (None if single day event)
            planned_date: Planned event date (for planned/future events)

        Returns:
            List of events with overlapping dates or matching planned dates
        """
        if end_date is None:
            end_date = start_date

        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

            # Query events where date ranges overlap OR planned dates match
            # Condition 1: Date ranges overlap (start1 <= end2 AND end1 >= start2)
            # Condition 2: Candidate's planned_event_date is within our range
            # Condition 3: Our planned_event_date is within candidate's range
            cursor.execute("""
                SELECT
                    e.event_id,
                    e.event,
                    e.start_date,
                    e.end_date,
                    e.planned_event_date,
                    e.raw_extracted_location,
                    e.raw_extracted_end_location
                FROM events e
                WHERE
                    e.is_duplicate = FALSE
                    AND (
                        -- Condition 1: Date ranges overlap
                        (
                            e.start_date <= %s
                            AND COALESCE(e.end_date, e.start_date) >= %s
                        )
                        -- Condition 2: Candidate's planned_event_date within our range
                        OR (
                            e.planned_event_date IS NOT NULL
                            AND e.planned_event_date >= %s
                            AND e.planned_event_date <= %s
                        )
                        -- Condition 3: Our planned_event_date within candidate's range
                        OR (
                            %s IS NOT NULL
                            AND %s >= e.start_date
                            AND %s <= COALESCE(e.end_date, e.start_date)
                        )
                    )
                ORDER BY e.start_date
            """, (end_date, start_date, start_date, end_date, planned_date, planned_date, planned_date))

            results = cursor.fetchall()
            cursor.close()

            return [dict(row) for row in results]


    # ============================================================
    # Statistics and Monitoring
    # ============================================================

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get overall processing statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

            cursor.execute("SELECT * FROM processing_progress")
            result = cursor.fetchone()

            cursor.close()
            return dict(result) if result else {}

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent processing errors"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

            cursor.execute(f"SELECT * FROM recent_errors LIMIT {limit}")
            results = cursor.fetchall()

            cursor.close()
            return [dict(row) for row in results]

    # ============================================================
    # Cleanup
    # ============================================================

    def close(self):
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()
            print("✓ Database connection pool closed")


# Convenience function for creating database manager
def create_db_manager() -> DatabaseManager:
    """Create and return a DatabaseManager instance"""
    return DatabaseManager()


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    db = create_db_manager()

    stats = db.get_processing_stats()
    print(f"\nProcessing stats: {stats}")

    db.close()
    print("\n✓ Database manager test completed")
