import os
import pandas as pd

COLUMNS_ACTORS = ['ID', 'Name', 'DateOfBirth', 'BornIn']
COLUMNS_ACTORS_KEYS = ['ID']

COLUMNS_MOVIES = ['ID', 'Title', 'Description', 'Release', 'AvgRating', 'Genre']
COLUMNS_MOVIES_KEYS = ['ID']

COLUMNS_LISTS = ['ID', 'SortId', 'Title', 'Type', 'ItemId']
COLUMNS_LISTS_KEYS = ['ID', 'Type', 'ItemId']

COLUMNS_AWARDS = ['ActorID', 'Name', 'Year', 'Winner', 'Category', 'Description', 'MovieId']
COLUMNS_AWARDS_KEYS = ['ActorID', 'Name', 'Year', 'MovieId']

COLUMNS_ACTORS_MOVIES = ['MovieID', 'ActorID']
COLUMNS_ACTORS_MOVIES_KEYS = ['MovieID', 'ActorID']

COLUMNS_ACTORS_MOVIES_SORTING = ['MovieID', 'ActorID', 'Type', 'Value', 'SortId']
COLUMNS_ACTORS_MOVIES_SORTING_KEYS = ['MovieID', 'ActorID', 'Type', 'Value', 'SortId']

class DataContainer:  
    _image_folder: str

    actors: pd.DataFrame
    movies: pd.DataFrame
    lists: pd.DataFrame
    awards: pd.DataFrame
    actors_movies: pd.DataFrame

    database_loaded: bool = False

    def _initEmpty(self):
        self.actors = pd.DataFrame ([], columns = COLUMNS_ACTORS)
        self.movies = pd.DataFrame ([], columns = COLUMNS_MOVIES)
        self.lists = pd.DataFrame ([], columns = COLUMNS_LISTS)
        self.awards = pd.DataFrame ([], columns = COLUMNS_AWARDS)
        self.actors_movies = pd.DataFrame([], columns = COLUMNS_ACTORS_MOVIES)

    def save(self, folder):
        actors = os.path.join(folder, 'actors.csv')
        movies = os.path.join(folder, 'movies.csv')
        lists = os.path.join(folder, 'lists.csv')
        awards = os.path.join(folder, 'awards.csv')
        actors_movies = os.path.join(folder, 'actors_movies.csv')

        self.actors.to_csv(actors)
        self.movies.to_csv(movies)
        self.lists.to_csv(lists)
        self.awards.to_csv(awards)
        self.actors_movies.to_csv(actors_movies)

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
        self._initEmpty()

        actors = os.path.join(folder, 'actors.csv')
        movies = os.path.join(folder, 'movies.csv')
        lists = os.path.join(folder, 'lists.csv')
        awards = os.path.join(folder, 'awards.csv')
        actors_movies = os.path.join(folder, 'actors_movies.csv')
        self._image_folder = os.path.join(folder, 'images')

        if not os.path.isdir(self._image_folder):
            os.mkdir(self._image_folder)

        if os.path.isfile(actors):
            self.actors = pd.read_csv(actors)
            
        if os.path.isfile(movies):
            self.movies = pd.read_csv(movies)
            
        if os.path.isfile(lists):
            self.lists = pd.read_csv(lists)
            
        if os.path.isfile(awards):
            self.awards = pd.read_csv(awards)

        if os.path.isfile(actors_movies):
            self.actors_movies = pd.read_csv(actors_movies)

        self.database_loaded = True


    def migrateActorsMovies(self, actorsMovies, delete_orphanded_items):
        df2 = pd.DataFrame(actorsMovies, columns=COLUMNS_ACTORS_MOVIES)

        if delete_orphanded_items == True:
            self.actors_movies = df2
        else:
            self.actors_movies = self.actors_movies.set_index(COLUMNS_ACTORS_MOVIES_SORTING_KEYS).combine_first(df2.set_index(COLUMNS_ACTORS_MOVIES_SORTING_KEYS))

    def migrateActors(self, actors, delete_orphanded_items):
        df2 = pd.DataFrame(actors, columns=COLUMNS_ACTORS)

        if delete_orphanded_items == True:
            self.actors = df2
        else:
            self.actors = self.actors.set_index(COLUMNS_ACTORS_KEYS).combine_first(df2.set_index(COLUMNS_ACTORS_KEYS))

    def migrateMovies(self, movies, delete_orphanded_items):
        df2 = pd.DataFrame(movies, columns=COLUMNS_MOVIES)

        if delete_orphanded_items == True:
            self.movies = df2
        else:
            self.movies = self.movies.set_index(COLUMNS_MOVIES_KEYS).combine_first(df2.set_index(COLUMNS_MOVIES_KEYS))

    def migrateAwards(self, awards, delete_orphanded_items):
        df2 = pd.DataFrame(awards, columns=COLUMNS_AWARDS)

        if delete_orphanded_items == True:
            self.awards = df2
        else:
            self.awards = self.awards.set_index(COLUMNS_AWARDS_KEYS).combine_first(df2.set_index(COLUMNS_AWARDS_KEYS))

    def migrateLists(self, lists, delete_orphanded_items):
        df2 = pd.DataFrame(lists, columns=COLUMNS_LISTS)

        if delete_orphanded_items == True:
            self.lists = df2
        else:
            self.lists = self.lists.set_index(COLUMNS_LISTS_KEYS).combine_first(df2.set_index(COLUMNS_LISTS_KEYS))