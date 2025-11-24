from abc import ABC, abstractmethod
from domain.entity.abstraction.iimage_model import IImageModel


class IVideoMaker(ABC):
    """Builder astratto per comporre modelli generativi di immagini/video."""

    @abstractmethod
    def use_model_adapter(self, model_adapter: IImageModel) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_video(self) -> None:
        raise NotImplementedError
