import json
import os
import boto3
import re
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from botocore.exceptions import ClientError

emailFromEnvName = 'emailFrom'
emailToEnvName = 'emailTo'
tclCardObjectKeyEnvName = 'tclCardObjectKey'
prefixEnvName = 'prefix'
emailFrom = os.getenv(emailFromEnvName)
emailTo = os.getenv(emailToEnvName)
tclCardObjectKey = os.getenv(tclCardObjectKeyEnvName)
prefix = os.getenv(prefixEnvName)
# emailFrom = 'benjamin.ehlers@hardis.fr' #os.getenv(emailFromEnvName)
# emailTo = 'benjamin.ehlers@hardis.fr' #os.getenv(emailToEnvName)
# tclCardObjectKey = 'CarteTCL.jpg' #os.getenv(tclCardObjectKeyEnvName)

def getInvoiceFilename(fileKey):
    invoiceFilename = ''

    try:
        reg1 = 'invoices\/(.*)'
        file_pattern = re.compile(reg1)
        invoiceFilename = file_pattern.search(fileKey).group(1)
    except Exception as e:
        print("error while getting invoide filename")
        raise(e)
    
    return invoiceFilename

def getMonth(fileKey):
    month = ''

    try:
        reg = '20[0-9][0-9]-([0-1][0-9])_TCL'
        month_pattern = re.compile(reg)
        monthNumber = month_pattern.search(fileKey).group(1)
        print('monthNumber: ' + monthNumber)
        
        if (monthNumber == '01'):
            month = "de Janvier"
        elif (monthNumber == '02'):
            month = "de Février"
        elif (monthNumber == '03'):
            month = "de Mars"
        elif (monthNumber == '04'):
            month = "d'Avril"
        elif (monthNumber == '05'):
            month = "de Mai"
        elif (monthNumber == '06'):
            month = "de Juin"
        elif (monthNumber == '07'):
            month = "de Juillet"
        elif (monthNumber == '08'):
            month = "d'Août"
        elif (monthNumber == '09'):
            month = "de Septembre"
        elif (monthNumber == '10'):
            month = "d'Octobre"
        elif (monthNumber == '11'):
            month = "de Novembre"
        elif (monthNumber == '12'):
            month = "de Décembre"
    except Exception as e:
        print("Error while extracting month")
        raise(e)

    return month

def sendMail(emailFrom, emailTo, invoiceFilename, tclCardObjectKey, month):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = emailFrom

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = emailTo

    # The subject line for the email.
    SUBJECT = "Remboursement transport en commun"

    # The full path to the file that will be attached to the email.
    ATTACHMENT_INVOICE = prefix + invoiceFilename
    ATTACHMENT_TCLCARD = prefix + tclCardObjectKey

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "Bonjour,\nVoici un justificatif d'abonnement de transport en commun pour le mois " + month + "\n\nBien cordialement.\n\nBenjamin EHLERS\n\n"

    # The character encoding for the email.
    CHARSET = "utf-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses')

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT 
    msg['From'] = SENDER 
    msg['To'] = RECIPIENT

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)

    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    # msg_body.attach(htmlpart)

    # Define the attachment_INVOICE part and encode it using MIMEApplication.
    att1 = MIMEApplication(open(ATTACHMENT_INVOICE, 'rb').read())
    att2 = MIMEApplication(open(ATTACHMENT_TCLCARD, 'rb').read())

    # Add a header to tell the email client to treat this part as an attachment_INVOICE,
    # and to give the attachment_INVOICE a name.
    att1.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT_INVOICE))
    att2.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT_TCLCARD))

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    # Add the attachment_INVOICE to the parent container.
    msg.attach(att1)
    msg.attach(att2)
    #print(msg)
    try:
        #Provide the contents of the email.
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=[
                RECIPIENT
            ],
            RawMessage={
                'Data':msg.as_string(),
            }
            # ConfigurationSetName=CONFIGURATION_SET
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def sendTclInvoice(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        fileKey = event['Records'][0]['s3']['object']['key']

        invoiceFilename = getInvoiceFilename(fileKey)

        month = getMonth(fileKey)
        
        print("bucket: " + bucket)
        print("fileKey: " + fileKey)
        print("emailFrom: " + emailFrom)
        print('emailTo: ' + emailTo)
        print('tclCardObjectKey: ' + tclCardObjectKey)
        print('month: ' + month)
        print('invoiceFilename: ' + invoiceFilename)

        # Download files
        s3 = boto3.resource('s3')
        s3.Bucket(bucket).download_file(fileKey, prefix + invoiceFilename)
        s3.Bucket(bucket).download_file(tclCardObjectKey, prefix + tclCardObjectKey)
        
        sendMail(emailFrom, emailTo, invoiceFilename, tclCardObjectKey, month)
    except Exception as e:
        print(str(e))