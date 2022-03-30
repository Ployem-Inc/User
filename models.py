"""
user models
"""
import uuid
from django.db import models
from .managers import CustomUserManager
from user_utils.model_helpers import _send_email
from django.contrib.auth.models import AbstractBaseUser

##### Global Constants #####
alphabet_size = 26

##### Classes #####
class CustomUser(AbstractBaseUser):
    """
    AF(first_name, last_name, date_of_birth, email) = user first_name last_name born on date_of_birth reachable at email
    
    Represnetation Invariant
        - inherits from AbstractBaseUser

    Representation Exposure
        - inherits from AbstractBaseUser
        - access is allowed to all fields but they are all immutable
    """
    
    ##### Representation #####
    date_of_birth     = models.DateField()
    first_name        = models.CharField(max_length  = alphabet_size)
    last_name         = models.CharField(max_length  = 2*alphabet_size)
    email             = models.EmailField(max_length = 9*alphabet_size, unique = True)

    is_active         = models.BooleanField(default  = True)
    admin             = models.BooleanField(default  = False)
    staff             = models.BooleanField(default  = False)
    verified          = models.BooleanField(default  = False)
    id                = models.UUIDField(primary_key = True,  editable = False, unique = True, default = uuid.uuid4)
    verification_code = models.UUIDField(primary_key = False, editable = False, unique = True, default = uuid.uuid4)

    USERNAME_FIELD    = 'email'
    REQUIRED_FIELDS   = ['first_name', 'last_name', 'date_of_birth']

    objects           = CustomUserManager()

    def has_permission(self, permission, obj = None) -> bool:
        """
        Checks if the user has the given permission on an obj
        
        Inputs
            :param permission: <str> referencing the functionailty in question
            :param obj: <object> with the permission
        
        Outputs
            :returns: <bool> True if has the given permission on the obj, False otherwise
        """
        raise NotImplementedError
    
    def send_verification_code(self) -> uuid:
        """
        Generates a random verification code for the user and sends it to their email

        Outputs
            :returns: <UUID> encrypted verification code
        """
        self.verification_code = uuid.uuid4() 
        self.save()  
        # sender and reciepient information
        from_email        = "noreply@ployem.com"
        from_password     = None
        reciepient_emails = [self.email]
        # server and port sending the message
        smtp_server       = None 
        smtp_port         = None
        # message content
        subject           = "Account verification code"
        text_content      = "Your verification code is: P-%s" % str(self.verification_code)[:8]
        html_content      = ""

        _send_email(from_email, from_password, reciepient_emails, smtp_server, smtp_port, subject, text_content, html_content)
        return self.verification_code

    def __str__(self) -> str:
        """ Override AbstractBaseUser.__str__() """
        return "%s %s\n\tBirthday: %s\n\tEmail: %s" % (self.first_name, self.last_name, self.date_of_birth, self.email)