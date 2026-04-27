class Alias:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __class_getitem__(cls, item):
        return cls(*item)