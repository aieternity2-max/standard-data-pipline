from app.main import main


def test_main_no_arguments(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        "sys.argv",
        ["app.main"],
    )

    main()

    captured = capsys.readouterr()

    assert "Standard Data Pipeline" in captured.out
    assert "Usage:" in captured.out
    assert (
        "python -m app.main <file_path>"
        in captured.out
    )


def test_main_unsupported_file(
    monkeypatch,
    capsys,
    tmp_path,
):
    unsupported_file = (
        tmp_path / "sample.xyz"
    )

    unsupported_file.write_text(
        "This is a test file."
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            str(unsupported_file),
        ],
    )

    main()

    captured = capsys.readouterr()

    assert (
        "Unsupported file type: .xyz"
        in captured.out
    )

    assert (
        "Pipeline execution stopped."
        in captured.out
    )


def test_main_nonexistent_file(
    monkeypatch,
    capsys,
    tmp_path,
):
    missing_file = (
        tmp_path / "missing.csv"
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            str(missing_file),
        ],
    )

    main()

    captured = capsys.readouterr()

    assert (
        "CSV file not found"
        in captured.out
    )

    assert (
        "Pipeline execution stopped."
        in captured.out
    )


def test_main_empty_file(
    monkeypatch,
    capsys,
    tmp_path,
):
    empty_file = (
        tmp_path / "empty.csv"
    )

    empty_file.write_text("")

    monkeypatch.setattr(
        "sys.argv",
        [
            "app.main",
            str(empty_file),
        ],
    )

    main()

    captured = capsys.readouterr()

    assert (
        "WARNING: No documents were loaded."
        in captured.out
    )

    assert (
        "Pipeline execution stopped."
        in captured.out
    )