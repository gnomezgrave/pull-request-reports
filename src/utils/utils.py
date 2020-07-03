def get_dates_diff_str(today_date, pr_open_date):
    date_delta = today_date - pr_open_date
    if date_delta.days == 0:
        return "today"
    if date_delta.days == 1:
        return "yesterday"
    return f"{date_delta.days} day{'s' if date_delta.days > 1 else ''} ago"
