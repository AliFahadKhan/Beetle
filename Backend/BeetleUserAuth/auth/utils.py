import random
import string

BASE_URL = 'https://beetle-discussion-forum.azurewebsites.net/beetle'

def generate_pass():
    pool = string.ascii_letters + string.digits
    generated_str = ''.join((random.choice(pool) for i in range(8)))
    generated_str += random.choice(string.ascii_uppercase)
    generated_str += random.choice(string.digits)
    generated_str += random.choice(string.punctuation)
    return generated_str