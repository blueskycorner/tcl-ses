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
emailCcEnvName = 'emailCc'
tclCardObjectKeyEnvName = 'tclCardObjectKey'
prefixEnvName = 'prefix'
errorTopicArnParamName = 'errorTopicArn'
emailFrom = os.getenv(emailFromEnvName)
emailTo = os.getenv(emailToEnvName)
emailCc = os.getenv(emailCcEnvName)
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

def getMonth(bucket, fileKey):
    month = None

    try:
        rekognition = boto3.client("rekognition")
        response = rekognition.detect_text(
            Image={
                "S3Object": {
                    "Bucket": bucket,
                    "Name": fileKey,
                }
            },
        )

        monthNumber = None
        reg = '01\/([0-1][0-9])\/[0-9][0-9]'
        for item in response['TextDetections']:
            if (item['Type'] == 'WORD') and (int(item['Confidence']) >= 99):
                month_pattern = re.compile(reg)
                res = month_pattern.search(item['DetectedText'])
                if (res is not None):
                    monthNumber = res.group(1)
                    print(item['DetectedText'])

        if monthNumber is not None:     
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
        else:
            raise Exception('Impossible to extract the month')
    except Exception as e:
        print("Error while extracting month")
        raise(e)

    return month

def sendMail(emailFrom, emailTo, emailCc, invoiceFilename, tclCardObjectKey, month):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = emailFrom

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = emailTo

    CC = emailCc

    # The subject line for the email.
    SUBJECT = "Remboursement transport en commun"

    # The full path to the file that will be attached to the email.
    ATTACHMENT_INVOICE = prefix + invoiceFilename
    ATTACHMENT_TCLCARD = prefix + tclCardObjectKey

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "Bonjour,\nVoici un justificatif d'abonnement de transport en commun pour le mois " + month + "\n\nBien cordialement.\n\nBenjamin EHLERS\n\n"

    # The HTML body of the email.
    BODY_HTML = """\
    <html>
    <head></head>
    <body>
    Bonjour<br><br>
    Voici un justificatif d'abonnement de transport en commun pour le mois 
    """
    
    BODY_HTML += month
    BODY_HTML += '.'

    BODY_HTML += """\
    <br><br>
    Bien cordialement.<br>
    <br><font size="1" color="#4f4f4f" face="Century Gothic">PS: je ne travaille
    pas le mercredi.</font>
    <br><img src="https://s3.amazonaws.com/tcl-invoices-dev/hardis.jpg" style="border:0px solid" data-image-whitelisted="" class="CToWUd">
    <br><font size="2" color="#4f4f4f" face="Century Gothic"><b>Benjamin EHLERS
    | Architecte Cloud</b></font>
    <br><font size="1" color="#4f4f4f" face="Century Gothic">06 20 39 78 61 | <a href="mailto:benjamin.ehlers@hardis.fr" target="_blank">benjamin.ehlers@hardis.fr</a></font>
    <br><font size="1" color="#4f4f4f" face="Century Gothic">HARDIS GROUP - Immeuble
    Le Seven, 69 Av Tony Garnier – 69007 LYON</font>
    <br><a href="http://www.hardis-group.com" target="_blank" data-saferedirecturl="https://www.google.com/url?q=http://www.hardis-group.com&amp;source=gmail&amp;ust=1551193276200000&amp;usg=AFQjCNFJCmG3AY7VNcZfgs9UY_FPC3uOBg"><font size="1" color="blue" face="Century Gothic">www.hardis-group.com</font></a><font size="1" color="#4f4f4f" face="Century Gothic">
    - @GroupeHardis</font><div class="yj6qo"></div><div class="adL">
    </div></div></div>
    </body>
    </html>
    """

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
    msg['Cc'] = CC

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET) 

    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

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
                RECIPIENT,CC
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

        month = getMonth(bucket, fileKey)
        
        print("bucket: " + bucket)
        print("fileKey: " + fileKey)
        print("emailFrom: " + emailFrom)
        print('emailTo: ' + emailTo)
        print('emailCc: ' + emailCc)
        print('tclCardObjectKey: ' + tclCardObjectKey)
        print('month: ' + month)
        print('invoiceFilename: ' + invoiceFilename)

        # Download files
        s3 = boto3.resource('s3')
        s3.Bucket(bucket).download_file(fileKey, prefix + invoiceFilename)
        s3.Bucket(bucket).download_file(tclCardObjectKey, prefix + tclCardObjectKey)
        
        sendMail(emailFrom, emailTo, emailCc, invoiceFilename, tclCardObjectKey, month)
    except Exception as e:
        print(str(e))
        error = {"message": str(e)}
        sendError(error)

def sendError(message):

    print(message)
    sns = boto3.client('sns')
    
    errorTopicArn=os.getenv(errorTopicArnParamName)
    response = sns.publish(
        TargetArn=errorTopicArn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json')
    print(response)

if __name__ == "__main__":
    try:
        # For local testing
        event={
            "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": "2019-02-15T09:17:06.421Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                "principalId": "AWS:AIDAINR7FHESBZ5YUQE6A"
                },
                "requestParameters": {
                "sourceIPAddress": "90.102.110.89"
                },
                "responseElements": {
                "x-amz-request-id": "3CC425E9DDCC80EA",
                "x-amz-id-2": "w0HpU9Vg4kTQlq8AXhbqR9r+7qqQHlGgeplLgH6WzmQkyySMvj2CisVHJzuQFKOBEqtco9aBdyA="
                },
                "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "11bca8a7-6071-4b45-bd92-1cfbd7046148",
                "bucket": {
                    "name": "hardis-tcl-invoices-dev",
                    "ownerIdentity": {
                    "principalId": "A5769J9JPS9SL"
                    },
                    "arn": "arn:aws:s3:::hardis-tcl-invoices-dev"
                },
                "object": {
                    "key": "invoices/2019-02_TCL.jpg",
                    "size": 1995425,
                    "eTag": "d94c72c512af4f2ea313a84a29f0b4b6",
                    "sequencer": "005C668392525083D7"
                }
                }
            }
            ]
        }
        sendTclInvoice(event, '')
    except Exception as e:
        print(str(e))