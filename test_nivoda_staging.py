"""
Test script for Nivoda API staging environment
"""

from diamond_search import DiamondSearchClient, APIProvider
import json

print("=" * 80)
print("Testing Nivoda API - Staging Environment")
print("=" * 80)
print()

try:
    # Initialize client with Nivoda provider
    print("Initializing Nivoda client (staging)...")
    client = DiamondSearchClient(provider=APIProvider.NIVODA)

    print(f"Username: {client.username}")
    print(f"Endpoint: {client.endpoint}")
    print(f"Environment: {client.environment}")
    print()

    # Test 1: Simple search
    print("=" * 80)
    print("Test 1: Search for 1ct diamonds")
    print("=" * 80)
    print()

    result = client.search_and_calculate(
        carat=1.0,
        limit=10
    )

    print(f"Provider: {result['results'].get('provider', 'Unknown')}")
    print(f"Total count: {result['results'].get('total_count', 0)}")
    print(f"Diamonds returned: {len(result['results'].get('diamonds', []))}")
    print()

    if result['price_stats']['count'] > 0:
        print("Price Statistics:")
        print(f"  Average price: ${result['price_stats']['average_price']:,.2f}")
        print(f"  Median price: ${result['price_stats']['median_price']:,.2f}")
        print(f"  Price range: ${result['price_stats']['min_price']:,.2f} - ${result['price_stats']['max_price']:,.2f}")
        print(f"  Avg price/ct: ${result['price_stats']['average_price_per_carat']:,.2f}")
        print()

        # Show first diamond details
        diamonds = result['results'].get('diamonds', [])
        if diamonds:
            print("First diamond details:")
            diamond = diamonds[0]
            print(f"  ID: {diamond.get('id', 'N/A')}")
            print(f"  Shape: {diamond.get('shape', 'N/A')}")
            print(f"  Weight: {diamond.get('weight', 'N/A')} ct")
            print(f"  Color: {diamond.get('color', 'N/A')}")
            print(f"  Clarity: {diamond.get('clarity', 'N/A')}")
            print(f"  Cut: {diamond.get('cut', 'N/A')}")
            print(f"  Price: ${diamond.get('price', 0):,.2f}")
            print(f"  Price/ct: ${diamond.get('pricePerCarat', 0):,.2f}")

            cert = diamond.get('certificate', {})
            if cert:
                print(f"  Certificate: {cert.get('lab', 'N/A')} #{cert.get('certNumber', 'N/A')}")
    else:
        print("No diamonds found!")

    print()

    # Test 2: Search with specific criteria (like original request)
    print("=" * 80)
    print("Test 2: Search for 4ct D VVS1 lab-grown diamonds")
    print("=" * 80)
    print()

    result2 = client.search_and_calculate(
        carat=4.0,
        color='D',
        clarity='VVS1',
        lab_grown=True,
        limit=50
    )

    stats = result2['price_stats']
    print(f"Diamonds found: {stats['count']}")

    if stats['count'] > 0:
        print(f"\nPrice Statistics:")
        print(f"  Average price: ${stats['average_price']:,.2f}")
        print(f"  Median price: ${stats['median_price']:,.2f}")
        print(f"  Price range: ${stats['min_price']:,.2f} - ${stats['max_price']:,.2f}")
        print(f"  Avg price/ct: ${stats['average_price_per_carat']:,.2f}")

        diamonds = result2['results'].get('diamonds', [])[:3]
        if diamonds:
            print(f"\nSample diamonds:")
            for i, d in enumerate(diamonds, 1):
                print(f"  {i}. {d.get('weight', 'N/A')}ct {d.get('color', 'N/A')} {d.get('clarity', 'N/A')} - ${d.get('price', 0):,.2f}")
    else:
        print("No 4ct D VVS1 lab-grown diamonds found in staging data")
        print("(Staging may have limited inventory)")

    print()

    # Test 3: Search natural round diamonds
    print("=" * 80)
    print("Test 3: Search for 1ct D VS1 Excellent cut round natural diamonds")
    print("=" * 80)
    print()

    result3 = client.search_and_calculate(
        carat=1.0,
        color='D',
        clarity='VS1',
        cut='Excellent',
        shape='Round',
        lab_grown=False,
        limit=50
    )

    stats = result3['price_stats']
    print(f"Diamonds found: {stats['count']}")

    if stats['count'] > 0:
        print(f"\nPrice Statistics:")
        print(f"  Average price: ${stats['average_price']:,.2f}")
        print(f"  Median price: ${stats['median_price']:,.2f}")
        print(f"  Price range: ${stats['min_price']:,.2f} - ${stats['max_price']:,.2f}")
        print(f"  Avg price/ct: ${stats['average_price_per_carat']:,.2f}")
    else:
        print("No matching diamonds found")

    print()
    print("=" * 80)
    print("✓ All tests completed successfully!")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    import traceback
    traceback.print_exc()
