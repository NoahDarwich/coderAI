"""
Location Agent for extracting and enriching location data using Google Maps API.

This module provides functions to:
1. Extract location information from text using Google Maps API
2. Fill missing location data in DataFrames
3. Add latitude and longitude coordinates
4. Handle both start and end locations for protest events
"""

import pandas as pd
import requests
import time
import logging
from typing import Dict, List, Optional, Tuple, Union
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocationAgent:
    """
    A class to handle location data extraction and enrichment using Google Maps API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LocationAgent with Google Maps API key.

        Args:
            api_key (str, optional): Google Maps API key. If not provided,
                                   will try to get from GOOGLE_MAPS_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key is required. Set GOOGLE_MAPS_API_KEY environment variable or pass api_key parameter.")

        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.rate_limit_delay = 0.1  # Delay between requests to respect rate limits

    def geocode_location(self, location_text: str, country_code: str = "JO") -> Dict:
        """
        Geocode a location string using Google Maps API.

        Args:
            location_text (str): The location text to geocode
            country_code (str): Country code to bias results (default: "JO" for Jordan)

        Returns:
            Dict: Dictionary containing geocoding results with keys:
                - 'formatted_address': Full formatted address
                - 'latitude': Latitude coordinate
                - 'longitude': Longitude coordinate
                - 'components': Dictionary of address components
        """
        if not location_text or pd.isna(location_text):
            return self._empty_result()

        # Clean the location text
        location_text = str(location_text).strip()
        if not location_text:
            return self._empty_result()

        # Add country bias for better results
        query = f"{location_text}, {country_code}"

        params = {
            'address': query,
            'key': self.api_key,
            'region': country_code.lower(),
            'language': 'en'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                return self._parse_geocoding_result(result)
            else:
                logger.warning(f"Geocoding failed for '{location_text}': {data.get('status', 'Unknown error')}")
                return self._empty_result()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for '{location_text}': {e}")
            return self._empty_result()
        except Exception as e:
            logger.error(f"Unexpected error geocoding '{location_text}': {e}")
            return self._empty_result()
        finally:
            # Rate limiting
            time.sleep(self.rate_limit_delay)

    def _parse_geocoding_result(self, result: Dict) -> Dict:
        """Parse Google Maps geocoding result into standardized format for Jordan."""
        try:
            location = result['geometry']['location']
            location_type = result['geometry'].get('location_type', 'UNKNOWN')
            components = {}

            # Debug: Log all address components to understand the structure
            logger.debug(f"Full address components: {result.get('address_components', [])}")
            logger.debug(f"Location type: {location_type}")

            # Extract address components with better mapping for Jordan's administrative structure
            for component in result.get('address_components', []):
                types = component['types']
                long_name = component['long_name']
                short_name = component.get('short_name', '')

                # Debug: Log each component
                logger.debug(f"Component: {long_name} ({short_name}) - Types: {types}")

                # Map to Jordan's administrative subdivisions
                if 'administrative_area_level_1' in types:  # Governorate (highest level)
                    components['governorate'] = long_name
                elif 'administrative_area_level_2' in types:  # District/Liwaa
                    components['district'] = long_name
                elif 'administrative_area_level_3' in types:  # Town/Qadaa (sub-district)
                    components['town'] = long_name
                elif 'administrative_area_level_4' in types:  # Additional subdivision
                    # Use as neighborhood if we don't have one yet
                    if 'neighborhood' not in components:
                        components['neighborhood'] = long_name
                elif 'locality' in types:  # City/Town (fallback for town)
                    if 'town' not in components:
                        components['town'] = long_name
                elif 'sublocality' in types or 'sublocality_level_1' in types:  # Neighborhood
                    components['neighborhood'] = long_name
                elif 'neighborhood' in types:  # Neighborhood (alternative)
                    components['neighborhood'] = long_name
                elif 'route' in types:  # Street
                    components['street'] = long_name
                elif 'establishment' in types or 'point_of_interest' in types:  # Specific location
                    components['establishment'] = long_name
                elif 'premise' in types:  # Building/premise
                    if 'establishment' not in components:
                        components['establishment'] = long_name

            return {
                'formatted_address': result['formatted_address'],
                'latitude': location['lat'],
                'longitude': location['lng'],
                'location_type': location_type,
                'geometric_center': location_type == 'GEOMETRIC_CENTER',
                'components': components
            }
        except Exception as e:
            logger.error(f"Error parsing geocoding result: {e}")
            return self._empty_result()


    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'formatted_address': None,
            'latitude': None,
            'longitude': None,
            'location_type': None,
            'geometric_center': False,
            'components': {}
        }

    def debug_api_response(self, location_text: str, country_code: str = "JO") -> Dict:
        """
        Debug method to examine the full Google Maps API response structure.
        
        Args:
            location_text (str): Location text to geocode
            country_code (str): Country code to bias results
            
        Returns:
            Dict: Full API response for debugging
        """
        if not location_text or pd.isna(location_text):
            return {}

        location_text = str(location_text).strip()
        if not location_text:
            return {}

        query = f"{location_text}, {country_code}"
        params = {
            'address': query,
            'key': self.api_key,
            'region': country_code.lower(),
            'language': 'en'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                return data['results'][0]
            else:
                logger.warning(f"API call failed for '{location_text}': {data.get('status', 'Unknown error')}")
                return {}
                
        except Exception as e:
            logger.error(f"Error in debug_api_response for '{location_text}': {e}")
            return {}
        finally:
            time.sleep(self.rate_limit_delay)

    def extract_location_info(self, location_text: str, country_code: str = "JO") -> Dict:
        """
        Extract structured location information from text.

        Args:
            location_text (str): Location text to process
            country_code (str): Country code for biasing results

        Returns:
            Dict: Structured location information with keys:
                - 'Governorate': Governorate name
                - 'District': District/Liwaa name
                - 'Town': Town/Qadaa name
                - 'Neighborhood': Neighborhood name
                - 'Name_of_location': Specific location name
                - 'Latitude': Latitude coordinate
                - 'Longitude': Longitude coordinate
                - 'formatted_address': Full formatted address
                - 'geometric_center': Boolean indicating if coordinates are a geometric center
        """
        geocode_result = self.geocode_location(location_text, country_code)

        if not geocode_result['latitude'] or not geocode_result['longitude']:
            return {
                'Governorate': None,
                'District': None,
                'Town': None,
                'Neighborhood': None,
                'Name_of_location': location_text if location_text else None,
                'Latitude': None,
                'Longitude': None,
                'formatted_address': None,
                'geometric_center': False
            }

        components = geocode_result['components']

        # Debug: Print components to understand API response structure
        if components:
            logger.info(f"Extracted components for '{location_text}': {components}")

        return {
            'Governorate': components.get('governorate'),
            'District': components.get('district'),
            'Town': components.get('town'),
            'Neighborhood': components.get('neighborhood'),
            'Name_of_location': components.get('establishment') or components.get('street') or location_text,
            'Latitude': geocode_result['latitude'],
            'Longitude': geocode_result['longitude'],
            'formatted_address': geocode_result['formatted_address'],
            'geometric_center': geocode_result['geometric_center']
        }

    def fill_missing_location_data(self, df: pd.DataFrame,
                                 location_columns: List[str] = None,
                                 country_code: str = "JO") -> pd.DataFrame:
        """
        Fill missing location data in a DataFrame using Google Maps API.

        Args:
            df (pd.DataFrame): DataFrame containing location columns
            location_columns (List[str], optional): List of location columns to process.
                                                   If None, uses default location columns.
            country_code (str): Country code for biasing results

        Returns:
            pd.DataFrame: DataFrame with filled location data and added coordinates
        """
        if location_columns is None:
            location_columns = [
                'Governorate', 'District', 'Town', 'Neighborhood',
                'Name_of_location', 'multi_sited', 'end_Governorate',
                'end_District', 'end_Town', 'end_Neighborhood',
                'end_Name_of_location', 'end_multi_sited'
            ]

        # Create a copy to avoid modifying original
        result_df = df.copy()

        # Add coordinate columns if they don't exist
        coord_columns = ['Latitude', 'Longitude', 'end_Latitude', 'end_Longitude',
                        'geometric_center', 'end_geometric_center']
        for col in coord_columns:
            if col not in result_df.columns:
                result_df[col] = None

        # Process each row
        for idx, row in result_df.iterrows():
            logger.info(f"Processing row {idx + 1}/{len(result_df)}")

            # Process start location
            start_location_info = self._process_location_row(
                row, location_columns[:5], country_code, is_start=True
            )

            # Process end location
            end_location_info = self._process_location_row(
                row, location_columns[6:], country_code, is_start=False
            )

            # Update the row with extracted information (only fill empty values)
            for key, value in start_location_info.items():
                if key in result_df.columns:
                    # Only update if current value is empty
                    current_value = result_df.loc[idx, key]
                    # Ensure we have a scalar value
                    if isinstance(current_value, pd.Series):
                        current_value = current_value.iloc[0] if len(current_value) > 0 else None
                    is_empty = pd.isna(current_value) or (isinstance(current_value, str) and current_value.strip() == '')
                    if is_empty:
                        result_df.at[idx, key] = value

            for key, value in end_location_info.items():
                if key in result_df.columns:
                    # Only update if current value is empty
                    current_value = result_df.loc[idx, key]
                    # Ensure we have a scalar value
                    if isinstance(current_value, pd.Series):
                        current_value = current_value.iloc[0] if len(current_value) > 0 else None
                    is_empty = pd.isna(current_value) or (isinstance(current_value, str) and current_value.strip() == '')
                    if is_empty:
                        result_df.at[idx, key] = value

        return result_df

    def _process_location_row(self, row: pd.Series, location_columns: List[str],
                            country_code: str, is_start: bool = True) -> Dict:
        """Process a single row's location data."""
        prefix = "" if is_start else "end_"

        # Check if we have any non-null location data
        location_data = [row[col] for col in location_columns if col in row.index and pd.notna(row[col])]

        if not location_data:
            return {}

        # Create location string from available data
        location_parts = []
        for col in location_columns:
            if col in row.index and pd.notna(row[col]) and str(row[col]).strip():
                location_parts.append(str(row[col]).strip())

        if not location_parts:
            return {}

        location_string = ", ".join(location_parts)

        # Extract location information
        location_info = self.extract_location_info(location_string, country_code)

        # Only use results if we have valid coordinates
        if not location_info['Latitude'] or not location_info['Longitude']:
            return {}

        # Map to DataFrame columns
        result = {}

        # Map location components (Jordan administrative subdivisions)
        component_mapping = {
            'Governorate': 'Governorate',
            'District': 'District',  # Liwaa
            'Town': 'Town',         # Qadaa
            'Neighborhood': 'Neighborhood',
            'Name_of_location': 'Name_of_location'
        }

        for df_col, info_key in component_mapping.items():
            target_col = f"{prefix}{df_col}" if not is_start else df_col
            if target_col in row.index:
                # Only fill if current value is null/empty
                current_value = row[target_col]
                if pd.isna(current_value) or str(current_value).strip() == '':
                    result[target_col] = location_info[info_key]

        # Add coordinates
        lat_col = f"{prefix}Latitude" if not is_start else "Latitude"
        lng_col = f"{prefix}Longitude" if not is_start else "Longitude"
        geo_center_col = f"{prefix}geometric_center" if not is_start else "geometric_center"

        if lat_col in row.index:
            result[lat_col] = location_info['Latitude']
        if lng_col in row.index:
            result[lng_col] = location_info['Longitude']
        if geo_center_col in row.index:
            result[geo_center_col] = location_info['geometric_center']

        return result

    def batch_geocode_locations(self, location_texts: List[str],
                              country_code: str = "JO",
                              batch_size: int = 10) -> List[Dict]:
        """
        Geocode multiple locations in batches.

        Args:
            location_texts (List[str]): List of location texts to geocode
            country_code (str): Country code for biasing results
            batch_size (int): Number of locations to process in each batch

        Returns:
            List[Dict]: List of geocoding results
        """
        results = []

        for i in range(0, len(location_texts), batch_size):
            batch = location_texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(location_texts) + batch_size - 1)//batch_size}")

            for location_text in batch:
                result = self.extract_location_info(location_text, country_code)
                results.append(result)

        return results


