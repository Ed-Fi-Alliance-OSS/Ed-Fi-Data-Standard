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
poetry run python json_validator --data-lake-root /path/to/data/lake --openapi-spec /path/to/openapi.json
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

## Testing

This directory contains `sample/` with sample JSON files for demonstration purposes.

Example 1: running the validation using a `swagger.json` file from a running instance of the Ed-Fi ODS/API, using Data Standard 5.2 with the TPDM extension.

```shell
poetry run python json_validator --data-lake-root ./sample --openapi-spec https://api.ed-fi.org/v7.2/api/metadata/data/v3/resources/swagger.json
```

Example 2: running with a `.yaml` file in this repository, using Data Standard 6. Note that the TPDM extension no longer exists, and the Assessment data model has a breaking change compared to Data Standard 5.2. Therefore all files have a failure when compared to Data Standard 6.

```shell
poetry run python json_validator --data-lake-root ./sample --openapi-spec ../../Schemas/OpenAPI/Ed-Fi-Resource-API-Specification.yaml
```
