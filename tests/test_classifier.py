import pytest

from app.ai.classifier import DocumentClassifier


def test_classifier_structured_source():

    classifier = DocumentClassifier()

    assert (
        classifier.classify("csv")
        == "structured"
    )


def test_classifier_database_source():

    classifier = DocumentClassifier()

    assert (
        classifier.classify("mysql")
        == "database"
    )


def test_classifier_unstructured_source():

    classifier = DocumentClassifier()

    assert (
        classifier.classify("pdf")
        == "unstructured"
    )


def test_classifier_api_source():

    classifier = DocumentClassifier()

    assert (
        classifier.classify("api")
        == "api"
    )


def test_classifier_unknown_source():

    classifier = DocumentClassifier()

    assert (
        classifier.classify("unknown")
        == "unknown"
    )


def test_classifier_rejects_non_string():

    classifier = DocumentClassifier()

    with pytest.raises(TypeError):
        classifier.classify(123)


def test_classifier_rejects_empty_source():

    classifier = DocumentClassifier()

    with pytest.raises(ValueError):
        classifier.classify("   ")