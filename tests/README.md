# M8 Kit Creator Test Suite

Comprehensive test suite for M8 Kit Creator modules.

## Running Tests

### Run All Tests

```bash
python run_tests.py
```

### Run Specific Test Module

```bash
python -m unittest tests.test_octatrack_writer
python -m unittest tests.test_utils
python -m unittest tests.test_config
python -m unittest tests.test_audio_processor
```

### Run Specific Test Class

```bash
python -m unittest tests.test_octatrack_writer.TestOctatrackWriter
```

### Run Specific Test Method

```bash
python -m unittest tests.test_octatrack_writer.TestOctatrackWriter.test_file_creation
```

## Test Coverage

### test_octatrack_writer.py (46 tests)
Tests for the Octatrack .ot file writer module:
- File creation and structure validation
- Header magic bytes verification
- Tempo encoding (BPM × 6)
- Slice addition and storage
- Checksum calculation
- Bar length calculation
- Sample rate handling
- Gain encoding
- Edge cases (zero samples, no slices, invalid paths, max slices)

### test_utils.py (23 tests)
Tests for utility functions:
- WAV file validation (extension, existence, headers)
- Channel count validation
- Sample rate validation
- Sample width validation
- Channel description formatting
- Error message formatting
- Directory write permission checking

### test_config.py (25 tests)
Tests for configuration constants:
- UI configuration (window size, fonts, padding)
- Audio processing parameters
- File handling settings
- Output format constants
- Message templates
- Configuration consistency checks

### test_audio_processor.py (9 tests)
Tests for audio processor module structure:
- Module imports (with graceful handling of missing tkinter)
- Class initialization and parameters
- Method signatures
- Documentation completeness

**Note:** Most audio processor tests are skipped in environments without tkinter/pydub, but verify the module structure is correct.

## Test Results

```
Ran 71 tests in 0.037s
OK (skipped=10)
```

- **71 total tests**
- **61 passing**
- **10 skipped** (require tkinter/pydub which aren't available in all environments)
- **0 failures**
- **0 errors**

## Test Dependencies

The test suite uses only Python standard library modules:
- `unittest` - Test framework
- `tempfile` - Temporary file/directory creation
- `struct` - Binary data parsing
- `wave` - WAV file creation for test fixtures

No external dependencies are required to run the tests!

## Adding New Tests

1. Create a new test file in `tests/` directory named `test_<module>.py`
2. Import unittest and the module to test
3. Create test classes inheriting from `unittest.TestCase`
4. Add test methods starting with `test_`
5. Run `python run_tests.py` to verify

Example:
```python
import unittest
from m8_kitcreator.new_module import NewClass

class TestNewClass(unittest.TestCase):
    def test_something(self):
        obj = NewClass()
        self.assertTrue(obj.some_method())
```

## Continuous Integration

This test suite is designed to run in CI/CD pipelines:
```bash
# Exit with code 0 if all tests pass, 1 if any fail
python run_tests.py
```

## Notes

- Tests automatically create and clean up temporary files
- Tests are isolated and can run in any order
- Skipped tests are expected for modules requiring GUI libraries
- All tests use assertions for clear failure messages
