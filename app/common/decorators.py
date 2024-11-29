import asyncio
import functools
import logging
from typing import Callable, Any

def async_retry(max_retries: int = 5, delay: float = 1.0, backoff: float = 2.0):
    """
    Async decorator that retries a function if it raises an exception.
    
    Args:
        max_retries (int): Maximum number of retry attempts. Defaults to 5.
        delay (float): Initial delay between retries in seconds. Defaults to 1 second.
        backoff (float): Multiplier for increasing delay between retries. Defaults to 2.
    
    Returns:
        Decorator function that adds retry logic to the decorated async function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    
                    logging.warning(
                        f"Attempt {retries}/{max_retries} failed for {func.__name__}. "
                        f"Error: {type(e).__name__} - {str(e)}"
                    )
                    
                    if retries == max_retries:
                        logging.error(
                            f"All {max_retries} attempts failed for {func.__name__}. "
                            "Raising final exception."
                        )
                        raise
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            # This line should never be reached, but added for type checking
            raise RuntimeError(f"Unexpected error in retry mechanism for {func.__name__}")
        
        return wrapper
    
    return decorator
