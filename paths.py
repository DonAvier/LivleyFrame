import os

class Paths:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RSX_DIR = os.path.join(BASE_DIR, "Resourcex")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    GENERATED_FOLDER = os.path.join(BASE_DIR, "generated")


    @classmethod
    def ensure_directories(cls, directories=None):
        # Crea le cartelle se non esistono
        if directories is None:
            directories = [cls.UPLOAD_FOLDER, cls.GENERATED_FOLDER]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def get_upload_folder_path():
        # Restituisce il percorso della cartella "uploads"
        return Paths.UPLOAD_FOLDER

    @staticmethod
    def get_generated_folder_path():
        # Restituisce il percorso della cartella "generated"
        return Paths.GENERATED_FOLDER
