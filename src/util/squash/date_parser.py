def date_parser(input_date):
    # Split the input date string based on the underscore
    date_parts = input_date.split('_')
    
    # Extract date and time components
    date = date_parts[0].replace('-', '')
    time = date_parts[1].replace(':', '')

    # Concatenate date and time components
    formatted_date = date + time

    return formatted_date
