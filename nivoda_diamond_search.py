"""
Nivoda Diamond Price Search Tool

This tool allows users to search for diamonds by specific criteria using the Nivoda API
and calculate the average price for matching stones.

Usage:
    python nivoda_diamond_search.py

Requirements:
    pip install requests python-dotenv
"""

import requests
import json
import statistics
from typing import Dict, List, Optional, Any
from getpass import getpass
import os
from dotenv import load_dotenv


class NivodaDiamondSearch:
    """Client for searching diamonds and calculating prices using Nivoda API."""

    # API Endpoints
    PRODUCTION_ENDPOINT = "https://integrations.nivoda.net/api/diamonds"
    STAGING_ENDPOINT = "https://intg-customer-staging.nivodaapi.net/api/diamonds"

    def __init__(self, username: str = None, password: str = None, use_staging: bool = False):
        """
        Initialize the Nivoda API client.

        Args:
            username: Nivoda account username (if None, will try env var or prompt)
            password: Nivoda account password (if None, will try env var or prompt)
            use_staging: Whether to use staging endpoint (default: False)
        """
        load_dotenv()

        self.username = username or os.getenv('NIVODA_USERNAME')
        self.password = password or os.getenv('NIVODA_PASSWORD')
        self.endpoint = self.STAGING_ENDPOINT if use_staging else self.PRODUCTION_ENDPOINT

        if not self.username:
            self.username = input("Enter Nivoda username: ")
        if not self.password:
            self.password = getpass("Enter Nivoda password: ")

    def build_search_query(
        self,
        carat_min: Optional[float] = None,
        carat_max: Optional[float] = None,
        color: Optional[str] = None,
        clarity: Optional[str] = None,
        cut: Optional[str] = None,
        shape: Optional[str] = None,
        lab_grown: Optional[bool] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        limit: int = 100
    ) -> str:
        """
        Build a GraphQL query for searching diamonds.

        Args:
            carat_min: Minimum carat weight
            carat_max: Maximum carat weight
            color: Diamond color (e.g., 'D', 'E', 'F')
            clarity: Diamond clarity (e.g., 'VVS1', 'VVS2', 'VS1')
            cut: Diamond cut grade (e.g., 'Excellent', 'Very Good')
            shape: Diamond shape (e.g., 'Round', 'Princess', 'Oval')
            lab_grown: True for lab-grown, False for natural, None for both
            price_min: Minimum price
            price_max: Maximum price
            limit: Maximum number of results to return

        Returns:
            GraphQL query string
        """
        # Build filter conditions
        filters = []

        if carat_min is not None:
            filters.append(f'size_from: {carat_min}')
        if carat_max is not None:
            filters.append(f'size_to: {carat_max}')
        if color:
            filters.append(f'color: "{color}"')
        if clarity:
            filters.append(f'clarity: "{clarity}"')
        if cut:
            filters.append(f'cut: "{cut}"')
        if shape:
            filters.append(f'shape: "{shape}"')
        if lab_grown is not None:
            filters.append(f'lab_grown: {str(lab_grown).lower()}')
        if price_min is not None:
            filters.append(f'price_from: {price_min}')
        if price_max is not None:
            filters.append(f'price_to: {price_max}')

        filters.append(f'limit: {limit}')

        filter_str = ', '.join(filters)

        # Build GraphQL query
        # Note: Field names may need adjustment based on actual API schema
        query = f"""
        query {{
            diamonds_by_query({filter_str}) {{
                items {{
                    id
                    video
                    image
                    availability
                    supplierStockId
                    shape
                    weight
                    color
                    clarity
                    cut
                    polish
                    symmetry
                    fluorescence
                    measurements {{
                        length
                        width
                        depth
                    }}
                    certificate {{
                        id
                        lab
                        certNumber
                        shape
                        carats
                        color
                        clarity
                        cut
                    }}
                    price
                    discount
                    pricePerCarat
                    mine_of_origin
                    brown
                    green
                    milky
                    eyeClean
                    blue_nuance
                }}
                total_count
            }}
        }}
        """

        return query

    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a GraphQL query against the Nivoda API.

        Args:
            query: GraphQL query string

        Returns:
            API response as dictionary

        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        headers = {
            'Content-Type': 'application/json',
        }

        payload = {
            'query': query
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                auth=(self.username, self.password),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if 'errors' in data:
                error_messages = [error.get('message', str(error)) for error in data['errors']]
                raise Exception(f"GraphQL errors: {', '.join(error_messages)}")

            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Authentication failed. Please check your username and password.")
            elif e.response.status_code == 403:
                error_msg = (
                    "Access forbidden (403). Your Nivoda account doesn't have API access enabled.\n\n"
                    "To enable API access:\n"
                    "  1. Contact Nivoda support: tech@nivoda.net\n"
                    "  2. Request API access activation for your account\n"
                    "  3. Or contact your account manager\n\n"
                    "Note: Web platform credentials alone are not sufficient for API access.\n"
                    "See README_NIVODA.md for detailed instructions."
                )
                raise Exception(error_msg)
            else:
                raise Exception(f"API request failed: {e}")

    def search_diamonds(
        self,
        carat: Optional[float] = None,
        carat_range: Optional[tuple] = None,
        color: Optional[str] = None,
        clarity: Optional[str] = None,
        cut: Optional[str] = None,
        shape: Optional[str] = None,
        lab_grown: Optional[bool] = None,
        price_range: Optional[tuple] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for diamonds matching the specified criteria.

        Args:
            carat: Exact carat weight (will search +/- 0.1 ct)
            carat_range: Tuple of (min_carat, max_carat)
            color: Diamond color
            clarity: Diamond clarity
            cut: Diamond cut grade
            shape: Diamond shape
            lab_grown: True for lab-grown, False for natural
            price_range: Tuple of (min_price, max_price)
            limit: Maximum number of results

        Returns:
            List of diamond dictionaries
        """
        # Determine carat range
        carat_min, carat_max = None, None
        if carat is not None:
            carat_min = carat - 0.1
            carat_max = carat + 0.1
        elif carat_range is not None:
            carat_min, carat_max = carat_range

        # Determine price range
        price_min, price_max = None, None
        if price_range is not None:
            price_min, price_max = price_range

        # Build and execute query
        query = self.build_search_query(
            carat_min=carat_min,
            carat_max=carat_max,
            color=color,
            clarity=clarity,
            cut=cut,
            shape=shape,
            lab_grown=lab_grown,
            price_min=price_min,
            price_max=price_max,
            limit=limit
        )

        response = self.execute_query(query)

        # Extract diamonds from response
        try:
            diamonds = response['data']['diamonds_by_query']['items']
            total_count = response['data']['diamonds_by_query']['total_count']

            print(f"Found {total_count} matching diamonds (showing {len(diamonds)})")
            return diamonds
        except KeyError:
            print("Warning: Unexpected API response structure")
            print(f"Response: {json.dumps(response, indent=2)}")
            return []

    def calculate_average_price(self, diamonds: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate price statistics for a list of diamonds.

        Args:
            diamonds: List of diamond dictionaries

        Returns:
            Dictionary with price statistics
        """
        if not diamonds:
            return {
                'count': 0,
                'average_price': 0,
                'median_price': 0,
                'min_price': 0,
                'max_price': 0,
                'average_price_per_carat': 0
            }

        prices = []
        prices_per_carat = []

        for diamond in diamonds:
            price = diamond.get('price')
            price_per_carat = diamond.get('pricePerCarat')

            if price is not None:
                prices.append(float(price))
            if price_per_carat is not None:
                prices_per_carat.append(float(price_per_carat))

        if not prices:
            return {
                'count': 0,
                'average_price': 0,
                'median_price': 0,
                'min_price': 0,
                'max_price': 0,
                'average_price_per_carat': 0
            }

        return {
            'count': len(prices),
            'average_price': statistics.mean(prices),
            'median_price': statistics.median(prices),
            'min_price': min(prices),
            'max_price': max(prices),
            'average_price_per_carat': statistics.mean(prices_per_carat) if prices_per_carat else 0,
            'std_deviation': statistics.stdev(prices) if len(prices) > 1 else 0
        }

    def search_and_get_average_price(
        self,
        carat: Optional[float] = None,
        carat_range: Optional[tuple] = None,
        color: Optional[str] = None,
        clarity: Optional[str] = None,
        cut: Optional[str] = None,
        shape: Optional[str] = None,
        lab_grown: Optional[bool] = None,
        price_range: Optional[tuple] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for diamonds and return both the results and price statistics.

        Returns:
            Dictionary with 'diamonds' and 'price_stats' keys
        """
        diamonds = self.search_diamonds(
            carat=carat,
            carat_range=carat_range,
            color=color,
            clarity=clarity,
            cut=cut,
            shape=shape,
            lab_grown=lab_grown,
            price_range=price_range,
            limit=limit
        )

        price_stats = self.calculate_average_price(diamonds)

        return {
            'diamonds': diamonds,
            'price_stats': price_stats
        }


def format_search_criteria(**criteria) -> str:
    """Format search criteria for display."""
    parts = []

    if criteria.get('carat'):
        parts.append(f"{criteria['carat']} ct")
    elif criteria.get('carat_range'):
        min_ct, max_ct = criteria['carat_range']
        parts.append(f"{min_ct}-{max_ct} ct")

    if criteria.get('shape'):
        parts.append(criteria['shape'])

    if criteria.get('color'):
        parts.append(f"{criteria['color']} color")

    if criteria.get('clarity'):
        parts.append(f"{criteria['clarity']} clarity")

    if criteria.get('cut'):
        parts.append(f"{criteria['cut']} cut")

    if criteria.get('lab_grown') is not None:
        parts.append("Lab-grown" if criteria['lab_grown'] else "Natural")

    return ", ".join(parts) if parts else "No filters"


def main():
    """Main function demonstrating the diamond search tool."""
    print("=" * 80)
    print("Nivoda Diamond Price Search Tool")
    print("=" * 80)
    print()

    # Initialize the client
    print("Initializing Nivoda API client...")
    client = NivodaDiamondSearch()

    print()
    print("=" * 80)
    print("Example Search: 4ct Lab-grown D color VVS1 clarity")
    print("=" * 80)
    print()

    # Example search: 4ct lab-grown D color VVS1 clarity
    try:
        result = client.search_and_get_average_price(
            carat=4.0,
            color='D',
            clarity='VVS1',
            lab_grown=True,
            limit=100
        )

        diamonds = result['diamonds']
        stats = result['price_stats']

        print(f"\nSearch Results:")
        print(f"  Total diamonds found: {stats['count']}")

        if stats['count'] > 0:
            print(f"\nPrice Statistics:")
            print(f"  Average price: ${stats['average_price']:,.2f}")
            print(f"  Median price: ${stats['median_price']:,.2f}")
            print(f"  Price range: ${stats['min_price']:,.2f} - ${stats['max_price']:,.2f}")
            print(f"  Average price per carat: ${stats['average_price_per_carat']:,.2f}")
            if stats['std_deviation'] > 0:
                print(f"  Standard deviation: ${stats['std_deviation']:,.2f}")

            # Show some sample diamonds
            print(f"\nSample Diamonds (showing first 5):")
            for i, diamond in enumerate(diamonds[:5], 1):
                print(f"\n  Diamond {i}:")
                print(f"    Shape: {diamond.get('shape', 'N/A')}")
                print(f"    Weight: {diamond.get('weight', 'N/A')} ct")
                print(f"    Color: {diamond.get('color', 'N/A')}")
                print(f"    Clarity: {diamond.get('clarity', 'N/A')}")
                print(f"    Cut: {diamond.get('cut', 'N/A')}")
                print(f"    Price: ${diamond.get('price', 0):,.2f}")
                print(f"    Price/ct: ${diamond.get('pricePerCarat', 0):,.2f}")
                if diamond.get('certificate'):
                    cert = diamond['certificate']
                    print(f"    Certificate: {cert.get('lab', 'N/A')} #{cert.get('certNumber', 'N/A')}")
        else:
            print("\nNo diamonds found matching the criteria.")

        # Interactive search
        print("\n" + "=" * 80)
        print("Custom Search")
        print("=" * 80)
        print()

        while True:
            try:
                print("\nEnter search criteria (press Enter to skip any field):")

                carat_input = input("  Carat weight (e.g., 4.0): ").strip()
                carat = float(carat_input) if carat_input else None

                color = input("  Color (D, E, F, G, H, I, J, etc.): ").strip().upper() or None
                clarity = input("  Clarity (FL, IF, VVS1, VVS2, VS1, VS2, etc.): ").strip().upper() or None
                cut = input("  Cut (Excellent, Very Good, Good, etc.): ").strip().title() or None
                shape = input("  Shape (Round, Princess, Oval, etc.): ").strip().title() or None

                lab_input = input("  Lab-grown? (yes/no, or Enter for both): ").strip().lower()
                lab_grown = True if lab_input == 'yes' else False if lab_input == 'no' else None

                print(f"\nSearching for: {format_search_criteria(carat=carat, color=color, clarity=clarity, cut=cut, shape=shape, lab_grown=lab_grown)}")
                print()

                result = client.search_and_get_average_price(
                    carat=carat,
                    color=color,
                    clarity=clarity,
                    cut=cut,
                    shape=shape,
                    lab_grown=lab_grown,
                    limit=100
                )

                stats = result['price_stats']

                if stats['count'] > 0:
                    print(f"\nFound {stats['count']} diamonds:")
                    print(f"  Average price: ${stats['average_price']:,.2f}")
                    print(f"  Median price: ${stats['median_price']:,.2f}")
                    print(f"  Price range: ${stats['min_price']:,.2f} - ${stats['max_price']:,.2f}")
                    print(f"  Average price per carat: ${stats['average_price_per_carat']:,.2f}")
                else:
                    print("\nNo diamonds found matching the criteria.")

                another = input("\nPerform another search? (yes/no): ").strip().lower()
                if another != 'yes':
                    break

            except ValueError as e:
                print(f"Invalid input: {e}")
            except KeyboardInterrupt:
                print("\n\nSearch cancelled.")
                break

    except Exception as e:
        print(f"\nError: {e}")
        print("\nPlease ensure:")
        print("  1. Your Nivoda credentials are correct")
        print("  2. Your account has API access enabled")
        print("  3. You have an active internet connection")
        print("\nFor API documentation, visit: https://bitbucket.org/nivoda/nivoda-api/src/main/")
        return 1

    print("\n" + "=" * 80)
    print("Thank you for using Nivoda Diamond Price Search Tool!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    exit(main())
