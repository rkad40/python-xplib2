from rex import Rex

def custom_sort(val):
    rex = Rex()
    def update_nums(m):
        num = int(m[1])
        num = num + 1000000000000000000
        return str(num)
    val = rex.s(val, '(\d+)', update_nums, 'g=')    
    return val

def pre_data_validation(data, arg):
    return data

def post_data_validation(data, arg):
    if not arg['rule'] == 'Dict1':
        raise Exception('Houston, we have a problem!');
    return data
