from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    access_db_path: str = ""
    access_odbc_driver: str = "Microsoft Access Driver (*.mdb, *.accdb)"
    demo_allowed: bool = True

    @classmethod
    def from_environment(cls):
        return cls(
            access_db_path=os.getenv("ACCESS_DB_PATH", "").strip(),
            access_odbc_driver=os.getenv(
                "ACCESS_ODBC_DRIVER",
                "Microsoft Access Driver (*.mdb, *.accdb)",
            ),
            demo_allowed=os.getenv("CARIMBO_DEMO", "true").lower()
            not in {"0", "false", "nao", "não"},
        )

    @property
    def access_configured(self):
        return bool(self.access_db_path)