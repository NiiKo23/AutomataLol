"""
AutoмataLol - Logger Setup
Configuración de logging con loguru
"""

import logging
from pathlib import Path
from loguru import logger as loguru_logger


LOG_DIR = Path.home() / ".automatalol" / "logs"


def setup_logger(name: str = "AutomataLol", level: str = "INFO", debug: bool = False) -> logging.Logger:
    """
    Configurar logger.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging
        debug: Si está en modo debug
    
    Returns:
        Logger configurado
    """
    # Crear directorio de logs
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Eliminar handlers por defecto
    loguru_logger.remove()
    
    # Configurar nivel
    if debug:
        level = "DEBUG"
    
    # Agregar handler para archivo
    log_file = LOG_DIR / f"{name}.log"
    loguru_logger.add(
        str(log_file),
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 MB",
        retention="7 days",
    )
    
    # Agregar handler para consola
    loguru_logger.add(
        lambda msg: None,  # Dummy handler
        level=level,
        format="<level>{message}</level>",
    )
    
    # Integrar con logging estándar de Python
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(message)s",
        handlers=[logging.StreamHandler()],
    )
    
    return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """
    Obtener logger.
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger
    """
    return logging.getLogger(name)
