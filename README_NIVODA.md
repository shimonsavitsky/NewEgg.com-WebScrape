# Nivoda Diamond Price Search Tool

A Python tool for searching diamonds using the Nivoda API and calculating average prices based on specific criteria like carat weight, color, clarity, cut, and whether they're lab-grown or natural.

## Features

- Search for diamonds by multiple criteria:
  - Carat weight (exact or range)
  - Color (D, E, F, G, H, I, J, etc.)
  - Clarity (FL, IF, VVS1, VVS2, VS1, VS2, SI1, SI2, etc.)
  - Cut grade (Excellent, Very Good, Good, etc.)
  - Shape (Round, Princess, Oval, Cushion, etc.)
  - Type (Lab-grown or Natural)
  - Price range

- Calculate comprehensive price statistics:
  - Average price
  - Median price
  - Price range (min/max)
  - Average price per carat
  - Standard deviation

- Interactive command-line interface
- Support for both production and staging environments

## Prerequisites

1. **Nivoda Account**: You need an active Nivoda account
2. **API Access**: Your account must have API access enabled (see setup below)
3. **Python 3.7+**: Make sure Python is installed on your system

## Important: Enabling API Access

⚠️ **Your Nivoda web login credentials alone are NOT sufficient for API access.**

To use this tool, you must have API access enabled on your account:

1. **Contact Nivoda Support**:
   - Email: tech@nivoda.net or support@nivoda.net
   - Request API access for your account
   - Mention you want to use the GraphQL API

2. **Contact Your Account Manager**:
   - If you have a dedicated account manager, contact them directly
   - Request activation of API access for production

3. **Verify Access**:
   - Once enabled, your existing login credentials should work with the API
   - You can test access using the GraphiQL explorer at:
     - Production: https://integrations.nivoda.net/api/diamonds-graphiql
     - Credentials for docs: `nivoda-api-docs` / `nivoda-graphql`

## Installation

1. **Clone or download this repository**

2. **Install required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your credentials**:

   Option A - Environment variables (recommended):
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

   Option B - Enter credentials when prompted:
   ```bash
   # The script will prompt for credentials if not found in .env
   ```

## Configuration

Edit the `.env` file with your Nivoda credentials:

```env
NIVODA_USERNAME=your_email@example.com
NIVODA_PASSWORD=your_password
```

**Security Note**: The `.env` file is in `.gitignore` and will not be committed to version control.

## Usage

### Basic Usage

Run the interactive tool:

```bash
python nivoda_diamond_search.py
```

The tool will:
1. Prompt for credentials (if not in `.env`)
2. Run an example search (4ct lab-grown D VVS1)
3. Enter interactive mode for custom searches

### Programmatic Usage

You can also use the tool as a Python module:

```python
from nivoda_diamond_search import NivodaDiamondSearch

# Initialize the client
client = NivodaDiamondSearch(
    username='your_email@example.com',
    password='your_password'
)

# Search for diamonds
result = client.search_and_get_average_price(
    carat=4.0,
    color='D',
    clarity='VVS1',
    lab_grown=True,
    limit=100
)

# Access results
print(f"Found {result['price_stats']['count']} diamonds")
print(f"Average price: ${result['price_stats']['average_price']:,.2f}")
print(f"Price per carat: ${result['price_stats']['average_price_per_carat']:,.2f}")

# Access individual diamonds
for diamond in result['diamonds']:
    print(f"Diamond: {diamond['weight']}ct {diamond['color']} {diamond['clarity']}")
    print(f"  Price: ${diamond['price']:,.2f}")
```

### Search Parameters

All search parameters are optional:

```python
client.search_and_get_average_price(
    carat=4.0,                    # Exact carat (searches ±0.1ct)
    carat_range=(3.5, 4.5),       # Or specify a range
    color='D',                     # D, E, F, G, H, I, J, K, L, M, etc.
    clarity='VVS1',                # FL, IF, VVS1, VVS2, VS1, VS2, SI1, SI2, etc.
    cut='Excellent',               # Excellent, Very Good, Good, Fair, Poor
    shape='Round',                 # Round, Princess, Oval, Cushion, etc.
    lab_grown=True,                # True, False, or None for both
    price_range=(10000, 50000),   # Min and max price
    limit=100                      # Max results (default: 100)
)
```

