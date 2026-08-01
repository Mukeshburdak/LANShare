import hashlib


def calculate_checksum(filepath):
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:
        while True:
            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def verify_checksum(filepath, checksum):
    return calculate_checksum(filepath) == checksum
