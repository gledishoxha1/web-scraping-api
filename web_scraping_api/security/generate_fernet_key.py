"""
Generate a valid Fernet key for use in .env as SECRET_KEY.
"""

from cryptography.fernet import Fernet


def main() -> None:
    key = Fernet.generate_key().decode()
    print("SECRET_KEY=" + key)


if __name__ == "__main__":
    main()
