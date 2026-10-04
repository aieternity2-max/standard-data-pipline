from sqlalchemy import text

from app.storage.sql_storage import SQLStorage


def main():
    print("=" * 60)
    print("SQL DATABASE VERIFICATION")
    print("=" * 60)

    storage = SQLStorage()

    # -----------------------------------------
    # 1. Test database connection
    # -----------------------------------------

    if storage.test_connection():
        print("Database connection: SUCCESS")
    else:
        print("Database connection: FAILED")
        return

    # -----------------------------------------
    # 2. Check documents table
    # -----------------------------------------

    try:
        with storage.engine.connect() as connection:

            result = connection.execute(
                text(
                    "SELECT COUNT(*) FROM employee"
                )
            )

            count = result.scalar()

            print(f"Stored employee: {count}")

            # -----------------------------------------
            # 3. Display sample records
            # -----------------------------------------

            result = connection.execute(
                text(
                    """
                    SELECT
                        EMPID,
                        EMP_NAME,
                        AGE,
                        DOJ,
                        Email,
                        Bill_Pay,
                        LOCATION,
                        GENDER,
                        DEPARTMENT 
                    FROM employee
                    ORDER BY EMPID
                    LIMIT 5
                    """
                )
            )

            rows = result.fetchall()

            print("\nSample records:")

            for row in rows:
                  print("-" * 60)
                  print(f"Employee ID : {row.EMPID}")
                  print(f"Name        : {row.EMP_NAME}")
                  print(f"Age         : {row.AGE}")
                  print(f"DOJ         : {row.DOJ}")
                  print(f"Email       : {row.Email}")
                  print(f"Bill Pay    : {row.Bill_Pay}")
                  print(f"Location    : {row.LOCATION}")
                  print(f"Gender      : {row.GENDER}")
                  print(f"Department  : {row.DEPARTMENT}")

    except Exception as error:

        print("\nSQL verification failed:")
        print(error)


if __name__ == "__main__":
    main()