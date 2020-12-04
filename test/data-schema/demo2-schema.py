days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

def validate_day(value, obj):
    value = value.lower().capitalize()
    if not value in days_of_week: raise Exception('Value "{}" is not a valid day. Must be one of: "{}"'.format(value, '", "'.join(days_of_week)))
    return(value)
