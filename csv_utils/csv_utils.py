import os
import csv
import itertools

def set_deep(obj, toks, val):
    if len(toks) == 1:
        obj[toks[0]] = val
        return

    try:
        _obj = obj[toks[0]]
    except KeyError:
        _obj = obj[toks[0]] = {}
    return set_deep(_obj, toks[1:], val)

def unflatten(x):
    obj = {}
    for key, val in x.iteritems():
        set_deep(obj, key.split('.'), val)
    return obj

def dict_to_flat_pairs(x, root=None):
    if root is None:
        root = []
    if not hasattr(x, 'iteritems'):
        return [(root, x)]
    child_pairs = (dict_to_flat_pairs(val, root + [key])
                   for key, val in x.iteritems())
    child_pairs = list(child_pairs)
    pairs = list(itertools.chain(*child_pairs))
    return pairs

def flatten_obj(x):
    return {'.'.join(key): val for key, val in dict_to_flat_pairs(x)}

def write_mongo_collection(fname, collection, headers=None):
    rows = [flatten_obj(obj) for obj in collection.find({})]
    write_csv_rows(fname, rows, headers)

def load_csv(fname, header=None, to_np=False):
    data = {}
    with open(fname) as f:
        reader = csv.reader(f, delimiter='\t')
        if header is None:
            header = reader.next()
        for row in reader:
            if len(row) != len(header):
                raise Exception("csv not uniform width")
            if any(map(lambda(cell): cell == 'None', row)):
                continue
            for i, cell in enumerate(row):
                try:
                    val = float(cell)
                except ValueError:
                    val = cell
                try:
                    data[header[i]].append(val)
                except KeyError:
                    data[header[i]] = [val]
    if to_np:
        import numpy as np
        data = {k: np.array(v) for k, v in data.iteritems()}
    return data

def load_csv_rows(fname, header=None, no_nones=False, drop_odds=False, delimiter='\t'):
    data = []
    with open(fname) as f:
        reader = csv.reader(f, delimiter=delimiter)
        if header is None:
            header = reader.next()
        odd = False
        for row in reader:
            odd = not odd
            if drop_odds and odd:
                continue
            if no_nones:
                if len(row) != len(header):
                    continue
                if any(map(lambda(cell): cell == 'None', row)):
                    continue
            row_dict = {}
            for i, cell in enumerate(row):
                try:
                    val = float(cell)
                except ValueError:
                    val = cell
                row_dict[header[i]] = val
            data.append(row_dict)
    return data

def write_csv_headers_rows(fname, headers, rows):
    with open(fname, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

def write_csv(fname, columns=None, rows=None):
    if columns is not None:
        write_csv_columns(fname, columns)
    elif rows is not None:
        write_csv_rows(fname, columns)
    else:
        raise Exception("either columns or rows must be specified")

def write_csv_columns(fname, columns):
    headers = columns.keys()
    rows = itertools.izip(*[columns[key] for key in headers])
    write_csv_headers_rows(fname, headers, rows)

def write_csv_rows(fname, rows, headers=None):
    headers, row_tuples = rows_to_tuples(rows, headers=headers)
    write_csv_headers_rows(fname, headers, row_tuples)

def rows_to_tuples(rows, headers=None):
    rows = list(rows)  # because we need to loop twice

    # get all possible headers
    if headers is None:
        headers = set()
        for row in rows:
            headers = headers | set(row.keys())
        headers = sorted(list(headers))

    # convert to tuples
    row_tuples = []
    for row in rows:
        row_tuple = tuple([row.get(h) for h in headers])
        row_tuples.append(row_tuple)
    return headers, row_tuples

def append_csv_rows(fname, rows, headers=None):
    must_rewrite = False
    must_load = False

    # if no file exists then header must be written
    if not os.path.exists(fname):
        must_rewrite = True
    else:
        # if file exists then check that the headers are correct
        with open(fname, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            old_headers = reader.next()
            old_headers_set = set(old_headers)
            headers_set = set(headers)
            if len(headers_set - old_headers_set) == 0:
                headers = old_headers
            else:
                headers = list(old_headers_set | headers_set)
                must_rewrite = True
                must_load = True

    if must_load:
        old_rows = load_csv_rows(fname)
        rows = old_rows + rows

    headers, row_tuples = rows_to_tuples(rows, headers=headers)
    if must_rewrite:
        write_csv_headers_rows(fname, headers, row_tuples)
    else:
        # headers are correct, append just the rows
        with open(fname, 'a+') as f:
            writer = csv.writer(f, delimiter='\t')
            for row in row_tuples:
                writer.writerow(row)
