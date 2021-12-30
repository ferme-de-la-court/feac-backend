import datetime
from flask.json import JSONEncoder

class FarmerEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        return super().default(obj)
