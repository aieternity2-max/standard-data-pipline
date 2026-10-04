from app.processors.cleaner import DocumentCleaner


def test_document_cleaner():

    cleaner = DocumentCleaner()

    text = """
        Hello     World


        This is     a test.
    """

    result = cleaner.clean(text)

    assert result == (
        "Hello World\n\n"
        "This is a test."
    )