import os
import pandas as pd
import threading
from ast import literal_eval

COLUMNS_ACTORS = ['ID', 'Name', 'Nickname', 'DateOfBirth', 'BornIn', 'Biography', 'Height', 'SourceUrl', 'Completed'] # Supports partial data
COLUMNS_ACTORS_KEYS = ['ID']
COLUMNS_ACTORS_TYPE_OVERWRITE = {
    'ID': str,
    'Name': str,
    'Nickname': str,
    'Height': float,
    'DateOfBirth': str,
    'BornIn': str,
    'Biography': str,
    'SourceUrl': str,
    'Completed': bool
    }

COLUMNS_MOVIES = ['ID', 'Title', 'Release', 'AvgRating', 'Genres', 'SourceUrl', 'Completed'] # Supports partial data
COLUMNS_MOVIES_KEYS = ['ID']
COLUMNS_MOVIES_TYPE_OVERWRITE = {
    'ID': str,
    'Title': str,
    'Release': int,
    'AvgRating': float,
    'SourceUrl': str,
    'Completed': bool,
    'Release': pd.Int64Dtype()
    }

COLUMNS_LISTS = ['ID', 'SortId', 'Title', 'Type', 'ItemId', 'SourceUrl']
COLUMNS_LISTS_KEYS = ['ID', 'Type', 'ItemId']
COLUMNS_LISTS_TYPE_OVERWRITE = {
    'ID': str,
    'SortId': int,
    'Title': str,
    'Type': str,
    'ItemId': str,
    'SourceUrl': str
}

COLUMNS_AWARDS = ['ActorID', 'Name', 'Year', 'Winner', 'Category', 'Description', 'MovieId', 'SourceUrl']
COLUMNS_AWARDS_KEYS = ['ActorID', 'Name', 'Year', 'MovieId']
COLUMNS_AWARDS_TYPE_OVERWRITE = {
    'ActorID': str,
    'Name': str,
    'Year': int,
    'Winner': bool,
    'Category': str,
    'Description': str,
    'MovieId': str,
    'SourceUrl': str
}

COLUMNS_ACTORS_MOVIES = ['MovieID', 'ActorID', 'SourceUrl']
COLUMNS_ACTORS_MOVIES_KEYS = ['MovieID', 'ActorID']
COLUMNS_ACTORS_MOVIES_TYPE_OVERWRITE = {
    'MovieID': str,
    'ActorID': str,
    'SourceUrl': str
}

