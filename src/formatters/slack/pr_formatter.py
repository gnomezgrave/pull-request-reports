from formatters import BasePRFormatter


class PRFormatter(BasePRFormatter):
    def __init__(self, config, name_formatter):
        super().__init__(config, name_formatter)

    def _title(self, pull_request, date_suffix, warning_emoji):
        return f"<{pull_request.url}|*{pull_request.title}*> ({date_suffix}) {warning_emoji}"

    def _merge_message(self):
        return f"_*Please Merge!*_"
