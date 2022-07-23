"""
user tests
"""
import time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user_utils.test_helpers import _read_email
from django.core.exceptions import ValidationError

##### Global Constants #####
url = {"signup" : reverse("user-signup"),
       "signin" : reverse("user-signin"),
       "verify" : reverse("confirm-verify")}

class UserTests(APITestCase):
    """
    Testing Strategy:
        Definitions
            invalid request
                wrong request type

                Sending a POST to a GET only view is invalid
            incomplete fields
                incorrect and or missing request fields

                A request missing the first_name field is incomplete
            existing email / user
                email / user which is currently associated with an account

                An existing email / user can't be signed up / in
            unreachable email
                email address does not exist => no message can be sent to it

                Fake emails are usually unreachable

        Partition ... 
            ... on signup (in)valid request, (in)complete fields, (un)met precondition(s), (un)reachable / (non)existing email 
            ... on verify (in)valid verification code
            ... on signin (in)valid request, (non)existing / (un)verified user 
    """
    ##### Signup Tests #####
    def test_signup_invalid(self):
        """ 
        Tests ... 
              ... on signup: invalid request 
        """
        request_data = {"firstName" : "John", "lastName" : "Doe"}
        response     = self.client.get(url['signup'], request_data)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_signup_incomplete(self):
        """ 
        Tests ...
              ... on signup: valid request with incomplete feilds 
        """
        request_data = {"firstName" : "John", "lastName" : "Doe", "dateOfBirth" : "0000-00-00", "email" : "john@doe.com"}
        response     = self.client.post(url['signup'], request_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_unmet(self):
        """
        Tests ...
              ... on signup: valid request with complete fields and unmet preconditions
        """
        request_data = {"firstName" : "John", "lastName" : "Doe", "dateOfBirth" : "0000-00-00", "email" : "john@doe.com", "password" : "123"}
        response     = self.client.post(url['signup'], request_data)

        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)

    def test_signup_email(self):
        """
        Tests ...
              ... on signup: valid request with complete fields, met preconditions, reachable and (non)existing email
        """
        request_data = {"firstName" : "John", "lastName" : "Doe", "dateOfBirth" : "2011-11-22", "email" : "jdoe@gmail.com", "password" : "Pass$123"}
        response_1   = self.client.post(url['signup'], request_data)
        response_2   = self.client.post(url['signup'], request_data)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_412_PRECONDITION_FAILED)

    ##### Verify Tests #####
    def test_verify_invalid(self):
        """ 
        Tests ... 
              ... on signup: valid request with complete fields, met preconditions, unreachable and nonexisting email
              ... on verify: invalid verification code 
        """
        email        = "jdoedne@gmail.com"
        password     = "wrongpassword"
        smtp_server  = "imap.gmail.com"
        smtp_port    = 933
        criteria     = "(SUBJECT 'Ployem Verification Code')"

        request_data = {"firstName" : "John", "lastName" : "Doe", "dateOfBirth" : "2011-11-22", "email" : email, "password" : "Pass$123"}
        response     = self.client.post(url['signup'], request_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertRaises(ValidationError, _read_email, email, password, smtp_server, smtp_port, criteria)

    def test_verify_valid(self):
        """ 
        Tests ... 
              ... on signup: valid request with complete fields, met preconditions, reachable and nonexisting email
              ... on verify: valid verification code 
        """
        email                = "jdummy7898@gmail.com"
        password             = "kvhurribvflkdohx"
        smtp_server          = "imap.gmail.com"
        smtp_port            = 933
        mail_box             = "[Gmail]/Spam"
        criteria             = '(SUBJECT "Account verification code")'
          
        request_1_data       = {"firstName" : "Ahmed", "lastName" : "Katary", "dateOfBirth" : "2011-11-22", "email" : email, "password" : "Pass$123"}
        response_1           = self.client.post(url['signup'], request_1_data)
        
        print("Sleeping for 15 seconds while verification email sends...")
        time.sleep(15)

        verification_message = _read_email(email, password, smtp_server, smtp_port, mail_box, criteria)
        verification_code    = _read_code(verification_message[-1])

        request_2_data       = {"email" : email, "verificationCode" : verification_code}
        response_2           = self.client.post(url['verify'], request_2_data)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_202_ACCEPTED)

    ##### Signin Tests #####
    def test_signin_nonexisting(self):
        """ 
        Tests ... 
              ... on signin: valid request for nonexisting user
        """
        request_data = {"email" : "jdoe@gmail.com", "password" : "Pass$123"}
        response     = self.client.post(url['signin'], request_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_signin_unverified(self):
        """
        Tests ... 
              ... on signin: valid request for existing  unverified user
        """
        email          = "joed@gmail.com"
        password       = "Tree8BigFoot$$"

        request_1_data = {"firstName" : "Joe", "lastName" : "Doe", "dateOfBirth" : "2001-11-22", "email" : email, "password" : password}
        response_1     = self.client.post(url['signup'], request_1_data)

        request_2_data = {"email" : email, "password" : password}
        response_2     = self.client.post(url['signin'], request_2_data)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_403_FORBIDDEN)

    def test_signin_verified(self):
        """
        Tests ... 
              ... on signin: valid request for existing  verified user
        """
        email                = "testkatary1@gmail.com"
        password             = "rtztcabzylopkxbr"
        smtp_server          = "imap.gmail.com"
        smtp_port            = 933
        mail_box             = "[Gmail]/Spam"
        criteria             = '(SUBJECT "Account verification code")'
          
        request_1_data       = {"firstName" : "Ployem", "lastName" : "Verify", "dateOfBirth" : "2001-10-27", "email" : email, "password" : "Pass$123"}
        response_1           = self.client.post(url['signup'], request_1_data)
        
        print("Sleeping for 15 seconds while verification email sends...")
        time.sleep(15)

        verification_message = _read_email(email, password, smtp_server, smtp_port, mail_box, criteria)
        verification_code    = _read_code(verification_message[-1])

        request_2_data       = {"email" : email, "verificationCode" : verification_code}
        response_2           = self.client.post(url['verify'], request_2_data)

        request_3_data = {"email" : email, "password" : "Pass$123"}
        response_3     = self.client.post(url['signin'], request_3_data)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response_3.status_code, status.HTTP_200_OK)

##### Helper Functions #####
def _read_code(message):
    """
    Read the verification code from given email message

    Inputs
        :param message: <str> verification message sent
    
    Outputs
        :returns: <str> verification code that was sent
    """
    # print("Message Recieved: '%s'" % message)
    code = message.content.split(" ")[4][:-1]
    print("\n-----------------------------------------\n")
    print("Code found: %s" % code)
    return code