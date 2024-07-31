from datetime import datetime, timedelta

class DateFormatter:
    @staticmethod
    def process_date(date):
        if 'Yesterday' in date:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif 'ago' in date:
            date = datetime.now().strftime("%Y-%m-%d")
        elif ',' in date:
            date = datetime.strptime(date, '%B %d, %Y').strftime("%Y-%m-%d")
        else:
            date = datetime.strptime(date, '%B %d').replace(year=datetime.now().year).strftime("%Y-%m-%d")
        
        return date
