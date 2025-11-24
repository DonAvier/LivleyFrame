from domain.service.abstraction.ifile_manager import IFileManager
from domain.service.file_manager import FileManager
from paths import Paths


class FileManagerFactory:
    """Factory per risolvere il manager corretto in base al tipo di file."""

    _registry: dict[str, IFileManager] | None = None

    @classmethod
    def _build_registry(cls) -> dict[str, IFileManager]:
        return {
            "image": FileManager(Paths.get_upload_folder_path(), "uploads"),
            "video": FileManager(Paths.get_generated_folder_path(), "generated"),
        }

    @classmethod
    def get(cls, file_type: str) -> IFileManager:
        if not file_type:
            raise ValueError("file_type obbligatorio")

        if cls._registry is None:
            cls._registry = cls._build_registry()

        manager = cls._registry.get(file_type.lower())
        if manager is None:
            raise KeyError(f"Manager non registrato per il tipo '{file_type}'")
        return manager
