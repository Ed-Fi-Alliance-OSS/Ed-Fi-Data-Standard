# Ed-Fi JSON Validator - Quick Start Guide

## Installation

1. Navigate to the json-validator directory:

   ```bash
   cd json-validator
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

## Basic Usage

### Validate all files in a data lake

```bash
poetry run python json_validator \
  --data-lake-root /path/to/your/data/lake \
  --openapi-spec /path/to/openapi/specification.json
```

### Validate a single file

```bash
poetry run python json_validator \
  --data-lake-root /path/to/your/data/lake \
  --openapi-spec /path/to/openapi/specification.json \
  --file student-1.json
```

### Use a remote OpenAPI specification

```bash
poetry run python json_validator \
  --data-lake-root /path/to/your/data/lake \
  --openapi-spec https://api.ed-fi.org/v6.0.0/api/metadata/data/v3/openapi.json
```

### List available schemas

```bash
poetry run python json_validator \
  --data-lake-root /path/to/your/data/lake \
  --openapi-spec /path/to/openapi/specification.json \
  --list-schemas
```

### Quiet mode (summary only)

```bash
poetry run python json_validator \
  --data-lake-root /path/to/your/data/lake \
  --openapi-spec /path/to/openapi/specification.json \
  --quiet
```

## Expected Data Lake Structure

```none
root/
├── ed-fi/
│   ├── academicWeeks/
│   │   ├── academicWeek-1.json
│   │   └── academicWeek-2.json
│   ├── students/
│   │   ├── student-1.json
│   │   └── student-2.json
│   └── schools/
│       └── school-1.json
├── tpdm/
│   └── candidates/
│       └── candidate-1.json
└── extensions/
    └── customEntities/
        └── entity-1.json
```

## Schema Mapping

The validator automatically maps directory names to schema names:

* `ed-fi/students/` → `edFi_student` schema
* `ed-fi/academicWeeks/` → `edFi_academicWeek` schema
* `tpdm/candidates/` → `tpdm_candidate` schema
* `extensions/customEntities/` → `extensions_customEntity` schema

## Exit Codes

* `0`: All validations passed
* `1`: One or more validations failed
* `2`: Invalid command line arguments

## Python API Usage

```python
from json_validator.validator import DataLakeValidator

# Initialize validator
validator = DataLakeValidator(
    data_lake_root="/path/to/data/lake",
    openapi_spec_path="/path/to/openapi.json"
)

# Validate all files
results, summary = validator.validate_all()

# Validate single file
result = validator.validate_file("/path/to/file.json")

# Get available schemas
schemas = validator.get_available_schemas()
```

## Running Tests

```bash
poetry run pytest
```

## Code Quality

```bash
# Run linting
poetry run flake8 json_validator/

# Run type checking
poetry run mypy json_validator/

# Format code
poetry run black json_validator/
```
