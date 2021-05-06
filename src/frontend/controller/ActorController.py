from data.data_container import DataContainer

class ActorController:
    def __init__(self, model, id, dataContainer: DataContainer, displayMovie):
        self.model = model
        self.id = id
        self._dataContainer = dataContainer
        self._displayMovie = displayMovie

    def set_actor(self, id) -> bool():
        df = self._dataContainer.actors
        actor = df.loc[(df['ID'] == id)].to_dict('records')[0]

        self.model.setDataFrame(actor, None, None, self._dataContainer.getImage(id))

        return True

    def display_movie(self, movieId):
        self._displayMovie(movieId)
