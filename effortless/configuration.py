from typing import Any, Dict, List, Optional


class EffortlessConfig:
    """
    Configuration class for EffortlessDB.

    This class holds various configuration options for an EffortlessDB instance.
    """

    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialize an EffortlessConfig instance.

        Args:
            config (Dict[str, Any], optional): A dictionary of configuration options. Defaults to an empty dict.

        Attributes:
            debug (bool): Enable debug mode. Defaults to False.
            requires (List[str]): List of required fields for each entry. Defaults to an empty list.
            max_size (Optional[int]): Maximum size of the database in MB. Defaults to None (no limit).
            v (int): Version of the configuration. Always 1 for now.
            backup (Optional[str]): Path to backup location. Defaults to None (no backup).
            backup_interval (int): Number of operations between backups. Defaults to 1.
            encrypted (bool): Whether the database should be encrypted. Defaults to False.
            compressed (bool): Whether the database should be compressed. Defaults to False.
            readonly (bool): Whether the database is in read-only mode. Defaults to False.
        """
        self.debug: bool = config.get("dbg", False)
        self.requires: List[str] = config.get("rq", [])
        self.max_size: Optional[int] = config.get("ms")
        self.v: int = config.get("v", 1)
        self.backup: Optional[str] = config.get("bp")
        self.backup_interval: int = config.get("bpi", 1)
        self.encrypted: bool = config.get("enc", False)
        self.compressed: bool = config.get("cmp", False)
        self.readonly: bool = config.get("ro", False)

        self._validate()

    def _validate(self) -> None:
        """
        Validate the configuration values.

        Raises:
            ValueError: If any configuration value is invalid.
        """
        if self.max_size is not None and self.max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if self.v != 1:
            raise ValueError(
                "v1 is the only version of EffortlessDB currently available."
            )
        if self.backup_interval <= 0:
            raise ValueError("Backup interval must be a positive integer")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the configuration.
        """
        return {
            "dbg": self.debug,
            "rq": self.requires,
            "ms": self.max_size,
            "v": self.v,
            "bp": self.backup,
            "bpi": self.backup_interval,
            "enc": self.encrypted,
            "cmp": self.compressed,
            "ro": self.readonly,
        }

    @staticmethod
    def default_headers() -> Dict[str, Any]:
        """
        Create a dictionary with default headers.

        Note:
            Mainly used for internal unit testing. If you want a default config, just create one with EffortlessConfig().

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary containing default headers.
        """
        return {"headers": EffortlessConfig().to_dict()}
