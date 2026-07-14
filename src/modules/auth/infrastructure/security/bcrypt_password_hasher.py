import bcrypt
from src.modules.auth.exceptions import PasswordHasherError
from src.modules.auth.domain.ports.password_hasher_interface import IPasswordHasher
from src.modules.auth.domain.value_objects.password import Password
from src.modules.auth.domain.value_objects.hashed_password import HashedPassword


class BcryptPasswordHasher(IPasswordHasher):

    def hash(self, password: Password) -> HashedPassword:
        try:
            password_bytes = password.value.encode("utf-8")
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

            return HashedPassword(hashed.decode("utf-8"))
        except Exception as e:
            raise PasswordHasherError(
                f"Unexpected error occurred during hashing password:\n{str(e)}"
            ) from e

    def verify(self, plain: Password, hashed: HashedPassword) -> bool:
        try:
            plain_bytes = plain.value.encode("utf-8")
            hashed_bytes = hashed.value.encode("utf-8")
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception as e:
            raise PasswordHasherError(
                f"Unexpected error occurred during verifying password:\n{str(e)}"
            ) from e
