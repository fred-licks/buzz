# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build & Dependencies
- `poetry install` - Install dependencies
- `make clean` - Clean build artifacts and temporary files
- `make buzz/whisper_cpp.py` - Build whisper.cpp bindings and generate Python wrapper
- `make translation_mo` - Compile translation files (.po to .mo)

### Testing
- `pytest -s -vv --cov=buzz --cov-report=xml --cov-report=html --benchmark-skip --cov-fail-under=75 --cov-config=.coveragerc` - Run tests with coverage (75% minimum)
- `pytest -s -vv --benchmark-only --benchmark-json benchmarks.json` - Run performance benchmarks only
- Test files are in `tests/` directory

### Linting & Formatting
- `ruff check . --fix` - Run linter and auto-fix issues
- `ruff format .` - Format code
- Pre-commit hooks configured with ruff for automatic formatting

### Build Distributions
- `pyinstaller --noconfirm Buzz.spec` - Create executable distribution
- `make bundle_windows` - Bundle Windows installer
- `make bundle_mac` - Bundle macOS app with signing
- `make bundle_mac_unsigned` - Bundle unsigned macOS app

## Architecture

Buzz is a desktop audio transcription application using OpenAI's Whisper model, built with PyQt6 and Python.

### Core Components

**Transcription Engine** (`buzz/transcriber/`):
- `transcriber.py` - Base transcription classes and data structures (Segment, TranscriptionOptions)
- `whisper_cpp_file_transcriber.py` - whisper.cpp implementation for file transcription
- `whisper_file_transcriber.py` - OpenAI Whisper Python implementation
- `openai_whisper_api_file_transcriber.py` - OpenAI API integration
- `recording_transcriber.py` - Real-time audio recording transcription

**GUI Application** (`buzz/widgets/`):
- `main_window.py` - Primary application window
- `application.py` - PyQt6 application setup and lifecycle
- Widget classes for UI components (dialogs, controls, audio player)

**Data Layer** (`buzz/db/`):
- `dao/` - Data Access Objects for transcriptions and segments
- `entity/` - Database entity models
- `service/` - Business logic layer

**Audio Processing**:
- Integration with whisper.cpp (C++ library) via ctypes bindings
- Support for multiple Whisper model variants (tiny, base, small, medium, large)
- Real-time audio capture and processing

### Key Files
- `buzz/buzz.py` - Main application entry point, handles multiprocessing and logging setup
- `buzz/cli.py` - Command-line interface
- `build.py` - Custom build script for Poetry
- `Buzz.spec` - PyInstaller specification for creating executables

### Whisper.cpp Integration
The app compiles whisper.cpp from source using CMake and generates Python bindings with ctypesgen:
- `whisper.cpp/` - Git submodule containing whisper.cpp C++ library
- Build process creates `buzz/whisper_cpp.py` wrapper from `whisper.cpp/whisper.h`
- Platform-specific library files: `.dll` (Windows), `.dylib` (macOS), `.so` (Linux)

### Internationalization
- Translation files in `buzz/locale/{locale}/LC_MESSAGES/`
- Source strings marked with `_()` function from `buzz.locale`
- Makefile targets for updating translations: `translation_po_all`, `translation_mo`

### Configuration
- Uses Poetry for dependency management with CUDA/GPU support
- PyQt6 for cross-platform GUI
- Pre-commit hooks for code quality
- Platform-specific build configurations in Makefile