import os.path
import pandas as pd

COLUMNS_ACTORS = ['ID', 'Name', 'DateOfBirth', 'BornIn']
COLUMNS_MOVIES = ['ID', 'Title', 'Release', 'ImageUrl', 'AvgRating']
COLUMNS_LISTS = ['ID', 'SortId', 'Title', 'Type', 'ItemId']
COLUMNS_AWARDS = ['ActorID', 'Name', 'Year', 'Winner', 'MovieId']

class DataContainer:  
    _image_folder: str

    def _initEmpty(self):
        self.actors = pd.DataFrame ([], columns = COLUMNS_ACTORS)
        self.movies = pd.DataFrame ([], columns = COLUMNS_MOVIES)
        self.lists = pd.DataFrame ([], columns = COLUMNS_LISTS)
        self.awards = pd.DataFrame ([], columns = COLUMNS_AWARDS)

    def save(self, folder):
        actors = os.path.join(folder, 'actors.csv')
        movies = os.path.join(folder, 'movies.csv')
        lists = os.path.join(folder, 'lists.csv')
        awards = os.path.join(folder, 'awards.csv')

        self.actors.to_csv(actors)
        self.movies.to_csv(movies)
        self.lists.to_csv(lists)
        self.awards.to_csv(awards)

    def getImage(self, id):
        if self._image_folder == None:
            return None

        return os.path.join(self._image_folder, id)


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


    def migrateActors(self, actors, delete_orphanded_items):
        df2 = pd.DataFrame(actors.values(), columns=['ID', 'Name', 'DateOfBirth', 'BornIn'])

        if delete_orphanded_items == True:
            self.actors = df2
        else:
            self.actors = self.actors.set_index(['ID']).combine_first(df2.set_index('ID'))

    def migrateMovies(self, movies, delete_orphanded_items):
        df2 = pd.DataFrame(movies.values(), columns=['ID', 'Title', 'Release', 'ImageUrl', 'AvgRating'])

        if delete_orphanded_items == True:
            self.movies = df2
        else:
            self.movies = self.movies.set_index(['ID']).combine_first(df2.set_index('ID'))

    def migrateAwards(self, awards, delete_orphanded_items):
        df2 = pd.DataFrame(awards, columns=['ActorID', 'Name', 'Year', 'Winner', 'MovieId'])

        if delete_orphanded_items == True:
            self.awards = df2
        else:
            self.awards = self.awards.set_index(['ActorID', 'Name', 'Year', 'MovieId']).combine_first(df2.set_index(['ActorID', 'Name', 'Year', 'MovieId']))

    def migrateLists(self, lists, delete_orphanded_items):
        df2 = pd.DataFrame(lists, columns=['ID', 'SortId', 'Title', 'Type', 'ItemId'])

        if delete_orphanded_items == True:
            self.lists = df2
        else:
            self.lists = self.lists.set_index(['ID', 'Type', 'ItemId']).combine_first(df2.set_index(['ID', 'Type', 'ItemId']))