### Example Searches

**4 carat lab-grown D color VVS1 clarity**:
```python
result = client.search_and_get_average_price(
    carat=4.0,
    color='D',
    clarity='VVS1',
    lab_grown=True
)
```

**3-5 carat natural round diamonds, E-F color**:
```python
# Search for E color
result_e = client.search_diamonds(
    carat_range=(3.0, 5.0),
    color='E',
    shape='Round',
    lab_grown=False
)

# Search for F color
result_f = client.search_diamonds(
    carat_range=(3.0, 5.0),
    color='F',
    shape='Round',
    lab_grown=False
)

# Combine and calculate stats
all_diamonds = result_e + result_f
stats = client.calculate_average_price(all_diamonds)
```

**Budget search (under $20,000)**:
```python
result = client.search_and_get_average_price(
    carat_range=(2.0, 3.0),
    price_range=(0, 20000),
    cut='Excellent',
    lab_grown=True
)
```

## Output Example

```
================================================================================
Nivoda Diamond Price Search Tool
================================================================================

Initializing Nivoda API client...

================================================================================
Example Search: 4ct Lab-grown D color VVS1 clarity
================================================================================

Found 47 matching diamonds (showing 47)

Search Results:
  Total diamonds found: 47

Price Statistics:
  Average price: $18,456.32
  Median price: $17,890.00
  Price range: $14,230.00 - $24,500.00
  Average price per carat: $4,614.08
  Standard deviation: $2,341.12

Sample Diamonds (showing first 5):

  Diamond 1:
    Shape: Round
    Weight: 4.01 ct
    Color: D
    Clarity: VVS1
    Cut: Excellent
    Price: $18,500.00
    Price/ct: $4,613.47
    Certificate: GIA #2141234567
```

## Troubleshooting

### "Access denied" Error

This means your account doesn't have API access enabled. Solutions:

1. **Enable API access**: Contact Nivoda support (tech@nivoda.net) to enable API access
2. **Use staging**: Try using staging credentials (request from support)
3. **Verify credentials**: Double-check your username and password

### Authentication Failed

- Ensure your credentials in `.env` are correct
- Check that you're using your email address, not a username
- Verify your account is active on Nivoda platform

### No Diamonds Found

- Try broadening your search criteria
- Check if your filters are too restrictive
- Verify the values you're using match Nivoda's standards:
  - Colors: D, E, F, G, H, I, J, K, L, M
  - Clarity: FL, IF, VVS1, VVS2, VS1, VS2, SI1, SI2, I1, I2, I3
  - Cut: Excellent, Very Good, Good, Fair, Poor

### GraphQL Errors

If you see GraphQL errors, it may indicate:
- Field names have changed in the API
- You're requesting fields not available to your account tier
- Try updating the `build_search_query` method in the code

## API Documentation

- **Official Docs**: https://bitbucket.org/nivoda/nivoda-api/src/main/
- **GraphiQL Explorer**: https://integrations.nivoda.net/api/diamonds-graphiql
- **Support Email**: tech@nivoda.net

## Notes on API Schema

**Important**: This tool was built based on publicly available Nivoda API documentation. The actual GraphQL schema field names may vary. If you encounter errors about unknown fields:

1. Access the GraphiQL explorer (credentials: `nivoda-api-docs` / `nivoda-graphql`)
2. Use the schema explorer to see exact field names
3. Update the `build_search_query` method in `nivoda_diamond_search.py` accordingly

Common field name variations you might encounter:
- `weight` vs `carats` vs `size`
- `price` vs `total_price` vs `asking_price`
- `pricePerCarat` vs `price_per_carat` vs `per_carat_price`

## Development

### Running Tests

```bash
# Test API connection
python test_api_staging.py

# Test with sample data
python nivoda_diamond_search.py
```

### Modifying Search Filters

Edit the `build_search_query` method in `nivoda_diamond_search.py` to add new filters or modify existing ones.

## License

This tool is provided as-is for use with the Nivoda API. Ensure you comply with Nivoda's Terms of Service when using their API.

## Support

For issues with this tool:
- Check the Troubleshooting section above
- Review the Nivoda API documentation
- Contact Nivoda support for API-specific questions

For Nivoda API access and questions:
- Email: tech@nivoda.net
- Support: support@nivoda.net
