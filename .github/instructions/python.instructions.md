---
applyTo: "**/*.py, **/pyproject.toml"
---

# GitHub Copilot Instructions for Python Files

## Purpose

This file provides guidance for GitHub Copilot to assist with editing, creating, and maintaining PYthon scripts in this repository, especially within the `eng` directory

## General Guidelines

- **Code Review:** Make only high confidence suggestions when reviewing code changes

## Packaging

- Use Poetry for dependency management
- Use `poetry.lock` for locking dependencies

## Style and Format

- Apply code-formatting style defined in `.editorconfig`
- Follow PEP 8 style guide for Python code
- Use `black` for code formatting
- Use quotation `"` marks for strings, not apostrophes `'`

## Code

- Include type hints for all function signatures
- Use absolute imports within the repository
- Group imports as: standard library, third-party, local application
- Prefer explicit exception handling and logging for errors
- Avoid bare `except:` clauses

## Tools

- Use `pytest` for testing
  - Place all tests in a dedicated `tests/` directory
  - Use descriptive test names nad group related tests in modules
- Use `mypy` for type checking
- Use `flake8` for linting

## Change Management

- Always run flake8 after making changes
- Use clear commit messages describing the change (e.g., "Add new AcademicHonorCategoryDescriptor.xml")

---
This file is intended for use by GitHub Copilot and contributors to maintain high-quality Python files in the Ed-Fi-Standard repository.
