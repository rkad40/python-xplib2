import datetime
import ru
from django.utils import timezone

def get_localized_datetime_now():
    val = datetime.datetime.now()
    current_tz = timezone.get_current_timezone()
    return current_tz.localize(val)

def convert_model_inst_to_dict(data):
    d = {}
    data_dict = data.__dict__
    for key in data_dict:
        if key.startswith('_'): continue
        val = data_dict[key]
        str_type = ru.string_type(data_dict[key])
        if str_type not in ['int', 'str', 'bool', 'float']:
            val = str(val)
        d[key] = val
    return d
