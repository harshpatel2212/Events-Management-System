from django.http import HttpResponse
from django.template import loader

# To send Mail and SMS Msg
# from django.core.mail import send_mail
# from twilio.rest import Client        
# from EventManager import settings

from EM_App.models import Event, Participant

# To add neccesary date check-up while recieving form details
import datetime as dt


def index(request):
    template = loader.get_template('index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))


def participant(request):
    template = loader.get_template('participant.html')
    date_t = dt.datetime.now().date()
    time_t = dt.datetime.now().time()

    # Sort the events getting displayed on Participants page sorted by earlier deadline first
    event_database = Event.objects.all().order_by('deadlineDate', 'fromDate', 'fromTime')
    e_data = []
    for e in event_database:
        if e.deadlineDate > date_t or e.deadlineDate == date_t and e.deadlineTime > time_t:
            e_data.append(e)
        else:
            continue
    context = {
        'events': e_data,
    }

    # Collect data from Form and add it to database by creating an instance of participants
    if request.method == 'POST':
        participant_obj = Participant(
            name=request.POST['participantName'],
            cno=request.POST['cno'],
            email=request.POST['email'],
            event=request.POST['event'],
            regType=request.POST['regType'],
        )
        if participant_obj.regType == 'Individual':
            if request.POST['groupSize'] != '1':
                return error(request, 'Invalid Group size for Individual Registration.')        # redirect to error page via verifying groupSize for indiviual participants
            else:
                participant_obj.groupSize = request.POST['groupSize']
        else:
            participant_obj.groupSize = request.POST['groupSize']

        p_database = Participant.objects.all()
        for p in p_database:
            if participant_obj.email == p.email and participant_obj.event == p.event:       # Unique Email check
                error_msg = 'Email already registered for the selected event!'
                return error(request, error_msg)
            else:
                continue
        participant_obj.save()

        # Twilio SMS Code
        # client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
        # client.messages.create(
        #     body="\n\nThank you for participating in " + participant_obj.event + ".\n\nTickBird\nEventManager Web App",
        #     from_=settings.TWILIO_NUMBER,
        #     to=str(participant_obj.cno)
        # )
        return success(request, 'Registration Successful!!\nSMS has been send to the registered contact number.')           # redirect to success page
    return HttpResponse(template.render(context, request))


def event(request):
    template = loader.get_template('event.html')

    # Collect data from Form and add it to database by creating an instance of events
    if request.method == 'POST':
        e_obj = Event(
            eventName=request.POST['eventName'],
            description=request.POST['description'],
            location=request.POST['location'],
            fromDate=request.POST['fromDate'],
            fromTime=request.POST['fromTime'],
            toDate=request.POST['toDate'],
            toTime=request.POST['toTime'],
            deadlineDate=request.POST['deadlineDate'],
            deadlineTime=request.POST['deadlineTime'],
            email=request.POST['email'],
            password=request.POST['password']
        )
        date_t = str(dt.datetime.now().date())
        time_t = str(dt.datetime.now().time())
        if date_t < e_obj.fromDate and date_t < e_obj.toDate and (
                date_t < e_obj.deadlineDate or (date_t == e_obj.deadlineDate and time_t < e_obj.deadlineTime)):
            if e_obj.toDate > e_obj.fromDate or (e_obj.toDate == e_obj.fromDate and e_obj.toTime > e_obj.fromTime):
                e_obj.save()

                # GMAIL SMTP MAIL Code
                # subject = '[EVENTMANAGER] ' + e_obj.eventName + ' Registered Successfully!'
                # content = 'Hello Host,\n\n' + 'The details of the event are as follows:\n\n' \
                #           + 'Event ID - ' + str(e_obj.id) + '\n' \
                #           + 'Description - ' + str(e_obj.description) + '\n' \
                #           + 'Venue - ' + str(e_obj.location) + '\n' \
                #           + 'Timeline - ' + 'From ' + str(e_obj.fromDate) + ', ' + str(e_obj.fromTime) + ' to ' + str(e_obj.toDate) + ', ' + str(e_obj.toTime) + '\n' \
                #           + 'Registration Deadline - ' + str(e_obj.deadlineDate) + ', ' + str(e_obj.deadlineTime) + '\n' \
                #           + 'Event Password - ' + str(e_obj.password) + '\n' \
                #           + '\n\nThank you for using Event Manager.\n' \
                #           + 'Regards,\nTickBird\nEventManager WEB APP'
                # to = [e_obj.email]
                # send_mail(
                #     subject,                          # subject
                #     content,                          # content
                #     settings.EMAIL_HOST_USER,         # from
                #     to,                               # to
                # )
                return success(request, 'Email sent Successfully!!!')
            else:
                return error(request, 'End time less than Start time')
        else:
            return error(request, 'Invalid date and time of the event')
    context = {
    }
    return HttpResponse(template.render(context, request))


def dashboard(request):
    template = loader.get_template('dashboard.html')
    authorized = False

    # Authorization for event dashboard
    if request.method == 'POST':
        eventId = int(request.POST['eventId'])
        pwd = request.POST['password']
        mail = request.POST['email']
        event_database = Event.objects.all()
        for e_obj in event_database:
            if e_obj.id == eventId : 
                if e_obj.password == pwd and e_obj.email == mail:
                    authorized = True
                    p_data = []
                    e_name = e_obj.eventName
                    p_database = Participant.objects.all()
                    for p_obj in p_database:
                        if p_obj.event == e_name:
                            p_data.append(p_obj)
                        else:
                            continue
                    context = {
                        'participants': p_data, 
                        'valid': authorized,
                    }
                    return HttpResponse(template.render(context, request)) 
                else:
                    return error(request, 'Incorrect Password!!')
        return error(request, 'Invalid Event ID')
    context = {
    }
    return HttpResponse(template.render(context, request))


def error(request, error_msg):
    template = loader.get_template('error.html')
    context = {
        'messages': error_msg
    }
    return HttpResponse(template.render(context, request))


def success(request, success_msg):
    template = loader.get_template('success.html')
    context = {
        'messages': success_msg
    }
    return HttpResponse(template.render(context, request))
