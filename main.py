from app.database import initialize_database


def main() -> None:
    initialize_database()
    print("Pixiv Local Manager started.")


if __name__ == "__main__":
    main()
