from PyQt5.sip import delete


class WindowManager:
    """ This class handels all openend child windows for the currently running application instance.
    """

    _id_factories = {}
    _view_factories = {}
    _view_sessions = {}
    
    def __init__(self, *defaultArgs):
        """Constructor
        Args:
            *defaultArgs    All arguments which were passed here, are passed to the id and view factory.
        """
        self._defaultArgs = defaultArgs

    def get_or_create_view(self, type: str,  *args):
        """Get's or creates a new view if not existing for the generated id.

        Args:
            type (str): Window type

        Returns:
            object: Returns the created view.
        """
        id = self._id_factories[type](*args)

        if id in self._view_sessions.keys():
            return self._view_sessions[id]

        view = self._view_factories[type](self, *self._defaultArgs, *args)
        self._view_sessions[id] = view
        
        view.closed.connect(lambda: self._view_sessions.pop(id, None))

        return view

    def get_id(self, type: str, *args) -> str:
        """Returns the generated id based on type and the given arguments.

        Args:
            type (str): Window type

        Returns:
            str: A unique id
        """
        return self._id_factories[type](*args)

    def register_view(self, type: str, idGenerator, viewGenerator):
        """Registers a view factory with it's id generator.

        Args:
            type (str): The window type
            idGenerator ([type]): The id generator function
            viewGenerator ([type]): The view generator function
        """
        self._id_factories[type] = idGenerator
        self._view_factories[type] = viewGenerator

    def close_view(self, id: str):
        """Closes a view by it's given id

        Args:
            id (str): The window id which should be closed.
        """
        if id in self._view_sessions.keys():
            self._view_sessions[id].close()

    def destroy_all(self):
        """Destories all views
        """
        keys_copy = [] + list(self._view_sessions.keys()) # Make a copy, for avoiding collection change and threading issues

        for id in keys_copy:
            view = self._view_sessions.get(id, None)
            if view:
                view.close()