from formatters import BasePRFormatter


class PRFormatter(BasePRFormatter):
    def __init__(self, config, name_formatter):
        super().__init__(config, name_formatter)

    def _title(self, pull_request, date_suffix, warning_emoji):
        return f"<a href='{pull_request.url}'><b>{pull_request.title}</b></a> ({date_suffix}){warning_emoji}"

    def _merge_message(self):
        return f"<b><i>Please Merge!<i></b>"

    def _new_line(self):
        return "<br/>"

    def _tab(self):
        return "&tab;"
