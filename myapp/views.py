from . import models
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.models import AnonymousUser

# use django authentication for User authentication, We can also use django rest SessionAuthentication.
from django.contrib.auth import authenticate
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# use django user model
from django.contrib.auth.models import User

from django.contrib.auth import logout as django_logout

from rest_framework.authtoken.models import Token

from .Authentication import token_expire_handler


@api_view(['POST'])
@permission_classes(())
def signup(request):
    try:
        data = request.data
        data_username = data['username']
        data_password = data['password']
        data_email = data['email']
        data_phone = data['phone']
        data_confirm_password = data['cpassword']
        if data_confirm_password == data_password:
            newUser = models.MyUser.objects.create(username=data_username, email=data_email, phone=data_phone)
            newUser.set_password(data_password)
            newUser.save()
            if newUser:
                return Response({'flag': True, "message": "Created Successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({'flag': False, "message": "Something might be Wrong!"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes(())
def login(request):
    try:
        params = request.data
        user = authenticate(username=params['user'], password=params['pass'], )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            is_expired, token = token_expire_handler(token)
            tmp_response = {
                'access': token.key,
                'userid': token.user_id
            }
            return Response(tmp_response, status=status.HTTP_200_OK)
        else:
            return Response({'flag': False, "message": "Wrong username or password"},
                            status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes(())
def logout(request):
    try:
        django_logout(request)
        Token.objects.filter(key=request.headers.get('Authorization')[7:]).delete()
        return Response({"message": "Logout Successfully!"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"message": "An error occurs in logout!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    data = request.headers.get('Authorization')
    user_token = data[7:]
    rsp = {
        'username': Token.objects.get(key=user_token).user.username,
        'email': Token.objects.get(key=user_token).user.email
    }
    return Response(rsp, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_trip(request):
    data = request.data
    current_user = request.user
    dest = data["tripDestination"]
    date = data["tripDate"]
    detail = data["tripDetail"]

    try:
        current_user_trips = models.Trip.objects.filter(user_site=current_user)
        for i in current_user_trips:
            if i.destination == dest and i.date == date:
                return Response({'flag': False, 'message': 'there is another trip with the same dest and date'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        current_trip = models.Trip.objects.create(user_site=current_user, destination=dest, date=date, detail=detail)
        first_participent = models.Participant.objects.create(trip=current_trip,
                                                              user=current_user,
                                                              first_name=current_user.first_name,
                                                              last_name=current_user.last_name,
                                                              email=current_user.email,
                                                              phone=current_user.phone)
        return Response({'flag': True}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_participant(request):
    data = request.data
    current_user = request.user
    trip_dest = data["trip_dest"]
    trip_date = data["trip_date"]
    participants = data["participants"]
    try:
        current_user_trips = models.Trip.objects.filter(user_site=current_user)
        if participants:
            for i in current_user_trips:
                if i.destination == trip_dest and str(i.date) == trip_date:
                    current_trip = i
                    for j in participants:
                        if j['user_name']:
                            participant_user = models.MyUser.objects.get(username=j['user_name'])
                            if not models.Participant.objects.filter(trip=current_trip, user=participant_user):
                                new_participant = models.Participant.objects.create(trip=current_trip,
                                                                                    user=participant_user,
                                                                                    first_name=j['first_name'],
                                                                                    last_name=j['last_name'],
                                                                                    email=j['email'],
                                                                                    phone=j['phone'])
                                new_table = models.Table.objects.create(participant=new_participant,
                                                                        title=new_participant.first_name + ' ' + new_participant.last_name + 'table')
                        else:
                            new_participant = models.Participant.objects.create(trip=current_trip,
                                                                                first_name=j['first_name'],
                                                                                last_name=j['last_name'],
                                                                                email=j['email'],
                                                                                phone=j['phone'])
                            new_table = models.Table.objects.create(participant=new_participant,
                                                                    title=new_participant.first_name + ' ' + new_participant.last_name + 'table')
                    return Response({'flag': True}, status=status.HTTP_200_OK)
            return Response({'flag': False, 'message': 'there is no trip with this title'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({'flag': True, 'message': 'participants list is empty'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_participant(request):
    data = request.data
    current_user = request.user
    participant_user_name = data["user_name"]
    try:
        users = models.MyUser.objects.filter()
        for i in users:
            if participant_user_name == i.username:
                return Response({'flag': True, 'message': 'valid user_name'}, status=status.HTTP_200_OK)
        return Response({'flag': False, 'message': 'invalid user_name'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_trips(request):
    data = request.data
    current_user = request.user
    try:
        user_participants = models.Participant.objects.filter(user=current_user)
        trips = {}
        counter = 0
        for i in user_participants:
            counter = counter + 1
            trips.update({counter: {'dest': i.trip.destination,
                                    'date': i.trip.date,
                                    'detail': i.trip.detail}})
        trips.update({'number': counter})
        trips.update({'flag': True})
        return Response(trips, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_table(payerID):
    try:
        payer = models.Participant.objects.get(id=payerID)
        table = models.Table.objects.get(participant=payer)
        return table
    except Exception as e:
        return False


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_transaction(request):
    data = request.data
    current_user = request.user
    trip_title = data["trip_title"]
    payerID = data["payerID"]
    transaction_title = data["transaction_title"]
    fee = data["fee"]
    try:
        current_user_trips = models.Trip.objects.filter(user_site=current_user)
        payer = models.Participant.get(id=payerID)
        for i in current_user_trips:
            if i.title == trip_title:
                current_trip = i
                new_transaction = models.Transaction.objects.create(trip=current_trip, payer=payer,
                                                                    title=transaction_title, fee=fee)
                current_table = get_table(payerID)
                if current_table:
                    new_bedehkar = models.Bedehkar.objects.create(table=current_table, amount=fee)
                    return Response({'flag': True}, status=status.HTTP_200_OK)
                else:
                    return Response({'flag': False, 'message': 'there is no Table for the Participant with this ID'},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({'flag': False, 'message': 'there is no trip with this title'},
                        status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
