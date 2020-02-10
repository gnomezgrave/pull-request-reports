NAME_LIST_LIMIT = 2


class NameFormatter:
    def __init__(self):
        pass

    @staticmethod
    def get_name_list(names, limit=NAME_LIST_LIMIT):
        if not names:
            return None
        names = list(names.values())

        if len(names) == 1:
            return names[0]

        if len(names) <= limit:
            return ", ".join(names[:limit - 2]) + " and " + names[-1]
        elif len(names) > limit:
            return ", ".join(names[:limit]) + f" and {len(names[limit:])} others"
