from app.config.settings import settings


def main() -> None:
    print("=" * 50)
    print(settings.app_name)
    print(f"Environment: {settings.environment}")
    print("Python engine initialized successfully")
    print("=" * 50)


if __name__ == "__main__":
    main()