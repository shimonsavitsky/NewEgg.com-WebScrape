"""
Unified Diamond Price Search Tool

Supports multiple diamond API providers:
- OpenFacet: Free, real-time GIA-certified round diamond prices
- Nivoda: Comprehensive diamond search with advanced filters

Usage:
    python diamond_search.py

Requirements:
    pip install requests python-dotenv
"""

import requests
import json
import statistics
from typing import Dict, List, Optional, Any, Literal
from getpass import getpass
import os
from dotenv import load_dotenv
from enum import Enum


class APIProvider(Enum):
    """Supported diamond API providers."""
    OPENFACET = "openfacet"
    NIVODA = "nivoda"


class DiamondSearchClient:
    """Unified client for searching diamonds across multiple API providers."""

    # API Endpoints
    OPENFACET_BASE = "https://data.openfacet.net"
    NIVODA_PRODUCTION = "https://integrations.nivoda.net/api/diamonds"
    NIVODA_STAGING = "https://intg-customer-staging.nivodaapi.net/api/diamonds"

    def __init__(
        self,
        provider: APIProvider = APIProvider.OPENFACET,
        username: str = None,
        password: str = None,
        use_staging: bool = False
    ):
        """
        Initialize the diamond search client.

        Args:
            provider: API provider to use (OPENFACET or NIVODA)
            username: Username (required for Nivoda)
            password: Password (required for Nivoda)
            use_staging: Use staging environment (Nivoda only)
        """
        load_dotenv()

        self.provider = provider

        if provider == APIProvider.NIVODA:
            self.username = username or os.getenv('NIVODA_USERNAME')
            self.password = password or os.getenv('NIVODA_PASSWORD')

            # Check for USE_STAGING env var if use_staging not explicitly set
            if use_staging or os.getenv('NIVODA_USE_STAGING', '').lower() == 'true':
                self.endpoint = self.NIVODA_STAGING
                self.environment = "staging"
            else:
                self.endpoint = self.NIVODA_PRODUCTION
                self.environment = "production"

            if not self.username:
                self.username = input("Enter Nivoda username: ")
            if not self.password:
                self.password = getpass("Enter Nivoda password: ")

    def search_openfacet(
        self,
        carat: Optional[float] = None,
        color: Optional[str] = None,
        clarity: Optional[str] = None,
        cut: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for diamonds using OpenFacet API.

        OpenFacet provides real-time GIA-certified round diamond prices.
        Note: OpenFacet focuses on round diamonds and standard specifications.

        Args:
            carat: Carat weight to search for
            color: Diamond color (D, E, F, G, H, I, J)
            clarity: Diamond clarity (IF, VVS1, VVS2, VS1, VS2, SI1, SI2)
            cut: Diamond cut (usually Excellent for OpenFacet data)

        Returns:
            Dictionary with search results and pricing data
        """
        try:
            # Fetch the index data
            response = requests.get(
                f"{self.OPENFACET_BASE}/index.json",
                timeout=30,
                headers={
                    'User-Agent': 'DiamondSearchTool/1.0',
                    'Accept': 'application/json'
                }
            )
            response.raise_for_status()
            data = response.json()

            # Filter specs based on search criteria
            specs = data.get('specs', [])
            filtered_specs = []

            for spec in specs:
                matches = True

                if carat is not None:
                    # Match within ±0.1 carat
                    if abs(spec.get('carat', 0) - carat) > 0.1:
                        matches = False

                if color and spec.get('color', '').upper() != color.upper():
                    matches = False

                if clarity and spec.get('clarity', '').upper() != clarity.upper():
                    matches = False

                if cut and spec.get('cut', '').upper() != cut.upper():
                    matches = False

                if matches:
                    filtered_specs.append(spec)

            return {
                'provider': 'OpenFacet',
                'dcx_index': data.get('dcx'),
                'timestamp': data.get('ts'),
                'diamonds': filtered_specs,
                'total_count': len(filtered_specs)
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise Exception(
                    "OpenFacet API access denied (403). "
                    "The API may have access restrictions. "
                    "Try using the Nivoda provider instead or contact OpenFacet support."
                )
            else:
                raise Exception(f"OpenFacet API request failed: {e}")
        except Exception as e:
            raise Exception(f"OpenFacet API error: {e}")

    def search_nivoda(
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
        Search for diamonds using Nivoda API.

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
            Dictionary with search results and pricing data
        """
        # Build carat range
        carat_min, carat_max = None, None
        if carat is not None:
            carat_min = carat - 0.1
            carat_max = carat + 0.1
        elif carat_range is not None:
            carat_min, carat_max = carat_range

        # Build price range
        price_min, price_max = None, None
        if price_range is not None:
            price_min, price_max = price_range

        # Build GraphQL query
        query = self._build_nivoda_query(
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

        # Execute query
        try:
            response = requests.post(
                self.endpoint,
                json={'query': query},
                headers={'Content-Type': 'application/json'},
                auth=(self.username, self.password),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if 'errors' in data:
                error_messages = [error.get('message', str(error)) for error in data['errors']]
                raise Exception(f"GraphQL errors: {', '.join(error_messages)}")

            # Extract diamonds
            diamonds = data.get('data', {}).get('diamonds_by_query', {}).get('items', [])
            total_count = data.get('data', {}).get('diamonds_by_query', {}).get('total_count', 0)

            return {
                'provider': 'Nivoda',
                'diamonds': diamonds,
                'total_count': total_count
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Nivoda authentication failed. Check your credentials.")
            elif e.response.status_code == 403:
                raise Exception(
                    "Nivoda API access denied (403). Your account doesn't have API access enabled.\n"
                    "Contact Nivoda support: tech@nivoda.net to enable API access."
                )
            else:
                raise Exception(f"Nivoda API request failed: {e}")

    def _build_nivoda_query(
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
        """Build Nivoda GraphQL query."""
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

        return f"""
        query {{
            diamonds_by_query({filter_str}) {{
                items {{
                    id
                    shape
                    weight
                    color
                    clarity
                    cut
                    polish
                    symmetry
                    fluorescence
                    certificate {{
                        id
                        lab
                        certNumber
                        carats
                        color
                        clarity
                        cut
                    }}
                    price
                    pricePerCarat
                }}
                total_count
            }}
        }}
        """

    def search(
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
        Search for diamonds using the configured provider.

        Returns:
            Dictionary with search results
        """
        if self.provider == APIProvider.OPENFACET:
            return self.search_openfacet(
                carat=carat,
                color=color,
                clarity=clarity,
                cut=cut
            )
        elif self.provider == APIProvider.NIVODA:
            return self.search_nivoda(
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
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def calculate_price_stats(self, diamonds: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate price statistics for diamonds.

        Works with both OpenFacet and Nivoda data formats.

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
            # Handle both OpenFacet and Nivoda formats
            price = diamond.get('price')
            price_per_carat = diamond.get('pricePerCarat') or diamond.get('per_carat')

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

    def search_and_calculate(
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
        Search for diamonds and return results with price statistics.

        Returns:
            Dictionary with 'results' and 'price_stats' keys
        """
        results = self.search(
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

        diamonds = results.get('diamonds', [])
        price_stats = self.calculate_price_stats(diamonds)

        return {
            'results': results,
            'price_stats': price_stats
        }


def main():
    """Main function demonstrating the unified diamond search tool."""
    print("=" * 80)
    print("Unified Diamond Price Search Tool")
    print("=" * 80)
    print()

    print("Available API Providers:")
    print("  1. OpenFacet - Free, real-time GIA-certified round diamonds")
    print("  2. Nivoda - Comprehensive search with advanced filters")
    print()

    provider_choice = input("Select provider (1 for OpenFacet, 2 for Nivoda) [1]: ").strip() or "1"

    if provider_choice == "1":
        provider = APIProvider.OPENFACET
        print("\nUsing OpenFacet API (no authentication required)")
    else:
        provider = APIProvider.NIVODA
        print("\nUsing Nivoda API (authentication required)")

    try:
        client = DiamondSearchClient(provider=provider)

        # Example search
        print("\n" + "=" * 80)
        print("Example Search: 1ct D color VS1 clarity")
        print("=" * 80)
        print()

        result = client.search_and_calculate(
            carat=1.0,
            color='D',
            clarity='VS1',
            cut='Excellent'
        )

        stats = result['price_stats']
        results = result['results']

        print(f"Provider: {results.get('provider', 'Unknown')}")
        print(f"Diamonds found: {stats['count']}")

        if stats['count'] > 0:
            print(f"\nPrice Statistics:")
            print(f"  Average price: ${stats['average_price']:,.2f}")
            print(f"  Median price: ${stats['median_price']:,.2f}")
            print(f"  Price range: ${stats['min_price']:,.2f} - ${stats['max_price']:,.2f}")
            print(f"  Average price per carat: ${stats['average_price_per_carat']:,.2f}")

            # Show sample diamonds
            diamonds = results.get('diamonds', [])[:3]
            if diamonds:
                print(f"\nSample Diamonds:")
                for i, diamond in enumerate(diamonds, 1):
                    print(f"\n  Diamond {i}:")
                    # Handle both OpenFacet and Nivoda formats
                    print(f"    Carat: {diamond.get('carat') or diamond.get('weight', 'N/A')}")
                    print(f"    Color: {diamond.get('color', 'N/A')}")
                    print(f"    Clarity: {diamond.get('clarity', 'N/A')}")
                    print(f"    Cut: {diamond.get('cut', 'N/A')}")
                    print(f"    Price: ${diamond.get('price', 0):,.2f}")
                    if 'per_carat' in diamond or 'pricePerCarat' in diamond:
                        ppc = diamond.get('per_carat') or diamond.get('pricePerCarat', 0)
                        print(f"    Price/ct: ${ppc:,.2f}")
        else:
            print("\nNo diamonds found matching the criteria.")

        # Interactive search
        print("\n" + "=" * 80)
        print("Custom Search")
        print("=" * 80)

        while True:
            try:
                print("\nEnter search criteria (press Enter to skip):")

                carat_input = input("  Carat weight: ").strip()
                carat = float(carat_input) if carat_input else None

                color = input("  Color (D, E, F, G, H, I, J): ").strip().upper() or None
                clarity = input("  Clarity (IF, VVS1, VVS2, VS1, VS2, SI1, SI2): ").strip().upper() or None
                cut = input("  Cut (Excellent, Very Good, Good): ").strip().title() or None

                if provider == APIProvider.NIVODA:
                    shape = input("  Shape (Round, Princess, Oval): ").strip().title() or None
                    lab_input = input("  Lab-grown? (yes/no, Enter for both): ").strip().lower()
                    lab_grown = True if lab_input == 'yes' else False if lab_input == 'no' else None
                else:
                    shape = None
                    lab_grown = None

                print("\nSearching...")

                result = client.search_and_calculate(
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
        return 1

    print("\n" + "=" * 80)
    print("Thank you for using Diamond Search Tool!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    exit(main())
