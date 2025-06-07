import secrets
import string

def generate_secret_key(length=32):
    """
    Generate a secure secret key using Python's secrets module.
    
    Args:
        length (int): Length of the secret key (default: 32)
        
    Returns:
        str: A secure random string suitable for use as a secret key
    """
    # Define the character set for the secret key
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Generate the secret key
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return secret_key

if __name__ == '__main__':
    # Generate a secret key
    secret = generate_secret_key()
    
    # Print the secret key
    print("\nGenerated Secret Key:")
    print("-" * 50)
    print(secret)
    print("-" * 50)
    
    # Print instructions
    print("\nTo use this secret key:")
    print("1. Copy the key above")
    print("2. Open your .env file")
    print("3. Set SECRET_KEY=your-copied-key")
    print("\nExample .env entry:")
    print(f"SECRET_KEY={secret}") 