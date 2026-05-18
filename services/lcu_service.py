"""
AutoмataLol - LCU Service
Orquestador principal del cliente LCU
"""

import asyncio
import logging
from typing import Optional
from enum import Enum

from api import get_lcu_client, get_lcu_event_handler, LCUConnectionError
from core.events import get_event_bus, EventType
from core.exceptions import LCUServiceError

logger = logging.getLogger(__name__)


class LCUServiceState(str, Enum):
    """Estados del servicio LCU"""
    STOPPED = "stopped"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class LCUService:
    """Servicio de orquestación LCU"""
    
    def __init__(self, max_retries: int = 10, retry_delay: float = 2.0):
        """
        Inicializar servicio LCU.
        
        Args:
            max_retries: Máximo de reintentos de conexión
            retry_delay: Delay entre reintentos en segundos
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.state = LCUServiceState.STOPPED
        self.lcu_client = get_lcu_client()
        self.event_handler = None
        self.event_bus = get_event_bus()
        
        self._running = False
        self._retry_count = 0
        self._connection_task = None
    
    async def start(self) -> bool:
        """
        Iniciar servicio LCU.
        
        Returns:
            True si fue exitoso
        """
        if self._running:
            logger.warning("LCU Service already running")
            return True
        
        self._running = True
        self.state = LCUServiceState.CONNECTING
        
        logger.info("Starting LCU Service...")
        
        try:
            await self.event_bus.emit_async(
                EventType.LCU_SERVICE_STARTING,
                source="LCUService"
            )
            
            # Conectar al cliente LCU
            if not await self.lcu_client.connect():
                raise LCUConnectionError("Could not connect to LCU Client")
            
            logger.info("✅ LCU Client connected")
            
            # Inicializar event handler
            self.event_handler = get_lcu_event_handler(self.lcu_client)
            await self.event_handler.start()
            
            logger.info("✅ LCU Event handler started")
            
            self.state = LCUServiceState.CONNECTED
            self._retry_count = 0
            
            await self.event_bus.emit_async(
                EventType.LCU_SERVICE_READY,
                source="LCUService"
            )
            
            logger.info("🎉 LCU Service ready!")
            return True
        
        except Exception as e:
            logger.error(f"Failed to start LCU Service: {e}", exc_info=True)
            self.state = LCUServiceState.FAILED
            
            await self.event_bus.emit_async(
                EventType.LCU_SERVICE_FAILED,
                data={"error": str(e)},
                source="LCUService"
            )
            
            self._running = False
            return False
    
    async def stop(self) -> None:
        """
        Detener servicio LCU.
        """
        if not self._running:
            return
        
        self._running = False
        self.state = LCUServiceState.STOPPED
        
        logger.info("Stopping LCU Service...")
        
        try:
            if self.event_handler:
                await self.event_handler.stop()
            
            await self.lcu_client.disconnect()
            
            await self.event_bus.emit_async(
                EventType.LCU_SERVICE_STOPPED,
                source="LCUService"
            )
            
            logger.info("✅ LCU Service stopped")
        
        except Exception as e:
            logger.error(f"Error stopping LCU Service: {e}", exc_info=True)
    
    async def reconnect(self) -> bool:
        """
        Reconectar al cliente LCU.
        
        Returns:
            True si fue exitoso
        """
        logger.warning("Attempting to reconnect to LCU...")
        self.state = LCUServiceState.RECONNECTING
        
        await self.event_bus.emit_async(
            EventType.LCU_SERVICE_RECONNECTING,
            source="LCUService"
        )
        
        for attempt in range(self.max_retries):
            try:
                await asyncio.sleep(self.retry_delay)
                
                if await self.lcu_client.connect():
                    logger.info(f"✅ Reconnected after {attempt + 1} attempts")
                    self.state = LCUServiceState.CONNECTED
                    self._retry_count = 0
                    
                    await self.event_bus.emit_async(
                        EventType.LCU_SERVICE_READY,
                        source="LCUService"
                    )
                    
                    return True
            
            except Exception as e:
                logger.debug(f"Reconnection attempt {attempt + 1} failed: {e}")
        
        logger.error(f"Failed to reconnect after {self.max_retries} attempts")
        self.state = LCUServiceState.FAILED
        
        await self.event_bus.emit_async(
            EventType.LCU_SERVICE_FAILED,
            data={"error": "Max reconnection attempts exceeded"},
            source="LCUService"
        )
        
        return False
    
    def get_state(self) -> LCUServiceState:
        """Obtener estado actual del servicio"""
        return self.state
    
    def is_connected(self) -> bool:
        """Verificar si está conectado"""
        return self.state == LCUServiceState.CONNECTED


# Instancia global
_lcu_service: Optional[LCUService] = None


def get_lcu_service() -> LCUService:
    """Obtener instancia global del servicio LCU"""
    global _lcu_service
    if _lcu_service is None:
        _lcu_service = LCUService()
    return _lcu_service


lcu_service = get_lcu_service()
