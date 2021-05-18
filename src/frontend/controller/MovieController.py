import pandas as pd
from data.data_container import DataContainer
from frontend.WindowManager import WindowManager

class MovieController:
    def __init__(self, model, dataContainer: DataContainer, windowManager: WindowManager):
        self.model = model
        self._dataContainer = dataContainer
        self._windowManager = windowManager

    def set_movie(self, id) -> bool():
        df = self._dataContainer.movies
        movie = df.loc[(df['ID'] == id)].to_dict('records')[0]

        actors_df = self._dataContainer.actors[['ID', 'Name']]
        actors_movies_df = self._dataContainer.actors_movies[(self._dataContainer.actors_movies["ActorID"] == id)][["MovieID"]]
        
        actors = actors_movies_df.merge(actors_df, how='left', left_on='MovieID', right_on='ID')

        self.model.setDataFrame(movie, actors, self._dataContainer.getImage('movie_' + id))        

        return True

    def display_actor(self, actorId):
        if pd.isnull(actorId):
            return

        self._windowManager.get_or_create_view('ACTOR', actorId).show()