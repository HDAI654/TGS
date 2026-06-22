import nanoid


class IDGenerationError(Exception):
    """Raised when the IDGenerator.generate() had error"""

    pass


class IDGenerator:
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    LENGTH = 14

    @staticmethod
    def generate() -> str:
        try:
            return nanoid.generate(IDGenerator.ALPHABET, IDGenerator.LENGTH)
        except Exception as e:
            raise IDGenerationError(
                f"Unexpected error occurred during ID generation:\n{str(e)}"
            ) from e
