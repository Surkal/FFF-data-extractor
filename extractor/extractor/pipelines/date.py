import re
import time


class DatePipeline:
    def process_item(self, item, spider):
        date = item['confrontation_date']
        date = self.trunc_day_name(date)
        date = self.replace_month_name_by_number(date)
        date = self.get_time_object(date)
        item['confrontation_date'] = date
        return item

    def trunc_day_name(self, date):
        pattern = r"(\d.*)$"
        match = re.search(pattern, date)
        return match.group(0)

    def replace_month_name_by_number(self, date):
        months = {
            'janvier': '01',
            'février': '02',
            'mars': '03',
            'avril': '04',
            'mai': '05',
            'juin': '06',
            'juillet': '07',
            'août': '08',
            'septembre': '09',
            'octobre': '10',
            'novembre': '11',
            'décembre': '12',
        }

        for month_name, month_number in months.items():
            date = date.replace(month_name, month_number)
        
        return date

    def get_time_object(self, date):
        if re.search(r'^\d+\s+\d+\s+\d+$', date):
            # sometimes, the hour is not indicated
            return time.strptime(date, "%d %m %Y")
        return time.strptime(date, "%d %m %Y - %HH%M")