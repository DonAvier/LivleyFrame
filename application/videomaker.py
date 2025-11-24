from domain.entity.abstraction.iimage_model import IImageModel
from domain.service.abstraction.ivdeo_maker import IVideoMaker


class VideoMaker(IVideoMaker):
    def __init__(self):
        self.image_models: list[IImageModel] = []

    def use_model_adapter(self, model_adapter: IImageModel) -> None:
        if not isinstance(model_adapter, IImageModel):
            raise TypeError("model_adapter deve implementare IImageModel")

        if model_adapter not in self.image_models:
            self.image_models.append(model_adapter)

    def UseModelAdapter(self, model_adapter: IImageModel) -> None:
        """Alias PascalCase per retro-compatibilità con il diagramma."""
        self.use_model_adapter(model_adapter)

    def create_video(self):
        return [model.RunModel() for model in self.image_models]

    def CreateVideo(self):
        return self.create_video()
