"""
AutomataLol - Auto Runes Module
Importa runas automáticamente desde múltiples fuentes
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Tuple
import json
from enum import Enum

from core.events import get_event_bus, EventType
from core.exceptions import AutoRunesFailed, RuneImportFailed
from core.constants import DELAY_AUTO_PICK
from api.client import get_lcu_client

logger = logging.getLogger(__name__)


class RuneSource(str, Enum):
    """Fuentes de runas soportadas"""
    OPGG = "opgg"
    UGG = "ugg"
    POROFESSOR = "porofessor"
    MOBALYTICS = "mobalytics"
    CUSTOM = "custom"


class RunePreset:
    """Preset de runas"""
    
    def __init__(
        self,
        name: str,
        primary_style: int,
        sub_style: int,
        primary_perks: List[int],
        sub_perks: List[int],
        shards: List[int],
    ):
        """
        Inicializar preset de runas.
        
        Args:
            name: Nombre del preset
            primary_style: ID del árbol primario
            sub_style: ID del árbol secundario
            primary_perks: IDs de runas primarias (4)
            sub_perks: IDs de runas secundarias (2)
            shards: IDs de shards (3)
        """
        self.name = name
        self.primary_style = primary_style
        self.sub_style = sub_style
        self.primary_perks = primary_perks
        self.sub_perks = sub_perks
        self.shards = shards
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "name": self.name,
            "primaryStyleId": self.primary_style,
            "subStyleId": self.sub_style,
            "selectedPerkIds": self.primary_perks + self.sub_perks + self.shards,
        }


class AutoRunes:
    """Módulo para auto runas"""
    
    # Mapeo de estilos de runas
    RUNE_STYLES = {
        "precision": 8000,
        "domination": 8100,
        "sorcery": 8200,
        "resolve": 8400,
        "inspiration": 8300,
    }
    
    # Presets predefinidos (ejemplo)
    PRESETS = {
        "Ahri_default": RunePreset(
            name="Ahri Default",
            primary_style=8200,  # Sorcery
            sub_style=8000,  # Precision
            primary_perks=[8212, 8214, 8210, 8236],  # Electrocute, cheap shot, eyeball, treasure hunter
            sub_perks=[8005, 8017],  # Precision secondary
            shards=[5005, 5008, 5002],  # Adaptive, Adaptive, Armor
        ),
        "Yasuo_default": RunePreset(
            name="Yasuo Default",
            primary_style=8000,  # Precision
            sub_style=8200,  # Sorcery
            primary_perks=[8005, 8008, 8014, 8017],  # Fleet Footwork, Triumph, Legend Tenacity, Coup de Grace
            sub_perks=[8210, 8214],  # Sorcery secondary
            shards=[5005, 5008, 5002],
        ),
    }
    
    def __init__(
        self,
        enabled: bool = True,
        auto_import: bool = True,
        preferred_source: RuneSource = RuneSource.OPGG,
    ):
        """
        Inicializar AutoRunes.
        
        Args:
            enabled: Si está habilitado
            auto_import: Importar runas automáticamente
            preferred_source: Fuente preferida de runas
        """
        self.enabled = enabled
        self.auto_import = auto_import
        self.preferred_source = preferred_source
        
        self.event_bus = get_event_bus()
        self.lcu_client = get_lcu_client()
        
        self._running = False
        self._subscription = None
        self._cache: Dict[str, RunePreset] = {}
        
        # Cargar presets predefinidos
        self._cache.update(self.PRESETS)
    
    async def enable(self) -> None:
        """Habilitar auto runes"""
        if self.enabled:
            return
        
        self.enabled = True
        logger.info("Auto Runes enabled")
        
        await self.event_bus.emit_async(
            EventType.AUTO_RUNES_ENABLED,
            source="AutoRunes"
        )
        
        self._subscribe()
    
    async def disable(self) -> None:
        """Deshabilitar auto runes"""
        if not self.enabled:
            return
        
        self.enabled = False
        logger.info("Auto Runes disabled")
        
        await self.event_bus.emit_async(
            EventType.AUTO_RUNES_DISABLED,
            source="AutoRunes"
        )
        
        self._unsubscribe()
    
    def _subscribe(self) -> None:
        """Suscribirse a eventos"""
        if self._subscription or not self.auto_import:
            return
        
        self._subscription = self.event_bus.subscribe(
            EventType.CHAMP_SELECT_START,
            lambda event: asyncio.create_task(self.run(event)),
            async_handler=True,
        )
    
    def _unsubscribe(self) -> None:
        """Desuscribirse"""
        if self._subscription:
            self._subscription()
            self._subscription = None
    
    async def run(self, event: Optional[Any] = None) -> bool:
        """
        Ejecutar auto runes.
        
        Returns:
            True si fue exitoso
        """
        if not self.enabled or not self.auto_import:
            return False
        
        if self._running:
            return False
        
        self._running = True
        
        try:
            logger.info("Auto Runes started")
            
            # Obtener sesión
            try:
                session = await self.lcu_client.get("/lol-champ-select/v1/session")
            except Exception as e:
                logger.warning(f"Could not fetch session: {e}")
                return False
            
            # Obtener campeón seleccionado
            champion = self._get_selected_champion(session)
            if not champion:
                logger.debug("No champion selected yet")
                return False
            
            # Obtener preset de runas
            preset = await self._get_rune_preset(champion)
            if not preset:
                logger.warning(f"No rune preset found for {champion}")
                return False
            
            logger.info(f"Found rune preset for {champion}: {preset.name}")
            
            # Delay antes de importar
            await asyncio.sleep(DELAY_AUTO_PICK / 1000)
            
            # Importar runas
            success = await self._import_runes(preset)
            if success:
                logger.info(f"Successfully imported runes: {preset.name}")
                
                await self.event_bus.emit_async(
                    EventType.AUTO_RUNES_EXECUTED,
                    data={
                        "champion": champion,
                        "preset": preset.name,
                        "source": self.preferred_source.value,
                    },
                    source="AutoRunes"
                )
                
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Auto Runes failed: {e}", exc_info=True)
            
            await self.event_bus.emit_async(
                EventType.AUTOMATION_FAILED,
                data={"module": "AutoRunes", "error": str(e)},
                source="AutoRunes"
            )
            
            raise AutoRunesFailed(str(e))
        
        finally:
            self._running = False
    
    async def _get_rune_preset(self, champion: str) -> Optional[RunePreset]:
        """
        Obtener preset de runas para un campeón.
        
        Returns:
            Preset o None
        """
        # Buscar en cache
        cache_key = f"{champion}_default"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Intentar obtener de fuente externa
        preset = await self._fetch_from_external_source(champion)
        if preset:
            self._cache[cache_key] = preset
            return preset
        
        # Usar preset por defecto
        default_key = f"{champion}_default"
        if default_key in self.PRESETS:
            return self.PRESETS[default_key]
        
        logger.warning(f"No rune preset available for {champion}")
        return None
    
    async def _fetch_from_external_source(self, champion: str) -> Optional[RunePreset]:
        """
        Obtener preset desde fuente externa.
        
        Returns:
            Preset o None
        """
        try:
            if self.preferred_source == RuneSource.OPGG:
                return await self._fetch_from_opgg(champion)
            elif self.preferred_source == RuneSource.UGG:
                return await self._fetch_from_ugg(champion)
            elif self.preferred_source == RuneSource.POROFESSOR:
                return await self._fetch_from_porofessor(champion)
            elif self.preferred_source == RuneSource.MOBALYTICS:
                return await self._fetch_from_mobalytics(champion)
        
        except Exception as e:
            logger.warning(f"Failed to fetch from {self.preferred_source}: {e}")
        
        return None
    
    async def _fetch_from_opgg(self, champion: str) -> Optional[RunePreset]:
        """Obtener runas desde OP.GG"""
        logger.debug(f"Fetching runes from OP.GG for {champion}")
        # TODO: Implementar scraping/API de OP.GG
        return None
    
    async def _fetch_from_ugg(self, champion: str) -> Optional[RunePreset]:
        """Obtener runas desde U.GG"""
        logger.debug(f"Fetching runes from U.GG for {champion}")
        # TODO: Implementar scraping/API de U.GG
        return None
    
    async def _fetch_from_porofessor(self, champion: str) -> Optional[RunePreset]:
        """Obtener runas desde Porofessor"""
        logger.debug(f"Fetching runes from Porofessor for {champion}")
        # TODO: Implementar scraping/API de Porofessor
        return None
    
    async def _fetch_from_mobalytics(self, champion: str) -> Optional[RunePreset]:
        """Obtener runas desde Mobalytics"""
        logger.debug(f"Fetching runes from Mobalytics for {champion}")
        # TODO: Implementar scraping/API de Mobalytics
        return None
    
    async def _import_runes(self, preset: RunePreset) -> bool:
        """
        Importar runas en el cliente.
        
        Returns:
            True si fue exitoso
        """
        try:
            await self.lcu_client.post(
                "/lol-perks/v1/pages",
                data=preset.to_dict()
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to import runes: {e}")
            raise RuneImportFailed(str(e))
    
    def _get_selected_champion(self, session: Dict[str, Any]) -> Optional[str]:
        """Obtener campeón seleccionado"""
        my_team = session.get("myTeam", [])
        my_summoner_id = session.get("mySummonerId")
        
        for member in my_team:
            if member.get("summonerId") == my_summoner_id:
                return member.get("championPickName")
        
        return None
    
    def add_preset(self, champion: str, preset: RunePreset) -> None:
        """Agregar preset personalizado"""
        key = f"{champion}_{preset.name}".lower()
        self._cache[key] = preset
        logger.info(f"Added rune preset: {key}")
    
    def set_source(self, source: RuneSource) -> None:
        """Cambiar fuente de runas"""
        self.preferred_source = source
        logger.info(f"Rune source changed to: {source.value}")
    
    def export_preset(self, champion: str) -> Optional[Dict[str, Any]]:
        """Exportar preset de runas"""
        key = f"{champion}_default"
        if key in self._cache:
            return self._cache[key].to_dict()
        return None


# Instancia global
_auto_runes: Optional[AutoRunes] = None


def get_auto_runes() -> AutoRunes:
    """Obtener instancia global"""
    global _auto_runes
    if _auto_runes is None:
        _auto_runes = AutoRunes()
    return _auto_runes


auto_runes = get_auto_runes()
