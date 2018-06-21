class Slot:
    def to_dict(self) -> dict:
        ret = {}
        for field in self.__slots__:
            value = getattr(self, field)
            if hasattr(value, 'to_dict'):
                ret[field] = value.to_dict()
            else:
                ret[field] = value
        return ret

    def __repr__(self) -> str:
        return repr(self.to_dict())
