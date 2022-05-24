from datetime import datetime, timedelta
import panel

now = datetime.now()

date_range_picker = panel.widgets.DatetimeRangePicker(enable_time=False, value=(now - timedelta(days=1), now))