def create_location_agent(api_key: Optional[str] = None) -> LocationAgent:
    """
    Factory function to create a LocationAgent instance.

    Args:
        api_key (str, optional): Google Maps API key

    Returns:
        LocationAgent: Configured LocationAgent instance
    """
    return LocationAgent(api_key)


# Convenience functions for direct use
def fill_location_data(df: pd.DataFrame,
                      api_key: Optional[str] = None,
                      location_columns: List[str] = None,
                      country_code: str = "JO") -> pd.DataFrame:
    """
    Convenience function to fill location data in a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing location columns
        api_key (str, optional): Google Maps API key
        location_columns (List[str], optional): List of location columns to process
        country_code (str): Country code for biasing results

    Returns:
        pd.DataFrame: DataFrame with filled location data
    """
    agent = create_location_agent(api_key)
    return agent.fill_missing_location_data(df, location_columns, country_code)


def extract_single_location(location_text: str,
                          api_key: Optional[str] = None,
                          country_code: str = "JO") -> Dict:
    """
    Convenience function to extract location information from a single text.

    Args:
        location_text (str): Location text to process
        api_key (str, optional): Google Maps API key
        country_code (str): Country code for biasing results

    Returns:
        Dict: Structured location information
    """
    agent = create_location_agent(api_key)
    return agent.extract_location_info(location_text, country_code)


if __name__ == "__main__":
    # Example usage
    agent = create_location_agent()

    # Test with a sample location
    sample_location = "Amman, Jordan"
    result = agent.extract_location_info(sample_location)
    print("Sample location extraction:")
    print(result)
