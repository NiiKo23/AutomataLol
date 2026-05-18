"""
AutoмataLol - Helper Functions
Funciones auxiliares útiles
"""

import asyncio
import random
import logging
from pathlib import Path
from typing import Callable, Any, Optional, TypeVar, Coroutine
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def safe_call(func: Callable, *args, **kwargs) -> Any:
    """
    Ejecutar función de forma segura.
    
    Args:
        func: Función a ejecutar
        *args: Argumentos posicionales
        **kwargs: Argumentos nombrados
    
    Returns:
        Resultado o None si hay error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
        return None


def retry_async(max_retries: int = 3, delay: float = 1.0) -> Callable:
    """
    Decorador para reintentar funciones async.
    
    Args:
        max_retries: Máximo de reintentos
        delay: Delay entre reintentos
    
    Returns:
        Función decorada
    """
    def decorator(func: Callable[..., Coroutine]) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.debug(f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise
        
        return wrapper
    
    return decorator


def humanize_delay(base_ms: int, variance_ms: int = 50) -> float:
    """
    Crear delay humanizado.
    
    Args:
        base_ms: Base en milisegundos
        variance_ms: Varianza en milisegundos
    
    Returns:
        Delay en milisegundos
    """
    variance = random.randint(-variance_ms, variance_ms)
    delay = max(0, base_ms + variance)
    return delay / 1000


def get_lol_dir() -> Optional[Path]:
    """
    Obtener directorio de League of Legends.
    
    Returns:
        Path al directorio o None
    """
    common_paths = [
        Path("C:/Riot Games/League of Legends"),
        Path("C:/Program Files/Riot Games/League of Legends"),
        Path("C:/Program Files (x86)/Riot Games/League of Legends"),
        Path.home() / "AppData" / "Local" / "Riot Games" / "League of Legends",
    ]
    
    for path in common_paths:
        if path.exists():
            return path
    
    return None
