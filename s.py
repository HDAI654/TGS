from functools import wraps


def error_handler(func):
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper


@error_handler
async def create_country(
    self,
    country_code: str,
    country_name: str,
    capital: str,
) -> str:
    return f"{country_code}: {country_name}"


# ✅ inspect.signature shows the ORIGINAL parameters!
import inspect

print(inspect.signature(create_country))
