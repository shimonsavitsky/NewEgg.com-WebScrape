# Diamond Price Search Tools

A comprehensive suite of tools for searching diamonds and calculating average prices using multiple API providers.

## Overview

This repository contains diamond price search tools that support multiple API providers:

1. **OpenFacet** - Free, real-time GIA-certified round diamond prices
2. **Nivoda** - Comprehensive diamond search with advanced filters

## Tools Available

### 1. Unified Diamond Search Tool (`diamond_search.py`)

**Recommended** - A single tool that supports both OpenFacet and Nivoda APIs.

**Features:**
- Switch between API providers at runtime
- Unified interface for both APIs
- Price statistics calculation (average, median, min/max, per-carat)
- Interactive CLI
- Programmatic API

**Usage:**
```bash
python diamond_search.py
```

**Quick Example:**
```python
from diamond_search import DiamondSearchClient, APIProvider

# Try OpenFacet (free, no auth)
client = DiamondSearchClient(provider=APIProvider.OPENFACET)

result = client.search_and_calculate(
    carat=1.0,
    color='D',
    clarity='VS1',
    cut='Excellent'
)

print(f"Found {result['price_stats']['count']} diamonds")
print(f"Average price: ${result['price_stats']['average_price']:,.2f}")
```

### 2. Nivoda-Only Tool (`nivoda_diamond_search.py`)

A specialized tool for Nivoda API with more detailed features.

**Usage:**
```bash
python nivoda_diamond_search.py
```

See [README_NIVODA.md](README_NIVODA.md) for detailed Nivoda documentation.

## API Provider Comparison

| Feature | OpenFacet | Nivoda |
|---------|-----------|--------|
| **Cost** | Free | Requires account |
| **Authentication** | None | Username + Password + API access |
| **Diamond Types** | Natural, GIA-certified rounds | Natural + Lab-grown, all shapes |
| **Search Filters** | Carat, Color, Clarity, Cut | Carat, Color, Clarity, Cut, Shape, Lab-grown, Price, etc. |
| **Data Coverage** | Round diamonds, standard specs | Comprehensive inventory |
| **Setup Time** | Instant | Requires API access approval |
| **Best For** | Quick lookups, round diamonds | Comprehensive searches, lab-grown |

## Installation

1. **Clone the repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up credentials** (for Nivoda only):
   ```bash
   cp .env.example .env
   # Edit .env with your Nivoda credentials
   ```

## Quick Start

### Using OpenFacet (No Setup Required)

```bash
python diamond_search.py
# Select option 1 for OpenFacet
```

### Using Nivoda (Requires Credentials)

```bash
# Set up .env file first
python diamond_search.py
# Select option 2 for Nivoda
```

## API Provider Details

### OpenFacet

**Pros:**
- ✅ Free and open
- ✅ No authentication required
- ✅ Real-time GIA-certified pricing
- ✅ Instant access

**Cons:**
- ❌ Limited to round diamonds
- ❌ Standard specifications only
- ❌ No lab-grown diamonds
- ❌ May have access restrictions (403 errors reported)

**Endpoints:**
- Index: `https://data.openfacet.net/index.json`
- Matrix: `https://data.openfacet.net/matrix.json`
- Depth: `https://data.openfacet.net/depth.json`

**Documentation:** https://openfacet.net/en/api-docs/

### Nivoda

**Pros:**
- ✅ Comprehensive inventory
- ✅ Lab-grown + Natural diamonds
- ✅ All shapes (Round, Princess, Oval, etc.)
- ✅ Advanced filtering
- ✅ Verified supplier network

**Cons:**
- ❌ Requires account signup
- ❌ API access must be enabled (contact support)
- ❌ Setup time required

**Documentation:** https://bitbucket.org/nivoda/nivoda-api/src/main/

**Enabling API Access:**
1. Email: tech@nivoda.net
2. Request API access for your account
3. Provide your account email

## Example Searches

### Search for 4ct Lab-Grown D VVS1 (Nivoda)

```python
from diamond_search import DiamondSearchClient, APIProvider

client = DiamondSearchClient(provider=APIProvider.NIVODA)

result = client.search_and_calculate(
    carat=4.0,
    color='D',
    clarity='VVS1',
    lab_grown=True
)

print(f"Average price: ${result['price_stats']['average_price']:,.2f}")
```

### Search for 1ct D VS1 Round (OpenFacet)

```python
from diamond_search import DiamondSearchClient, APIProvider

client = DiamondSearchClient(provider=APIProvider.OPENFACET)

result = client.search_and_calculate(
    carat=1.0,
    color='D',
    clarity='VS1',
    cut='Excellent'
)

print(f"Average price: ${result['price_stats']['average_price']:,.2f}")
```

### Price Range Search (Nivoda)

```python
client = DiamondSearchClient(provider=APIProvider.NIVODA)

result = client.search_and_calculate(
    carat_range=(2.0, 3.0),
    price_range=(10000, 25000),
    cut='Excellent',
    lab_grown=True
)
```

## Programmatic Usage

### Unified Client

