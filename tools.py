#!/usr/bin/python3
import datetime
import uuid


NOW = datetime.datetime.now


def json_decode(pairs):
    d = {}
    # print(pairs)
    for k, v in pairs:
        try:
            d[k] = datetime.datetime.strptime(v, '%Y%m%d %T')
        except:
            try:
                d[k] = uuid.UUID(data)
            except:
                d[k] = v
    # print(d)
    return d


def json_encode(data):
    if isinstance(data, uuid.UUID):
        return data.__str__()
    if isinstance(data, datetime.datetime):
        return data.strftime('%Y%m%d %H:%M:%S')
    else:
        return data
