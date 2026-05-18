"""
AutoмataLol - Config Service
Manejo de configuración persistente
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


CONFIG_DIR = Path.home() / ".automatalol"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class AutoAcceptConfig:
    """Configuración de Auto Accept"""
    enabled: bool = True
    delay_ms: int = 50
    humanize_delay: bool = True


@dataclass
class AutoBanConfig:
    """Configuración de Auto Ban"""
    enabled: bool = True
    primary_bans: List[str] = field(default_factory=lambda: ["Yasuo", "Zed", "Ahri"])
    secondary_bans: List[str] = field(default_factory=lambda: ["Sylas"])
    fallback_bans: List[str] = field(default_factory=list)
    delay_ms: int = 100


@dataclass
class AutoPickConfig:
    """Configuración de Auto Pick"""
    enabled: bool = True
    champion: str = "Ahri"
    fallback_picks: List[str] = field(default_factory=lambda: ["Annie", "Lux"])
    delay_ms: int = 50
    safe_mode: bool = True


@dataclass
class AutoRunesConfig:
    """Configuración de Auto Runes"""
    enabled: bool = True
    auto_import: bool = True
    preferred_source: str = "opgg"


@dataclass
class AutoSummonerConfig:
    """Configuración de Auto Summoner Spells"""
    enabled: bool = True
    auto_assign: bool = True


@dataclass
class AppConfig:
    """Configuración general de la aplicación"""
    app_name: str = "AutomataLol"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    auto_accept: AutoAcceptConfig = field(default_factory=AutoAcceptConfig)
    auto_ban: AutoBanConfig = field(default_factory=AutoBanConfig)
    auto_pick: AutoPickConfig = field(default_factory=AutoPickConfig)
    auto_runes: AutoRunesConfig = field(default_factory=AutoRunesConfig)
    auto_summoner: AutoSummonerConfig = field(default_factory=AutoSummonerConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AppConfig':
        """Crear desde diccionario"""
        config = AppConfig()
        
        if "app_name" in data:
            config.app_name = data["app_name"]
        if "version" in data:
            config.version = data["version"]
        if "debug" in data:
            config.debug = data["debug"]
        if "log_level" in data:
            config.log_level = data["log_level"]
        
        if "auto_accept" in data:
            config.auto_accept = AutoAcceptConfig(**data["auto_accept"])
        if "auto_ban" in data:
            config.auto_ban = AutoBanConfig(**data["auto_ban"])
        if "auto_pick" in data:
            config.auto_pick = AutoPickConfig(**data["auto_pick"])
        if "auto_runes" in data:
            config.auto_runes = AutoRunesConfig(**data["auto_runes"])
        if "auto_summoner" in data:
            config.auto_summoner = AutoSummonerConfig(**data["auto_summoner"])
        
        return config


class ConfigService:
    """Servicio de configuración"""
    
    def __init__(self):
        """Inicializar servicio de configuración"""
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.config = AppConfig()
        
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Asegurar que exista el directorio de configuración"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Config directory: {self.config_dir}")
        except Exception as e:
            logger.error(f"Failed to create config directory: {e}")
    
    def load(self) -> AppConfig:
        """
        Cargar configuración desde archivo.
        
        Returns:
            Configuración cargada o por defecto
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = AppConfig.from_dict(data)
                    logger.info(f"✅ Configuration loaded from {self.config_file}")
                    return self.config
        
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
        
        logger.info("Using default configuration")
        return self.config
    
    def save(self) -> bool:
        """
        Guardar configuración a archivo.
        
        Returns:
            True si fue exitoso
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Configuration saved to {self.config_file}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get(self) -> AppConfig:
        """Obtener configuración actual"""
        return self.config
    
    def set(self, config: AppConfig) -> None:
        """Establecer configuración"""
        self.config = config
        self.save()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Actualizar valores de configuración"""
        config_dict = self.config.to_dict()
        config_dict.update(updates)
        self.config = AppConfig.from_dict(config_dict)
        self.save()


# Instancia global
_config_service: Optional[ConfigService] = None


def get_config_service() -> ConfigService:
    """Obtener instancia global del servicio de configuración"""
    global _config_service
    if _config_service is None:
        _config_service = ConfigService()
    return _config_service


config_service = get_config_service()
