from domain.service.file_manager import FileManager
from paths import Paths


class VideoManager(FileManager):
    """Manager specifico per i video generati."""

    def __init__(self):
        super().__init__(Paths.get_generated_folder_path(), "generated")
