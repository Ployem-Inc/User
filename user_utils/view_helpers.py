"""
view helpers 
"""
from rest_framework import status
from django.core.validators import RegexValidator 
from django.core.exceptions import ValidationError

##### Global Constants #####
months             = {1 : "JAN", 2 : "FEB", 3 : "MAR", 4 : "APR", 
                      5 : "MAY", 6 : "JUN", 7 : "JUL", 8 : "AUG", 
                      9 : "SEP", 10 : "OCT", 11 : "NOV", 12 : "DEC"}
date_regex         = "^(19\d\d|20[01][01])[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$"
password_regex     = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

_validate_password = RegexValidator(password_regex)
_leap_year         = lambda year : year % 4 == 0

##### Functions #####
def _validate_date(date):
    """
    Validates that a date is within 1900-01-01 through 2011-12-31 

    Inputs
        :param date: <str> formatted as YYYY-MM-DD
    
    Outputs
        :raises: <ValidationError> if the date is formatted incorrectly or the date does not exist 
    """
    RegexValidator(date_regex)(date)

    day   = int(date[8:])
    year  = int(date[:4])
    month = months[int(date[5:7])]

    if month == "FEB":
        if day > 29 or (not _leap_year(year) and day == 29): 
            raise ValidationError("FEB %d is not a valid day in %d" % (day, year))

    elif month in ["APR", "JUN", "SEP", "NOV"]:
        if day == 31: 
            raise ValidationError("%s 31st is not a valid day" % month)

def _is_subset(required_fields, request_fields):
    """
    Checks that the required fields are a subset of the request fields

    Definitions
        subset
            a sequence of objects contained within another sequence 

            A = {1, 2, 3} is a subset of B = {1, 2, 3, 4, 5}

    Inputs
        :param required_fields: <list> of strings representing fields required
        :param request_fields: <view> of strings representing fields sent by the request 

    Outputs
        :returns: Status ...
                         ... HTTP_200_OK if the required fields are a subset of the request fields
                         ... HTTP_400_BAD_REQUEST if the required fields are not a subset of the request fields
    """
    for field in required_fields:
        if field not in request_fields: 
            return status.HTTP_400_BAD_REQUEST
    return status.HTTP_200_OK