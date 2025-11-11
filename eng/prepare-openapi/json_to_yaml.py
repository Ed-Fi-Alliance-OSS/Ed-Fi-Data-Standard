#!/usr/bin/env python3
"""
JSON to YAML Converter

Converts JSON files to YAML format with proper formatting and validation.
Supports both single file conversion and batch processing of directories.

Usage:
    python json_to_yaml.py input.json output.yaml
    python json_to_yaml.py input.json  # Creates input.yaml
    python json_to_yaml.py --directory input_dir output_dir
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data as a dictionary

    Raises:
        json.JSONDecodeError: If the JSON is invalid
        FileNotFoundError: If the file doesn't exist
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {file_path}: {e}")
        raise
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise


def save_yaml_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save data as a YAML file.

    Args:
        data: Dictionary to save as YAML
        file_path: Output file path
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                allow_unicode=True,
                width=1000,  # Prevent line wrapping for long strings
            )
        logging.info(f"Successfully saved YAML to {file_path}")
    except Exception as e:
        logging.error(f"Error saving YAML to {file_path}: {e}")
        raise


def convert_single_file(input_path: Path, output_path: Optional[Path] = None) -> None:
    """Convert a single JSON file to YAML.

    Args:
        input_path: Path to input JSON file
        output_path: Path to output YAML file (optional)
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_path.suffix.lower() == ".json":
        raise ValueError(f"Input file must have .json extension: {input_path}")

    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.with_suffix(".yaml")

    logging.info(f"Converting {input_path} to {output_path}")

    # Load JSON data
    json_data = load_json_file(input_path)

    # Save as YAML
    save_yaml_file(json_data, output_path)

    print(f"✓ Converted {input_path.name} → {output_path.name}")


def convert_directory(input_dir: Path, output_dir: Path) -> None:
    """Convert all JSON files in a directory to YAML.

    Args:
        input_dir: Input directory containing JSON files
        output_dir: Output directory for YAML files
    """
    if not input_dir.exists() or not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory not found: {input_dir}")

    # Find all JSON files in input directory
    json_files = list(input_dir.glob("*.json"))

    if not json_files:
        logging.warning(f"No JSON files found in {input_dir}")
        return

    logging.info(f"Found {len(json_files)} JSON files to convert")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    error_count = 0

    for json_file in json_files:
        try:
            yaml_file = output_dir / json_file.with_suffix(".yaml").name
            convert_single_file(json_file, yaml_file)
            success_count += 1
        except Exception as e:
            logging.error(f"Failed to convert {json_file}: {e}")
            error_count += 1

    print(f"\nConversion complete: {success_count} successful, {error_count} errors")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert JSON files to YAML format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file
  python json_to_yaml.py openapi.json openapi.yaml

  # Convert single file (auto-generate output name)
  python json_to_yaml.py openapi.json

  # Convert all JSON files in directory
  python json_to_yaml.py --directory json_specs yaml_specs
        """,
    )

    parser.add_argument("input", help="Input JSON file or directory")

    parser.add_argument(
        "output",
        nargs="?",
        help="Output YAML file or directory (optional for single files)",
    )

    parser.add_argument(
        "--directory",
        action="store_true",
        help="Process all JSON files in input directory",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    try:
        input_path = Path(args.input)

        if args.directory:
            # Directory mode
            if not args.output:
                parser.error("Output directory required when using --directory")

            output_path = Path(args.output)
            convert_directory(input_path, output_path)
        else:
            # Single file mode
            output_path = Path(args.output) if args.output else None
            convert_single_file(input_path, output_path)

        print("Conversion completed successfully!")

    except KeyboardInterrupt:
        print("\nConversion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
