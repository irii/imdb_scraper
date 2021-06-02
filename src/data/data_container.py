import os
import pandas as pd
import threading
from ast import literal_eval

COLUMNS_ACTORS = ['ID', 'Name', 'DateOfBirth', 'BornIn', 'Biography', 'SourceUrl', 'Completed'] # Supports partial data
COLUMNS_ACTORS_KEYS = ['ID']

COLUMNS_MOVIES = ['ID', 'Title', 'Release', 'AvgRating', 'Genres', 'SourceUrl', 'Completed'] # Supports partial data
COLUMNS_MOVIES_KEYS = ['ID']

COLUMNS_LISTS = ['ID', 'SortId', 'Title', 'Type', 'ItemId', 'SourceUrl']
COLUMNS_LISTS_KEYS = ['ID', 'Type', 'ItemId']

COLUMNS_AWARDS = ['ActorID', 'Name', 'Year', 'Winner', 'Category', 'Description', 'MovieId', 'SourceUrl']
COLUMNS_AWARDS_KEYS = ['ActorID', 'Name', 'Year', 'MovieId']

COLUMNS_ACTORS_MOVIES = ['MovieID', 'ActorID', 'SourceUrl']
COLUMNS_ACTORS_MOVIES_KEYS = ['MovieID', 'ActorID']

class DataContainer:
    _lock = threading.Lock() # Allows usage of multi scraping processes

    _database_folder: str
    _image_folder: str

    actors: pd.DataFrame
    movies: pd.DataFrame
    lists: pd.DataFrame
    awards: pd.DataFrame
    actors_movies: pd.DataFrame

    database_loaded: bool = False

    def _initEmpty(self):
        self.actors = pd.DataFrame ([], columns = COLUMNS_ACTORS)#.set_index(COLUMNS_ACTORS_KEYS)
        self.movies = pd.DataFrame ([], columns = COLUMNS_MOVIES)#.set_index(COLUMNS_MOVIES_KEYS)
        self.lists = pd.DataFrame ([], columns = COLUMNS_LISTS)#.set_index(COLUMNS_LISTS_KEYS)
        self.awards = pd.DataFrame ([], columns = COLUMNS_AWARDS)#.set_index(COLUMNS_AWARDS_KEYS)
        self.actors_movies = pd.DataFrame([], columns = COLUMNS_ACTORS_MOVIES)#.set_index(COLUMNS_ACTORS_MOVIES_KEYS)

    def save(self):
        with self._lock:
            actors = os.path.join(self._database_folder, 'actors.csv')
            movies = os.path.join(self._database_folder, 'movies.csv')
            lists = os.path.join(self._database_folder, 'lists.csv')
            awards = os.path.join(self._database_folder, 'awards.csv')
            actors_movies = os.path.join(self._database_folder, 'actors_movies.csv')

            self.actors.to_csv(actors, index=False)
            self.movies.to_csv(movies, index=False)
            self.lists.to_csv(lists, index=False)
            self.awards.to_csv(awards, index=False)
            self.actors_movies.to_csv(actors_movies, index=False)

    def getImage(self, id):
        if self._image_folder == None:
            return None

        for f in os.listdir(self._image_folder):
            if os.path.splitext(f)[0].lower() == id.lower():
                return os.path.join(self._image_folder, f)

        return None


    def getImages(self):
        if self._image_folder == None:
            return []

        return os.listdir(self._image_folder)

    def saveImage(self, name, data):
        if self._image_folder == None:
            return

        fileName = os.path.join(self._image_folder, name)
        with open(fileName, "wb") as f:
            f.write(data)

    def loadImage(self, name):
        if self._image_folder == None:
            return

        fileName = os.path.join(self._image_folder, name)
        if os.path.isfile(fileName):
            with open(fileName, "rb") as f:
                return f.read()

        return None

    def imageExists(self, name):
        fileName = os.path.join(self._image_folder, name)
        return os.path.isfile(fileName)


    def load(self, folder):
        with self._lock:
            self._initEmpty()
            self._database_folder = folder

            actors = os.path.join(folder, 'actors.csv')
            movies = os.path.join(folder, 'movies.csv')
            lists = os.path.join(folder, 'lists.csv')
            awards = os.path.join(folder, 'awards.csv')
            actors_movies = os.path.join(folder, 'actors_movies.csv')
            self._image_folder = os.path.join(folder, 'images')

            if not os.path.isdir(self._image_folder):
                os.mkdir(self._image_folder)

            if os.path.isfile(actors):
                self.actors = pd.read_csv(actors)#.set_index(COLUMNS_ACTORS_KEYS)
                
            if os.path.isfile(movies):
                self.movies = pd.read_csv(movies)#.set_index(COLUMNS_MOVIES_KEYS)
                self.movies['Genres'] = self.movies['Genres'].apply(literal_eval)
                
            if os.path.isfile(lists):
                self.lists = pd.read_csv(lists)#.set_index(COLUMNS_LISTS_KEYS)
                
            if os.path.isfile(awards):
                self.awards = pd.read_csv(awards)#.set_index(COLUMNS_AWARDS_KEYS)

            if os.path.isfile(actors_movies):
                self.actors_movies = pd.read_csv(actors_movies)#.set_index(COLUMNS_ACTORS_MOVIES_SORTING_KEYS)

            self.database_loaded = True


    def insertOrUpdateActor(self, actorDict):
        with self._lock:
            id = actorDict["ID"]
            exists = self.actors[(self.actors["ID"] == id)]

            if len(exists) > 0 and exists.loc[exists.index[0], 'Completed'] == True and actorDict["Completed"] == False:
                return # Don't overwrite complete actor with incomplete data

            df1 = self.actors
            df2 = pd.DataFrame([actorDict], columns=COLUMNS_ACTORS)

            self.actors = pd.concat([df1,df2]).drop_duplicates(COLUMNS_ACTORS_KEYS, keep='last').sort_values('ID')

    def insertOrUpdateActorAward(self, awardDict):
        with self._lock:
            df1 = self.awards
            df2 = pd.DataFrame([awardDict], columns=COLUMNS_AWARDS_KEYS)
            self.awards = pd.concat([df1,df2]).drop_duplicates(COLUMNS_AWARDS_KEYS, keep='last').sort_values(['Year', 'Name'])

    def insertOrUpdateMovie(self, movieDict):
        with self._lock:
            id = movieDict["ID"]
            exists = self.movies[(self.movies["ID"] == id)]

            if len(exists) > 0 and exists.loc[exists.index[0], 'Completed'] == True and movieDict["Completed"] == False:
                return # Don't overwrite complete actor with incomplete data

            df1 = self.movies
            df2 = pd.DataFrame([movieDict], columns=COLUMNS_MOVIES)

            self.movies = pd.concat([df1,df2]).drop_duplicates(COLUMNS_MOVIES_KEYS, keep='last').sort_values('ID')

    def insertActorMovie(self, mapping):
        with self._lock:
            df1 = self.actors_movies
            df2 = pd.DataFrame([mapping], columns=COLUMNS_ACTORS_MOVIES)
            self.actors_movies = pd.concat([df1,df2]).drop_duplicates(COLUMNS_ACTORS_MOVIES_KEYS, keep='last')

    def insertOrUpdateList(self, id, items):
        with self._lock:
            df1 = self.lists[(self.lists["ID"] != id)]
            df2 = pd.DataFrame(items, columns=COLUMNS_LISTS)
            self.lists = pd.concat([df1,df2]).drop_duplicates(COLUMNS_LISTS_KEYS,keep='last')