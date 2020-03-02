class NameFormatter:
    def __init__(self, config):
        self._max_names_limit = config.max_names_limit

    def get_name_list(self, names):
        if not names:
            return None
        names = list(names.values())

        if len(names) == 1:
            return names[0]
        limit = self._max_names_limit
        if len(names) <= limit:
            return ", ".join(names[:limit - 1]) + " and " + names[-1]
        elif len(names) > limit:
            remaining_count = len(names[limit:])
            names_str = ", ".join(names[:limit])
            if remaining_count == 1:
                return f"{names_str} and {names[-1]}"
            else:
                return f"{names_str} and {remaining_count} others"
