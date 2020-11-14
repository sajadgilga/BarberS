from BarberS import settings


def get_error_obj(err, e=None):
    error_object = settings.error_status[err]
    if e:
        error_object['exception'] = e
    return {'error': error_object}