```python
from diamond_search import DiamondSearchClient, APIProvider

# Initialize client
client = DiamondSearchClient(
    provider=APIProvider.OPENFACET  # or APIProvider.NIVODA
)

# Search
result = client.search(
    carat=1.5,
    color='E',
    clarity='VVS2',
    cut='Excellent'
)

# Calculate statistics
stats = client.calculate_price_stats(result['diamonds'])

print(f"Average: ${stats['average_price']:,.2f}")
print(f"Median: ${stats['median_price']:,.2f}")
print(f"Range: ${stats['min_price']:,.2f} - ${stats['max_price']:,.2f}")
```

### Comparing Across Providers

```python
from diamond_search import DiamondSearchClient, APIProvider

# Search both providers
criteria = {
    'carat': 1.0,
    'color': 'D',
    'clarity': 'VS1',
    'cut': 'Excellent'
}

# OpenFacet
openfacet_client = DiamondSearchClient(provider=APIProvider.OPENFACET)
openfacet_result = openfacet_client.search_and_calculate(**criteria)

# Nivoda (if you have access)
nivoda_client = DiamondSearchClient(provider=APIProvider.NIVODA)
nivoda_result = nivoda_client.search_and_calculate(**criteria)

print(f"OpenFacet avg: ${openfacet_result['price_stats']['average_price']:,.2f}")
print(f"Nivoda avg: ${nivoda_result['price_stats']['average_price']:,.2f}")
```

## Troubleshooting

### OpenFacet: 403 Forbidden Error

If you get a 403 error with OpenFacet:
1. The API may have temporary restrictions
2. Try using Nivoda instead
3. Check OpenFacet's status page
4. Contact OpenFacet support

**Workaround:** Use the Nivoda provider instead:
```bash
python diamond_search.py
# Select option 2 for Nivoda
```

### Nivoda: Access Denied (403)

Your account doesn't have API access enabled:
1. Email: tech@nivoda.net
2. Request API access activation
3. Provide your account email: shimmy@shimmytime.watch
4. Wait for confirmation

See [README_NIVODA.md](README_NIVODA.md) for detailed instructions.

### No Diamonds Found

- **Criteria too restrictive:** Try broadening your search
- **Wrong provider:** OpenFacet only has round natural diamonds
- **Price range:** If using price filters, they may be too narrow

## Price Statistics Explained

The tools calculate these statistics:

- **Average Price:** Mean price across all matching diamonds
- **Median Price:** Middle value (less affected by outliers)
- **Min/Max Price:** Price range
- **Average Price Per Carat:** Mean per-carat price
- **Standard Deviation:** Price variability (higher = more spread)

## Files

- `diamond_search.py` - Unified multi-API tool (recommended)
- `nivoda_diamond_search.py` - Nivoda-specific tool
- `requirements.txt` - Python dependencies
- `.env.example` - Credential template
- `.gitignore` - Protects sensitive files
- `README.md` - This file
- `README_NIVODA.md` - Detailed Nivoda documentation

## Environment Variables

Create a `.env` file for Nivoda credentials:

```env
NIVODA_USERNAME=your_email@example.com
NIVODA_PASSWORD=your_password
```

**Security:** The `.env` file is excluded from git via `.gitignore`.

## Requirements

- Python 3.7+
- requests
- python-dotenv

## Use Cases

### Jewelers & Retailers
- Compare market prices
- Source diamonds
- Price inventory

### Consumers
- Research diamond prices
- Compare options
- Budget planning

### Analysts
- Market analysis
- Price trends
- Data collection

### Developers
- Build pricing tools
- Integrate diamond data
- Create comparison apps

## Support & Documentation

### OpenFacet
- **Docs:** https://openfacet.net/en/api-docs/
- **MCP Server:** https://mcp.openfacet.net/

### Nivoda
- **Docs:** https://bitbucket.org/nivoda/nivoda-api/src/main/
- **Support:** tech@nivoda.net
- **GraphiQL:** https://integrations.nivoda.net/api/diamonds-graphiql

## Contributing

To add support for additional diamond APIs:

1. Add provider to `APIProvider` enum
2. Implement `search_<provider>()` method
3. Update the `search()` dispatcher
4. Add documentation

## License

This tool is provided as-is for use with the respective diamond APIs. Ensure you comply with each API provider's Terms of Service.

## Changelog

### Version 1.1 (Current)
- Added unified multi-API tool
- OpenFacet integration
- Nivoda integration
- Interactive CLI
- Price statistics

### Version 1.0
- Initial Nivoda-only implementation

## Roadmap

Future enhancements:
- [ ] Add more diamond API providers (RapNet, IDEX)
- [ ] Web interface
- [ ] Price history tracking
- [ ] Advanced analytics
- [ ] Export to CSV/JSON
- [ ] Price alerts

## Author

Created for diamond price research and comparison.

## Support

For issues:
- **Tool issues:** Check Troubleshooting section
- **OpenFacet API:** Contact OpenFacet support
- **Nivoda API:** Contact tech@nivoda.net
