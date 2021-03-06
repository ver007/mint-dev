def bitify(data):
    return ''.join('{:08b}'.format(ord(byte)) for byte in data)

def unbitify(bits):
    return ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

def format_bytes(bytes, type='hex'):
    if type == 'hex':
        return ' '.join('{:02x}'.format(ord(byte)) for byte in bytes)
    elif type == 'bin':
        return ' '.join('{:08b}'.format(ord(byte)) for byte in bytes)

def split(xs, *preds):
    if not preds:
        return xs
    if len(preds) == 1:
        preds += (lambda t: not preds[0](t),)
    rss = [[] for _ in preds]
    for x in xs:
        for rs, yes in zip(rss, map(lambda p: p(x), preds)):
            if yes:
                rs.append(x)
    return rss

def split_into(xs, group_size):
    return [xs[i:i+group_size] for i in range(0, len(xs), group_size)]

def split_at(xs, index):
    return xs[:index], xs[index:]

if __name__ == '__main__':
    t = bitify('hi\x03')
    print t
    t = unbitify(t)
    print repr(t)
