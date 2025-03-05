def extract_phone_number(full_number):
    country_code = full_number[1:4]  # Extracts the first 4 characters
    phone_number = '0' + full_number[4:]  # Adds '0' to the remaining characters
    return country_code, phone_number