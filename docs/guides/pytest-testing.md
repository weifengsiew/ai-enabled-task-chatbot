# Testing in Python with `pytest`

A useful test suite checks software at different levels. The three common levels are **unit tests**, **integration tests**, and **end-to-end (E2E) tests**. The main difference is scope: a unit test checks one small behavior, an integration test checks multiple pieces working together, and an E2E test checks a complete workflow from input to final output.

The examples below all use the same small **data-cleaning application** so the difference between the test types is easy to see. They are designed to be copied into files and run with `pytest`.

## Setup

Use this layout:

```text
data-cleaning-example/
├── cleaner.py
└── test_cleaner.py
```

Install the only dependencies:

```bash
python -m pip install pytest pandas
```

Put the following application code in `cleaner.py`:

```python
from pathlib import Path

import pandas as pd


class DataCleaner:
    """Clean a small customer dataset."""

    def clean_name(self, value: str) -> str:
        return value.strip().title()

    def clean_age(self, value) -> int:
        return int(str(value).strip())

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        cleaned = df.copy()
        cleaned["name"] = cleaned["name"].apply(self.clean_name)
        cleaned["age"] = cleaned["age"].apply(self.clean_age)
        return cleaned

    def clean_file(self, input_path: Path, output_path: Path) -> None:
        df = pd.read_csv(input_path)
        cleaned = self.clean_dataframe(df)
        cleaned.to_csv(output_path, index=False)
```

---

## 1. Unit tests

A **unit test** checks one small piece of behavior in isolation. For data cleaning, that might mean testing a single rule such as trimming whitespace, normalizing capitalization, or converting a value to the expected type.

Unit tests should normally be fast and focused. When one fails, it should be obvious which cleaning rule is incorrect.

Add these tests to `test_cleaner.py`:

```python
import pytest

from cleaner import DataCleaner


@pytest.mark.parametrize(
    ("actual_input", "expected_output"),
    [
        (" alice ", "Alice"),
        ("BOB", "Bob"),
        ("  mary jane  ", "Mary Jane"),
    ],
)
def test_clean_name(actual_input, expected_output):
    cleaner = DataCleaner()

    actual_output = cleaner.clean_name(actual_input)

    assert actual_output == expected_output


def test_clean_age():
    cleaner = DataCleaner()

    assert cleaner.clean_age(" 25 ") == 25
```

`pytest.mark.parametrize` is useful for cleaning functions because the same rule often needs to be checked against many input values. Instead of writing a separate test function for every name, pytest runs the same test once for each `(actual_input, expected_output)` pair.

---

## 2. Integration tests

An **integration test** checks that multiple parts of the program work together. Here, `clean_dataframe()` combines the individual name and age cleaning methods with a real pandas `DataFrame`.

This test is broader than the unit tests: it verifies that the cleaning rules are correctly applied to the appropriate DataFrame columns and that the resulting table has the expected values.

Add this test to `test_cleaner.py`:

```python
import pandas as pd
from pandas.testing import assert_frame_equal


def test_clean_dataframe():
    cleaner = DataCleaner()

    actual_input = pd.DataFrame(
        {
            "name": [" alice smith ", "BOB"],
            "age": [" 25 ", "30"],
        }
    )

    expected_output = pd.DataFrame(
        {
            "name": ["Alice Smith", "Bob"],
            "age": [25, 30],
        }
    )

    actual_output = cleaner.clean_dataframe(actual_input)

    assert_frame_equal(actual_output, expected_output)
```

For pandas objects, `pandas.testing.assert_frame_equal` is preferable to several individual `assert` statements because it compares the DataFrames and reports useful details when rows, columns, values, or dtypes differ.

---

## 3. End-to-end tests

An **end-to-end test** checks the complete workflow through the program. In this example, the real workflow is:

**raw CSV file → pandas DataFrame → cleaning logic → cleaned CSV file**

The test therefore starts with an actual input file and checks the final output file rather than calling the lower-level cleaning methods directly.

Add this test to `test_cleaner.py`:

```python
def test_clean_file_end_to_end(tmp_path):
    input_file = tmp_path / "raw.csv"
    output_file = tmp_path / "clean.csv"

    input_file.write_text(
        "name,age\n alice smith , 25 \nBOB,30\n",
        encoding="utf-8",
    )

    cleaner = DataCleaner()
    cleaner.clean_file(input_file, output_file)

    actual_output = pd.read_csv(output_file)
    expected_output = pd.DataFrame(
        {
            "name": ["Alice Smith", "Bob"],
            "age": [25, 30],
        }
    )

    assert output_file.exists()
    assert_frame_equal(actual_output, expected_output)
```

`tmp_path` is a built-in pytest fixture that provides a unique temporary directory for a test. It is well suited to file-processing tests because the test can create real files without writing permanent test files into the project.

---

## Comparing the three test levels

| Test type | What this example tests | Scope |
|---|---|---|
| Unit | `clean_name()` and `clean_age()` | One cleaning rule |
| Integration | `clean_dataframe()` | Cleaning rules + pandas DataFrame |
| End-to-end | `clean_file()` | CSV input → cleaning → CSV output |

A project will usually contain many unit tests, fewer integration tests, and a smaller number of E2E tests for important workflows. The categories are not defined by the name of the test file; they are defined by **how much of the system the test exercises**.

## Run the tests

From the directory containing `cleaner.py` and `test_cleaner.py`, run:

```bash
pytest -v
```

With the code above, pytest should collect **6 test cases**: four parameterized/unit cases, one integration test, and one E2E test.

## References

- [pytest: Get Started](https://docs.pytest.org/en/stable/getting-started.html)
- [pytest: Parametrizing tests](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest: Temporary directories and files (`tmp_path`)](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- [pandas: Testing utilities](https://pandas.pydata.org/docs/reference/testing.html)
- [pandas: `assert_frame_equal`](https://pandas.pydata.org/docs/reference/api/pandas.testing.assert_frame_equal.html)
