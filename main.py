import boto3
import json
import os
import csv
import smtplib
import plotly.express as px
from PIL import Image
from datetime import datetime
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def get_filename_datetime():

    # Use current date to get a text file name.

    return "Prod-Infra-Checklist-" + str(datetime.now().strftime('%d-%m-%Y_%H-%M-%S')) + ".csv"

name = get_filename_datetime()

path = "path\\to\\folder\\" + name

print(path)

os.environ['AWS_DEFAULT_REGION'] = ''
os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = ''


fields = ['Name', 'id', 'State', 'Public IP', 'Private IP', 'CPU Utilization', 'Status']

with open(path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(fields)


ec2 = boto3.resource('ec2')

rowlists = []
statuses = []
statusTag = ''

for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
    instanceID = status["InstanceId"]
    instanceStatus = status["InstanceStatus"]["Status"]
    systemStatus = status["SystemStatus"]["Status"]
    statuses.append([instanceID, instanceStatus,systemStatus])


print(statuses)

j=0
for instance in ec2.instances.all():
    if instance.state['Name']=='running':
        print(instance.tags[0]['Value'])
        for instance_iterator in statuses:
            if instance.id == instance_iterator[0]:
                print(instance.id)
                if instance_iterator[j+1] == 'ok' and instance_iterator[j+2] == 'ok':
                    statusTag = 'Healthy'
                else:
                    statusTag = 'Unhealthy'

                row_list = [[instance.tags[0]['Value'], instance.id, instance.state['Name'], instance.public_ip_address, instance.private_ip_address, statusTag]]
                rowlists.append(row_list)

    else:
        statusTag = 'Stopped'
        row_list = [instance.tags[0]['Value'], instance.id, instance.state['Name'], instance.public_ip_address, instance.private_ip_address, statusTag]
        rowlists.append(row_list)
        # server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        # server.login("email", "password")
        # server.sendmail("sender email", "receiver email", "Server "+ instance.tags[0]['Value']+ " is stopped")

client = boto3.client('ec2')
s=0
imagelist=[]
client2 = boto3.client('cloudwatch')
for k in range(len(rowlists)):
    print(k)
    l = []
    n = []
    nested2 = rowlists[k]
    print(nested2)
    response = client2.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                'Name': 'InstanceId',
                'Value': nested2[1]
                },
            ],
            StartTime=datetime(2021, 11, 29, 12, 00),
            EndTime=datetime(2021, 11, 30, 12, 00 ),
            Period=300,
            Statistics=[
                'Maximum',
            ],
            Unit='Percent'
             )

    for cpu in response['Datapoints']:
        if 'Maximum' in cpu:
            l.append(cpu['Maximum'])
        if 'Timestamp' in cpu:
            n.append(cpu['Timestamp'])

    print(max(l))

    fig = px.bar(x=n, y=l)
    fig.update_layout(title=nested2[0], xaxis_title="TimeStamp" ,yaxis_title="CPU Percenteage" ,bargap=0)
    fig.update_traces(marker=dict(color='black'))
    fig.show()
    #nested2.append(max(l))
    nested2.insert(5,max(l))
   
    fig.write_image("path/to/folder/"+nested2[0]+".png")
    figname=Image.open(r'path//to//folder//'+nested2[0]+'.png')
    figname1=figname.convert('RGB')
    if k!=0:
        imagelist.append(figname1)
    else:
        figname2=figname1

figname2.save(r'path/to/folder/name.pdf',save_all=True, append_images=imagelist)
print(rowlists)
with open(path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(fields)
    for i in rowlists:
        writer.writerow(i)

subject = "An email with attachment from Python"
body = "This is an email with attachment sent from Python"
sender_email = "email@gmail.com"
receiver_email = "email@gmail.com"
password = input("Type your password and press enter:")

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email  # Recommended for mass emails

# Add body to email
message.attach(MIMEText(body, "plain"))

filename = [name,"name.pdf"]  # In same directory as script
dir_path = "path/to/folder"
for f in filename:  # add files to the message
        file_path = os.path.join(dir_path, f)
        attachment = MIMEApplication(open(file_path, "rb").read(), _subtype="txt")
        attachment.add_header('Content-Disposition','attachment', filename=f)
        message.attach(attachment)

text = message.as_string()

# Log in to server using secure context and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)
