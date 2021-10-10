def decode(code):
    code = [code[i:i+1] for i in range(0, len(code), 1)]

    return decode_dict(code)[0]


def decode_dict(code):
    i = 1
    decoded = {}
    key = False

    while code[i] != b'e':

        if code[i] in [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']:
            if key:
                a, b = decode_str(code[i:])
                decoded[key] = a
                i += b
                key = False

            else:
                a, b = decode_str(code[i:])
                key = a
                i += b

        elif code[i] == b'd':
            if key:
                a, b = decode_dict(code[i:])
                decoded[key] = a
                i += b
                key = False

            else:
                a, b = decode_dict(code[i:])
                key = a
                i += b

        elif code[i] == b'i':
            if key:
                a, b = decode_int(code[i:])
                decoded[key] = a
                i += b
                key = False

            else:
                a, b = decode_int(code[i:])
                key = a
                i += b

        elif code[i] == b'l':
            if key:
                a, b = decode_list(code[i:])
                decoded[key] = a
                i += b
                key = False

            else:
                a, b = decode_list(code[i:])
                key = a
                i += b

    return decoded, i + 1


def decode_str(code):
    i = 0
    c = b''
    decoded = b''

    while code[i] in [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']:
        c += code[i]
        i += 1
    i += 1

    for j in range(int(c)):
        decoded += code[i+j]

    try:
        decoded = decoded.decode('utf-8')

    except:
        pass

    return decoded, i + int(c)


def decode_int(code):
    i = 0
    decoded = b''

    while code[i] != b'e':
        i += 1
        decoded += code[i]

    return int(decoded[:-1]), i + 1

def decode_list(code):
    i = 1
    decoded = []

    while code[i] != b'e':
        if code[i] in [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']:
            a, b  = decode_str(code[i:])
            i += b
            decoded.append(a)

        elif code[i] == b'd':
            a, b = decode_dict(code[i:])
            i += b
            decoded.append(a)

        elif code[i] == b'i':
            a, b = decode_int(code[i:])
            i += b
            decoded.append(a)

        elif code[i] == b'l':
            a, b = decode_list(code[i:])
            i += b
            decoded.append(a)

    return decoded, i + 1
