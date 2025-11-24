from abc import ABC, abstractmethod
from domain.entity.media_file import MediaFile

class IImageModel(ABC):

    @abstractmethod
    def ImportMedia(self, media_file: MediaFile):
        pass

    @abstractmethod
    def RunModel(self):
        pass