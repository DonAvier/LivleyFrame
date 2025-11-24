from domain.entity.abstraction.iimage_model import IImageModel

class VideoMaker:

    ImageModelLists: list[IImageModel] = []

    def __init__(self):
        pass

    def UseModelAdapter(self, model_adapter: IImageModel):
        if not isinstance(model_adapter, IImageModel):
            raise TypeError("model_adapter deve implementare IImageModel")

        # Registrazione nell'array (evitando duplicati)
        if model_adapter not in self.ImageModelLists:
            self.ImageModelLists.append(model_adapter)

    def CreateVideo(self):
        for model in self.ImageModelLists:
            model.RunModel()