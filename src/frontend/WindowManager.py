from PyQt5.sip import delete


class WindowManager:
    _id_facotries = {}
    _view_facotries = {}

    _view_sessions = {}
    
    def __init__(self, *defaultArgs):
        self._defaultArgs = defaultArgs

    def get_or_create_view(self, type,  *args):
        id = self._id_facotries[type](*args)

        if id in self._view_sessions.keys():
            return self._view_sessions[id]

        view = self._view_facotries[type](self, *self._defaultArgs, *args)
        self._view_sessions[id] = view
        
        view.closed.connect(lambda: self._view_sessions.pop(id, None))

        return view

    def get_id(self, type, *args):
        return self._id_facotries[type](*args)

    def register_view(self, type, idGenerator, viewGenerator):
        self._id_facotries[type] = idGenerator
        self._view_facotries[type] = viewGenerator

    def close_view(self, id):
        if id in self._view_sessions.keys():
            self._view_sessions[id].close()

    def destroy_all(self):
        keys_copy = [] + list(self._view_sessions.keys()) # Avoid threading issues

        for id in keys_copy:
            view = self._view_sessions.get(id, None)
            if view:
                view.close()