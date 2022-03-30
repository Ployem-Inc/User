"""
user views
"""
from .models import CustomUser
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from user_utils.view_helpers import _is_subset
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout

@api_view(['POST'])
def sign_up(request, *args, **kwargs) -> Response:
    """
    Signs a user up

    Inputs    
        :param request: <HttpRequest> containing a user's firstName, lastName, dateOfBirth (YYYY-MM-DD), email and password

    Outputs
        :returns: Status ...
                         ... HTTP_201_CREATED if the user is signed up successfully
                         ... HTTP_403_FORBIDDEN if email is unreachable 
                         ... HTTP_412_PRECONDITION_FAILED if one ore more of the request fields don't meet their precondition(s)  
    """
    signup_fields = ["firstName", "lastName", "dateOfBirth", "email", "password"]
    user_status   = _is_subset(signup_fields, request.data.keys())

    if user_status == status.HTTP_200_OK:
        email         = request.data['email']
        password      = request.data['password']
        last_name     = request.data['lastName']
        first_name    = request.data['firstName']
        date_of_birth = request.data['dateOfBirth']

        user, user_status  = CustomUser.objects.create(first_name, last_name, date_of_birth, email, password)

    return Response(status = user_status)

@api_view(['POST'])
def send_verify(request, *args, **kwargs) -> HttpResponse:
    """
    Sends a verification code to email

    Inputs    
        :param request: <HttpRequest> with email of user to send the verification to
    
    Outputs
        :returns: Status ... HTTP_200_OK if the user exists 
                         ... HTTP_404_NOT_FOUND if the user does not exists 
    """
    verify_fields         = ["email"]
    user_status           = _is_subset(verify_fields, request.data.keys())

    if user_status == status.HTTP_200_OK:
        email = request["request"]
        try: 
            user  = CustomUser.objects.get(email = email)
            user.send_verification_code()  
        except ObjectDoesNotExist:
            user_status = status.HTTP_404_NOT_FOUND
    
    return Response(status = user_status)

@api_view(['POST'])
def confirm_verify(request, *args, **kwargs) -> HttpResponse:
    """
    Verifies a user by checking the verification code they provided against the code sent 
    in the database

    Definitions
        verify
            confirm identity
 
            Given an email, verify it exists

    Inputs    
        :param request: <HttpRequest> containing a user's email and the verificationCode they provided

    Outputs
        :returns: Status ...
                         ... HTTP_202_ACCEPTED if the user is verfied
                         ... HTTP_403_FORBIDDEN if the user is not verified 
    """
    verify_fields         = ["email", "verificationCode"]
    user_status           = _is_subset(verify_fields, request.data.keys())

    if user_status == status.HTTP_200_OK:
        email             = request.data['email']
        verification_code = request.data['verificationCode']
        user              = CustomUser.objects.get(email = email)
    
        if verification_code != "P-" + str(user.verification_code)[:8]:
            user_status   = status.HTTP_403_FORBIDDEN
        else:
            user.verified = True
            user.save()
            user_status   = status.HTTP_202_ACCEPTED
    
    return Response(status = user_status)

@api_view(['POST'])
def sign_in(request, *args, **kwargs) -> HttpResponse:
    """
    Signs a user in

    Definitions
        authenticate
            verify identity

            Given an email and password we authenticate that they match the credentials stored in the database

    Inputs    
        :param request: <HttpRequest> containing a user's email and password

    Outputs
        :returns: Status ...
                         ... HTTP_200_OK if the user is authenticated
                         ... HTTP_403_FORBIDDEN if the user is unauthenticated 
    """
    verify_fields         = ["email", "password"]
    user_status           = _is_subset(verify_fields, request.data.keys())

    if user_status == status.HTTP_200_OK:
        email    = request.data['email']
        password = request.data['password']
        user     = authenticate(username = email, password = password)
    
        if user is None:
            print("User not found")
            user_status = status.HTTP_403_FORBIDDEN
        elif not user.verified:
            print("User not verified")
            user_status = status.HTTP_403_FORBIDDEN
        else:
            login(request, user)
            user_status = status.HTTP_200_OK
    
    return Response(status = user_status)
    
@api_view(['POST'])
def sign_out(request, *args, **kwargs) -> HttpResponse: 
    """
    Signs a user in
     
    Inputs    
       :param request: <HttpRequest> to sign a user out containing the user's email

    Outputs
       :returns: Status … 
                        … HTTP_200_OK if the user is signed out
                        … HTTP_403_FORBIDDEN if the user is not signed out
    """
    verify_fields         = ['email']
    user_status           = _is_subset(verify_fields, request.data.keys())

    if user_status == status.HTTP_200_OK: logout(request)
    
    return Response(status = user_status)