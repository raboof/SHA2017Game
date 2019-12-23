import shards

# The shamir secret sharing code in this file was based on
# https://github.com/blockstack/secret-sharing

# micropython 'int' is actually arbitrary-precision it seems?
integer_types = (int)

secret_charset = '0123456789abcdef'
share_charset = '0123456789abcdef'

def egcd(a, b):
    u, u1 = 1, 0
    v, v1 = 0, 1
    g, g1 = a, b
    while g1:
        q = g // g1
        u, u1 = u1, u - q * u1
        v, v1 = v1, v - q * v1
        g, g1 = g1, g - q * g1
    return (g, u, v)

def mod_inverse(k, prime):
    k = k % prime
    if k < 0:
        r = egcd(prime, -k)[2]
    else:
        r = egcd(prime, k)[2]
    return (prime + r) % prime

def modular_lagrange_interpolation(x, points, prime):
    # break the points up into lists of x and y values
    x_values, y_values = zip(*points)
    # initialize f(x) and begin the calculation: f(x) = SUM( y_i * l_i(x) )
    f_x = 0
    for i in range(len(points)):
        # evaluate the lagrange basis polynomial l_i(x)
        numerator, denominator = 1, 1
        for j in range(len(points)):
            # don't compute a polynomial fraction if i equals j
            if i == j:
                continue
            # compute a fraction & update the existing numerator + denominator
            numerator = (numerator * (x - x_values[j])) % prime
            denominator = (denominator * (x_values[i] - x_values[j])) % prime
        # get the polynomial from the numerator + denominator mod inverse
        lagrange_polynomial = numerator * mod_inverse(denominator, prime)
        # multiply the current y & the evaluated polynomial & add it to f(x)
        f_x = (prime + f_x + (y_values[i] * lagrange_polynomial)) % prime
    return f_x

def calculate_mersenne_primes():
    """ Returns all the mersenne primes with less than 500 digits.
        All primes:
        3, 7, 31, 127, 8191, 131071, 524287, 2147483647L, 2305843009213693951L,
        618970019642690137449562111L, 162259276829213363391578010288127L,
        170141183460469231731687303715884105727L,
        68647976601306097149...12574028291115057151L, (157 digits)
        53113799281676709868...70835393219031728127L, (183 digits)
        10407932194664399081...20710555703168729087L, (386 digits)
    """
    mersenne_prime_exponents = [
        2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279
    ]
    primes = []
    for exp in mersenne_prime_exponents:
        prime = 1
        for i in range(exp):
            prime *= 2
        prime -= 1
        primes.append(prime)
    return primes

SMALLEST_257BIT_PRIME = (2**256 + 297)
SMALLEST_321BIT_PRIME = (2**320 + 27)
SMALLEST_385BIT_PRIME = (2**384 + 231)
STANDARD_PRIMES = calculate_mersenne_primes() + [
    SMALLEST_257BIT_PRIME, SMALLEST_321BIT_PRIME, SMALLEST_385BIT_PRIME
]
STANDARD_PRIMES.sort()


def get_large_enough_prime(batch):
    """ Returns a prime number that is greater all the numbers in the batch.
    """
    # build a list of primes
    primes = STANDARD_PRIMES
    # find a prime that is greater than all the numbers in the batch
    for prime in primes:
        numbers_greater_than_prime = [i for i in batch if i > prime]
        if len(numbers_greater_than_prime) == 0:
            return prime
    return None


def int_to_charset(val, charset):
    """ Turn a non-negative integer into a string.
    """
    if not val >= 0:
        raise ValueError('"val" must be a non-negative integer.')
    if val == 0:
        return charset[0]
    output = ""
    while val > 0:
        val, digit = divmod(val, len(charset))
        output += charset[digit]
    # reverse the characters in the output and return
    # No 'step' supported in micropython slices
    # return output[::-1]
    return ''.join(reversed(output))

def charset_to_int(s, charset):
    """ Turn a string into a non-negative integer.
    """
    output = 0
    for char in s:
        output = output * len(charset) + charset.index(char)
    return output

def points_to_secret_int(points, prime=None):
    """ Join int points into a secret int.
        Get the intercept of a random polynomial defined by the given points.
    """
    if not isinstance(points, list):
        raise ValueError("Points must be in list form.")
    for point in points:
        if not isinstance(point, tuple) and len(point) == 2:
            raise ValueError("Each point must be a tuple of two values.")
        if not (isinstance(point[0], integer_types) and
                isinstance(point[1], integer_types)):
            raise ValueError("Each value in the point must be an int, got %d and %d." % (point[0], point[1]))
    x_values, y_values = zip(*points)
    if not prime:
        prime = get_large_enough_prime(y_values)
    free_coefficient = modular_lagrange_interpolation(0, points, prime)
    secret_int = free_coefficient  # the secret int is the free coefficient
    return secret_int

def share_string_to_point(share_string, charset):
    """ Convert a share string to a point (a tuple of integers).
    """
    # share should be in the format "01-d051080de7..."
    if '-' in charset:
        raise ValueError(
            'The character "-" cannot be in the supplied charset.')
    if not isinstance(share_string, str) and share_string.count('-') == 1:
        raise ValueError('Share format is invalid.')
    x_string, y_string = share_string.split('-')
    if (set(x_string) - set(charset)) or (set(y_string) - set(charset)):
        raise ValueError("Share has characters that aren't in the charset.")
    x = charset_to_int(x_string, charset)
    y = charset_to_int(y_string, charset)
    return (x, y)

def key_from_shards(shards):
    points = []
    for share in shards:
        points.append(share_string_to_point(share, share_charset))
    secret_int = points_to_secret_int(points)
    secret_string = int_to_charset(secret_int, secret_charset)
    return secret_string
