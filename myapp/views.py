# use django authentication for User authentication, We can also use django rest SessionAuthentication.
from django.contrib.auth import authenticate
from django.contrib.auth import logout as django_logout
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import models
from .Authentication import token_expire_handler


@api_view(['POST'])
@permission_classes(())
def signup(request):
    try:
        data = request.data
        data_username = data['username']
        data_password = data['password']
        first_name = data['firstName']
        last_name = data['lastName']
        data_confirm_password = data['cpassword']
        if data_confirm_password == data_password:
            newUser = models.MyUser.objects.create(username=data_username, first_name=first_name, last_name=last_name)
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
    current_user = request.user
    rsp = {
        'username': current_user.username,
        'firstName': current_user.first_name,
        'lastName': current_user.last_name,
    }
    return Response(rsp, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_trip(request):
    data = request.data
    thisUser = request.user
    dest = data["tripDestination"]
    date = data["tripDate"]
    detail = data["tripDetail"]
    try:
        current_user = models.MyUser.objects.get(id=thisUser.id)
        current_user_trips = models.Trip.objects.filter(user_site=current_user)
        for i in current_user_trips:
            if i.destination == dest and i.date == date:
                return Response({'flag': False, 'message': 'there is another trip with the same destination and date'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        current_trip = models.Trip.objects.create(user_site=current_user, destination=dest, date=date, detail=detail)
        first_participant = models.Participant.objects.create(trip=current_trip,
                                                              user=current_user,
                                                              first_name=current_user.first_name,
                                                              last_name=current_user.last_name,
                                                              email=current_user.email,
                                                              phone=current_user.phone)
        new_table = models.Table.objects.create(participant=first_participant,
                                                title=first_participant.first_name + ' ' + first_participant.last_name + ' table')
        return Response({'flag': True, 'newTripId': current_trip.id}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_participant(request, pk):
    data = request.data
    current_user = request.user
    participants = data["participants"]
    try:
        current_trip = models.Trip.objects.get(id=pk)
        if current_user == current_trip.user_site:
            if participants:
                for j in participants:
                    if j['user_name']:
                        participant_user = models.MyUser.objects.get(username=j['user_name'])
                        if not models.Participant.objects.filter(trip=current_trip, user=participant_user):
                            new_Participant = models.Participant.objects.create(trip=current_trip,
                                                                                user=participant_user,
                                                                                first_name=participant_user.first_name,
                                                                                last_name=participant_user.last_name)
                            new_table = models.Table.objects.create(participant=new_Participant,
                                                                    title=new_Participant.first_name + ' ' + new_Participant.last_name + ' table')

                            if j['email']:
                                new_Participant.email = j['email']
                            else:
                                new_Participant.email = participant_user.email
                            if j['phone']:
                                new_Participant.phone = j['phone']
                            else:
                                new_Participant.phone = participant_user.phone
                            new_Participant.save()
                    else:
                        new_Participant = models.Participant.objects.create(trip=current_trip,
                                                                            first_name=j['first_name'],
                                                                            last_name=j['last_name'],
                                                                            email=j['email'],
                                                                            phone=j['phone'])
                        new_table = models.Table.objects.create(participant=new_Participant,
                                                                title=new_Participant.first_name + ' ' + new_Participant.last_name + 'table')
                return Response({'flag': True}, status=status.HTTP_200_OK)
            return Response({'flag': True, 'message': 'participants list is empty'}, status=status.HTTP_200_OK)
        else:
            return Response({'flag': False, 'message': 'you are not leader of this trip'}, status=status.HTTP_200_OK)
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
                                    'detail': i.trip.detail,
                                    'id': i.trip.id}})
        trips.update({'number': counter})
        trips.update({'flag': True})
        return Response(trips, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_info(request, pk):
    current_user = request.user
    try:
        current_trip = models.Trip.objects.get(id=pk)
        temp_participants = models.Participant.objects.filter(trip=current_trip)
        for j in temp_participants:
            if current_user == j.user:
                rsp = {'leader': current_trip.user_site.username,
                       'dest': current_trip.destination,
                       'date': current_trip.date,
                       'detail': current_trip.detail
                       }
                participants = {}
                counter = 0
                for i in temp_participants:
                    counter = counter + 1

                    if i.user:
                        userName = i.user.username
                    else:
                        userName = 'کاربر ثبت نشده'

                    if i.phone:
                        phone = i.phone
                    else:
                        phone = 'شماره تماس ثبت نشده'

                    if i.email:
                        email = i.email
                    else:
                        email = 'ایمیل ثبت نشده'

                    participants.update({counter: {'fullName': i.first_name + ' ' + i.last_name,
                                                   'username': userName,
                                                   'email': email,
                                                   'phone': phone,
                                                   'id': i.id}})
                rsp.update({'participants': participants,
                            'number': counter})
                return Response(rsp, status=status.HTTP_200_OK)

        return Response({'flag': False, 'message': 'you are not participant in this trip'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_transactions(request, pk):
    current_user = request.user
    try:
        current_trip = models.Trip.objects.get(id=pk)
        temp_transactions = models.Transaction.objects.filter(trip=current_trip)
        rsp = {}
        counter = 0
        for j in temp_transactions:
            counter = counter + 1
            rsp.update({counter: {'payer': j.payer.first_name + ' ' + j.payer.last_name,
                                  'cost': j.fee,
                                  'title': j.title}})
        rsp.update({'number': counter})
        rsp.update({'flag': True})
        return Response(rsp, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_trip_info(request, pk):
    data = request.data
    current_user = request.user
    dest = data["tripDestination"]
    date = data["tripDate"]
    detail = data["tripDetail"]
    try:
        current_trip = models.Trip.objects.get(id=pk)
        if current_trip.user_site == current_user:
            current_trip.date = date
            current_trip.detail = detail
            current_trip.destination = dest
            current_trip.save()
            return Response({'flag': True}, status=status.HTTP_200_OK)
        return Response({'flag': False, 'message': 'you are not leader of this trip'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_participant(request, pk):
    try:
        current_trip = models.Trip.objects.get(id=pk)
        participants = models.Participant.objects.filter(trip=current_trip)
        rsp = []
        for i in participants:
            rsp.append({'value': i.id, 'viewValue': i.first_name + ' ' + i.last_name})
        return Response(rsp, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_transaction(request):
    data = request.data
    current_user = request.user
    trip_id = data["trip_id"]
    payer_id = data["payerID"]
    transaction_title = data["transaction_title"]
    cost = data["cost"]
    try:
        if request.user == models.Trip.objects.get(id=trip_id).user_site:
            current_trip = models.Trip.objects.get(id=trip_id)
            payer_participant = models.Participant.objects.get(id=payer_id)
            new_transaction = models.Transaction.objects.create(trip=current_trip,
                                                                payer=payer_participant,
                                                                title=transaction_title,
                                                                fee=cost)
            current_table = models.Table.objects.get(participant=payer_participant)
            new_bedehkar = models.Bedehkar.objects.create(table=current_table, amount=cost)
            return Response({'flag': True}, status=status.HTTP_200_OK)
        else:
            return Response({'flag': False}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes(())
def calculate_dong(request, pk):
    user = request.user
    try:
        current_trip = models.Trip.objects.get(id=pk)
        participants = models.Participant.objects.filter(trip=current_trip)
        participants_number = participants.count()
        sum = 0
        for participant in participants:
            participant_table = models.Table.objects.get(participant=participant)
            bedehkars = models.Bedehkar.objects.filter(table=participant_table)
            for bedehkar in bedehkars:
                sum = sum + bedehkar.amount
        dong = sum / participants_number
        debtors = {}
        creditors = {}
        for participant in participants:
            participant_table = models.Table.objects.get(participant=participant)
            bedehkars = models.Bedehkar.objects.filter(table=participant_table)
            sum_bedehkar = 0
            for bedehkar in bedehkars:
                sum_bedehkar = sum_bedehkar + bedehkar.amount
            bestankar = sum_bedehkar - dong
            # new_bestankar = models.Bestankar.objects.create(table=participant_table, amount=bestankar)
            if bestankar < 0:
                debtors.update({participant.id: bestankar})
            elif bestankar > 0:
                creditors.update({participant.id: bestankar})
        rsp = {}
        counter = 0

        for debtor in debtors:
            bedehkarFullName = models.Participant.objects.get(id=debtor)
            for creditor in creditors:
                talabkarFullname = models.Participant.objects.get(id=creditor)
                if abs(debtors[debtor]) == 0:
                    pass
                if creditors[creditor] == 0:
                    pass
                elif abs(debtors[debtor]) > creditors[creditor]:
                    cost = creditors[creditor]
                    if cost != 0:
                        debtors[debtor] = debtors[debtor] + creditors[creditor]
                        creditors[creditor] = 0
                        rsp.update({counter: {'Bname': bedehkarFullName.first_name + ' ' + ' ' + bedehkarFullName.last_name,
                                              'cost': cost,
                                              'Tname': talabkarFullname.first_name + ' ' + talabkarFullname.last_name}})
                        counter = counter + 1
                elif abs(debtors[debtor]) == creditors[creditor]:
                    cost = creditors[creditor]
                    if cost != 0:
                        debtors[debtor] = abs(debtors[debtor]) - creditors[creditor]
                        creditors[creditor] = 0
                        rsp.update({counter: {'Bname': bedehkarFullName.first_name + ' ' + ' ' + bedehkarFullName.last_name,
                                              'cost': cost,
                                              'Tname': talabkarFullname.first_name + ' ' + talabkarFullname.last_name}})
                        counter = counter + 1
                    # rsp.update({counter: bedehkarFullName.first_name + ' ' + ' ' + bedehkarFullName.last_name +
                    #             ' ' + str(cost) + ' تومان بدهد به' +
                    #             talabkarFullname.first_name + ' ' + talabkarFullname.last_name})
                elif abs(debtors[debtor]) < creditors[creditor]:
                    cost = abs(debtors[debtor])
                    if cost != 0:
                        creditors[creditor] = creditors[creditor] - abs(debtors[debtor])
                        debtors[debtor] = 0
                        rsp.update({counter: {'Bname': bedehkarFullName.first_name + ' ' + ' ' + bedehkarFullName.last_name,
                                              'cost': cost,
                                              'Tname': talabkarFullname.first_name + ' ' + talabkarFullname.last_name}})
                        counter = counter + 1
                    # rsp.update({counter: bedehkarFullName.first_name + ' ' + ' ' + bedehkarFullName.last_name +
                    #             ' ' + str(cost) + ' تومان بدهد به' +
                    #             talabkarFullname.first_name + ' ' + talabkarFullname.last_name})
        rsp.update({'number': counter})
        return Response(rsp, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False, 'message': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
