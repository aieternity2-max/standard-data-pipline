from app.validation.data_quality import (
    DataQualityValidator,
)


def test_required_fields():

    validator = DataQualityValidator(
        required_fields=[
            "customer_id",
            "name",
        ]
    )

    record = {
        "customer_id": 101,
        "name": "Alice",
    }

    result = validator.validate_record(record)

    assert result.is_valid is True

    assert result.errors == []


def test_missing_required_field():

    validator = DataQualityValidator(
        required_fields=[
            "customer_id",
            "name",
        ]
    )

    record = {
        "customer_id": 101,
    }

    result = validator.validate_record(record)

    assert result.is_valid is False

    assert (
        "Required field missing: name"
        in result.errors
    )


def test_empty_required_field():

    validator = DataQualityValidator(
        required_fields=[
            "customer_id",
            "name",
        ]
    )

    record = {
        "customer_id": 101,
        "name": "",
    }

    result = validator.validate_record(record)

    assert result.is_valid is False

    assert (
        "Required field is empty: name"
        in result.errors
    )


def test_data_type_validation():

    validator = DataQualityValidator(
        field_types={
            "customer_id": int,
            "age": int,
        }
    )

    record = {
        "customer_id": "101",
        "age": 30,
    }

    result = validator.validate_record(record)

    assert result.is_valid is False

    assert (
        "Invalid type for customer_id"
        in result.errors[0]
    )


def test_allowed_values():

    validator = DataQualityValidator(
        allowed_values={
            "status": {
                "active",
                "inactive",
            }
        }
    )

    record = {
        "status": "deleted",
    }

    result = validator.validate_record(record)

    assert result.is_valid is False

    assert (
        "Invalid value for status: deleted"
        in result.errors
    )


def test_valid_allowed_value():

    validator = DataQualityValidator(
        allowed_values={
            "status": {
                "active",
                "inactive",
            }
        }
    )

    record = {
        "status": "active",
    }

    result = validator.validate_record(record)

    assert result.is_valid is True


def test_find_duplicates():

    validator = DataQualityValidator()

    records = [
        {
            "customer_id": 101,
            "name": "Alice",
        },
        {
            "customer_id": 102,
            "name": "Bob",
        },
        {
            "customer_id": 101,
            "name": "Alice",
        },
    ]

    duplicates = validator.find_duplicates(
        records,
        key_fields=["customer_id"],
    )

    assert len(duplicates) == 1

    assert duplicates[0]["customer_id"] == 101


def test_validate_multiple_records():

    validator = DataQualityValidator(
        required_fields=[
            "customer_id",
        ]
    )

    records = [
        {
            "customer_id": 101,
        },
        {
            "customer_id": 102,
        },
    ]

    results = validator.validate_records(
        records
    )

    assert len(results) == 2

    assert all(
        result.is_valid
        for result in results
    )