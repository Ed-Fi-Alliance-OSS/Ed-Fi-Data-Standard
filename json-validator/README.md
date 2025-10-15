# Ed-Fi JSON Validator

A Python script that validates JSON files in a data lake against Ed-Fi OpenAPI specifications.

## Overview

This tool validates JSON files stored in a data lake structure against their corresponding schema definitions in an Ed-Fi OpenAPI specification. It maps directory structures to schema names and performs JSON Schema validation.

## Installation

```bash
cd json-validator
poetry install
```

## Usage

### Command Line

```bash
poetry run validate-json --data-lake-root /path/to/data/lake --openapi-spec /path/to/openapi.json
```

### Python API

```python
from json_validator.validator import DataLakeValidator

validator = DataLakeValidator(
    data_lake_root="/path/to/data/lake",
    openapi_spec_path="/path/to/openapi.json"
)

results = validator.validate_all()
```

## Data Lake Structure

The validator expects a data lake structure like:

```text
root/
├── ed-fi/
│   ├── academicWeeks/
│   │   ├── academicWeek-1.json
│   │   └── academicWeek-2.json
│   └── students/
│       ├── student-1.json
│       └── student-2.json
└── tpdm/
    └── candidates/
        └── candidate-1.json
```

## Schema Mapping

* Files in `ed-fi/academicWeeks/` → `edFi_academicWeek` schema
* Files in `ed-fi/students/` → `edFi_student` schema  
* Files in `tpdm/candidates/` → `tpdm_candidate` schema

## Features

* Validates all JSON files in data lake against OpenAPI schemas
* Supports both local files and remote OpenAPI specifications
* Detailed validation error reporting
* Configurable logging levels
* Performance metrics and summary reporting
