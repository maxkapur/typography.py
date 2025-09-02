import pytest

import typography


@pytest.mark.parametrize(
    "before,after,count",
    [
        # Contractions
        ("this can't be right", "this can’t be right", 1),
        ("could've been", "could’ve been", 1),
        ("he's cooking", "he’s cooking", 1),
        ("I'd rather not", "I’d rather not", 1),
        ("what'll it take", "what’ll it take", 1),
        (" I'm livid", " I’m livid", 1),
        ("yes ma'am", "yes ma’am", 1),
        ("Yes, Ma'am.", "Yes, Ma’am.", 1),
        ("thirteen o'clock", "thirteen o’clock", 1),
        # Spelling
        ("Hawaii", "Hawaiʻi", 1),
        # Punctuation
        ("One way--to em dash", "One way—to em dash", 1),
        ("Another---way", "Another—way", 1),
        ("Range: 25-28", "Range: 25–28", 1),
        ("2025-01-01", "2025-01-01", 0),
        ('Time for "curly quotes"', "Time for “curly quotes”", 2),
        ("Trailing whitespace    ", "Trailing whitespace", 1),
        ("Trailing whitespace    \n\n", "Trailing whitespace\n\n", 1),
        ("Trailing \n  whitespace\t\n", "Trailing\n  whitespace\n", 2),
        # Multiple issues
        # Long example
    ],
)
def test_apply_count_issues(before: str, after: str, count: int) -> None:
    after_res, count_res = typography.apply_count_issues(before)
    assert after_res == after
    assert count_res == count

    # Idempotence. No guarantee that this property holds for all inputs, but it
    # should for the stylized test examples
    after_res_again, count_res_again = typography.apply_count_issues(after)
    assert after_res_again == after
    assert count_res_again == 0
