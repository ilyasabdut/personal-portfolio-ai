import os
from pathlib import Path
from typing import Any

from loguru import logger


class MoneyTrackerConfig:
    _obj: Any = None

    @classmethod
    def initiate(cls, reinitiate: bool = False) -> Any:
        if cls._obj is None or reinitiate:
            try:
                env_path = (Path(os.getcwd()) / ".env").as_posix()

                # Load environment variables directly
                env_vars = {}
                if os.path.exists(env_path):
                    with open(env_path) as f:
                        for line in f:
                            if line.strip() and not line.startswith("#"):
                                key, value = line.strip().split("=", 1)
                                env_vars[key.lower()] = value
                                os.environ[key] = value

                # Create a dynamic config object
                class Config:
                    def __init__(self, env_vars):
                        # Set all environment variables as attributes
                        for key, value in env_vars.items():
                            setattr(self, key.lower(), value)

                        # Set defaults for required variables
                        if not hasattr(self, "environment"):
                            self.environment = "development"

                cls._obj = Config(env_vars)

                logger.info(
                    "Successfully initiated Money Tracker configuration"
                )

            except Exception as e:
                logger.error(
                    f"Failed to initiate Money Tracker configuration: {e}",
                    exc_info=True,
                )
                raise

    @classmethod
    def get_config(cls) -> Any:
        cls.initiate()
        return cls._obj

    @classmethod
    def get_server_host(cls) -> str:
        config = cls.get_config()
        if config.environment.lower() == "development":
            return money_tracker_config.backend_url
        return (
            "https://your-production-domain.com"  # Change this for production
        )


money_tracker_config: Any = MoneyTrackerConfig.get_config()
