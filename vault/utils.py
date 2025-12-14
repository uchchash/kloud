import secrets, string

def generate_permalink():
	characters = string.digits + string.ascii_letters
	return ''.join(secrets.choice(characters) for _ in range(20))
