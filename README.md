# Ecommerce Analytics

RFM analysis and customer segmentation for ecommerce data with automated root-cause analysis.

## Features

- **Data Cleaning Pipeline**: Automated ETL with schema validation
- **RFM Segmentation**: Quintile-based customer scoring (Recency, Frequency, Monetary)
- **Root-Cause Analysis**: Basket comparison and return rate analysis
- **Customer Segments**: Champion, At-Risk, New Customer, Standard
- **Executive Reporting**: Data-driven recommendations

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Ecommerce

# Install dependencies
pip install -e ".[dev]"
```

### Usage

```bash
# Run data cleaning
python clean_data.py

# Run RFM analysis
python analysis.py

# Or use Make commands
make run-etl
make run-analysis
```

### Docker

```bash
# Build image
docker build -t ecommerce-analytics .

# Run analysis
docker run -v $(pwd)/output:/app/output ecommerce-analytics

# Or use docker-compose
docker-compose up etl
docker-compose up analytics
```

## Project Structure

```
.
├── clean_data.py          # ETL pipeline
├── analysis.py            # RFM analysis
├── tests/                 # Unit tests
├── output/                # Generated data
├── report/                # Executive summary
├── pyproject.toml         # Project configuration
└── README.md
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Or use Make
make test
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Format code
make format

# Lint
make lint

# Clean generated files
make clean
```

## CI/CD

GitHub Actions workflow runs on every push:
- Linting (ruff)
- Type checking (mypy)
- Unit tests (pytest)
- Docker build
- Coverage reporting

## Output

- `output/online_retail_cleaned.parquet` - Cleaned sales data
- `output/online_retail_returns.parquet` - Returns data
- `output/rfm_table.parquet` - RFM segmentation results
- `report/executive_summary.md` - Strategic recommendations

## License

MIT