class DataContainer:
    """This class handles all data loading, saving and merging
    
    Attributes:
        _lock               Allows usage of multi scraping processes (Avoids merge collisions)
        _database_folder    Currently loaded database folder
        _image_folder       Currently used images folder
        actors              Current actor pandas dataframe data
        movies              Current movies pandas dataframe data
        awards              Current awards pandas dataframe data
        actors_movies       Current actor movie mapping pandas dataframe data
        database_loaded     Indicator if a database is currently loaded
    
    """

    _lock = threading.Lock() # Allows usage of multi scraping processes (Avoids merge collisions)

    _database_folder: str # Currently loaded database folder
    _image_folder: str #

    actors: pd.DataFrame
    movies: pd.DataFrame
    lists: pd.DataFrame
    awards: pd.DataFrame
    actors_movies: pd.DataFrame

    database_loaded: bool = False

    def _initEmpty(self):
        """Creats a empty database
        """
        self.actors = pd.DataFrame ([], columns = COLUMNS_ACTORS).astype(COLUMNS_ACTORS_TYPE_OVERWRITE)
        self.movies = pd.DataFrame ([], columns = COLUMNS_MOVIES).astype(COLUMNS_MOVIES_TYPE_OVERWRITE)
        self.lists = pd.DataFrame ([], columns = COLUMNS_LISTS).astype(COLUMNS_LISTS_TYPE_OVERWRITE)
        self.awards = pd.DataFrame ([], columns = COLUMNS_AWARDS).astype(COLUMNS_AWARDS_TYPE_OVERWRITE)
        self.actors_movies = pd.DataFrame([], columns = COLUMNS_ACTORS_MOVIES).astype(COLUMNS_ACTORS_MOVIES_TYPE_OVERWRITE)

    def save(self):
        """Saves the current database
        """
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

    def getImage(self, id: str) -> str:
        """Returns the image path based by the given id.

        Args:
            id (str): Image name

        Returns:
            str: Path
        """
        if self._image_folder == None:
            return None

        for f in os.listdir(self._image_folder):
            if os.path.splitext(f)[0].lower() == id.lower():
                return os.path.join(self._image_folder, f)

        return None


    def getImages(self):
        """Returns a list of all images

        Returns:
            list: List of all images (paths)
        """
        if self._image_folder == None:
            return []

        return os.listdir(self._image_folder)

    def saveImage(self, name: str, data):
        """Saves the image into the current database

        Args:
            name (str): Image name
            data ([blob]): Image data
        """
        if self._image_folder == None:
            return

        fileName = os.path.join(self._image_folder, name)
        with open(fileName, "wb") as f:
            f.write(data)

    def loadImage(self, name: str):
        """Loads a image by the given name

        Args:
            name (str): [description]

        Returns:
            [blob]: Image data
        """
        if self._image_folder == None:
            return

        fileName = os.path.join(self._image_folder, name)
        if os.path.isfile(fileName):
            with open(fileName, "rb") as f:
                return f.read()

        return None

    def imageExists(self, name: str) -> bool:
        """Checks if the requested image exists.

        Args:
            name (str): Image name

        Returns:
            bool: Exists result
        """

        fileName = os.path.join(self._image_folder, name)
        return os.path.isfile(fileName)


    def load(self, folder: str):
        """Loads a database given by the folder.

        Args:
            folder (str): Folder path
        """
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
                self.actors = pd.read_csv(actors).astype(COLUMNS_ACTORS_TYPE_OVERWRITE)
                
            if os.path.isfile(movies):
                self.movies = pd.read_csv(movies).astype(COLUMNS_MOVIES_TYPE_OVERWRITE)
                self.movies['Genres'] = self.movies['Genres'].apply(literal_eval)
                
            if os.path.isfile(lists):
                self.lists = pd.read_csv(lists).astype(COLUMNS_LISTS_TYPE_OVERWRITE)
                
            if os.path.isfile(awards):
                self.awards = pd.read_csv(awards).astype(COLUMNS_AWARDS_TYPE_OVERWRITE)

            if os.path.isfile(actors_movies):
                self.actors_movies = pd.read_csv(actors_movies).astype(COLUMNS_ACTORS_MOVIES_TYPE_OVERWRITE)

            self.database_loaded = True


    def insertOrUpdateActor(self, actorDict: dict):
        """Add's or merges the actor data into the current database

        Args:
            actorDict (dict): Data
        """
        with self._lock:
            id = actorDict["ID"]
            exists = self.actors[(self.actors["ID"] == id)]

            if len(exists) > 0 and exists.loc[exists.index[0], 'Completed'] == True and actorDict["Completed"] == False:
                return # Don't overwrite complete actor with incomplete data

            df1 = self.actors
            df2 = pd.DataFrame([actorDict], columns=COLUMNS_ACTORS).astype(COLUMNS_ACTORS_TYPE_OVERWRITE)

            self.actors = pd.concat([df1,df2]).drop_duplicates(COLUMNS_ACTORS_KEYS, keep='last').sort_values('ID')

    def insertOrUpdateActorAward(self, awardDict: dict):
        """Add's or merges the award data into the current database

        Args:
            awardDict (dict): Data
        """
        with self._lock:
            df1 = self.awards
            df2 = pd.DataFrame([awardDict], columns=COLUMNS_AWARDS).astype(COLUMNS_AWARDS_TYPE_OVERWRITE)
            self.awards = pd.concat([df1,df2]).drop_duplicates(COLUMNS_AWARDS_KEYS, keep='last').sort_values(['Year', 'Name'])

    def insertOrUpdateMovie(self, movieDict: dict):
        """Add's or merges the movie data into the current database

        Args:
            movieDict (dict): Data
        """
        with self._lock:
            id = movieDict["ID"]
            exists = self.movies[(self.movies["ID"] == id)]

            if len(exists) > 0 and exists.loc[exists.index[0], 'Completed'] == True and movieDict["Completed"] == False:
                return # Don't overwrite complete actor with incomplete data

            df1 = self.movies
            df2 = pd.DataFrame([movieDict], columns=COLUMNS_MOVIES).astype(COLUMNS_MOVIES_TYPE_OVERWRITE)

            self.movies = pd.concat([df1,df2]).drop_duplicates(COLUMNS_MOVIES_KEYS, keep='last').sort_values('ID')

    def insertActorMovie(self, mapping: dict):
        """Add's or merges the actor_movie mapping data into the current database

        Args:
            mapping (dict): Data
        """
        with self._lock:
            df1 = self.actors_movies
            df2 = pd.DataFrame([mapping], columns=COLUMNS_ACTORS_MOVIES)
            self.actors_movies = pd.concat([df1,df2]).drop_duplicates(COLUMNS_ACTORS_MOVIES_KEYS, keep='last').astype(COLUMNS_ACTORS_MOVIES_TYPE_OVERWRITE)

    def insertOrUpdateList(self, id, items):
        """Add's or merges the items data into the current database

        Args:
            items (list): Items
        """

        with self._lock:
            df1 = self.lists[(self.lists["ID"] != id)]
            df2 = pd.DataFrame(items, columns=COLUMNS_LISTS).astype(COLUMNS_LISTS_TYPE_OVERWRITE)
            self.lists = pd.concat([df1,df2]).drop_duplicates(COLUMNS_LISTS_KEYS,keep='last')