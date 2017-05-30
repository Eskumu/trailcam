import os
import imaplib

from django.core.files.base import ContentFile

import setup
import email

parsedate_to_datetime = email.utils.parsedate_to_datetime


from trailcam.settings import BASE_DIR
from background_task import background

from .models import Photo
from django.utils import timezone


def readmail():

    detach_dir = os.path.join(BASE_DIR,"media",'catche')
    mail = imaplib.IMAP4_SSL(setup.SMTP_SERVER)
    mail.login(setup.FROM_EMAIL, setup.FROM_PWD)

    mail.select("inbox")

    type, data = mail.search(None, "ALL",'(UNSEEN)')
    mail_ids = data[0]
    if len(mail_ids) == 0:
        print("LEN 0")
        return None

    id_list = mail_ids.split()
    first_email_id = int(id_list[0])
    latest_email_id = int(id_list[-1])

    for i in range(latest_email_id, first_email_id, -1):
        typ, data = mail.fetch(str(i), '(RFC822)')

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subjet = msg['subject']
                email_from = msg['from']
                email_date = parsedate_to_datetime(msg['date'])


                if msg.get_content_maintype() != 'multipart':
                    continue
                print("HELLO")
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue

                    if part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()
                    counter = 1

                    if not filename:
                        filename ='part-%03d%s' %(counter,'bin')


                    att_path =os.path.join(detach_dir,filename)

                    while os.path.isfile(att_path):
                        counter += 1
                        if counter == 2:
                            filename = '%03d%s' % (counter, filename)
                        else:
                            filename = '%03d%s' % (counter, filename[3:])
                        att_path = os.path.join(detach_dir,filename)

                    if not os.path.isfile(att_path):
                        fp = open(att_path, 'wb')
                        payload= (part.get_payload(decode=True))
                        print(payload)
                        # payload is bytes (isinstance(payload,bytes)) == True
                        # payload "b'\xff\xd8\xff\xdb\x00\x84\x00\x14\x0e\x0f\x12"
                        fp.write(part.get_payload(decode=True))
                        photo = Photo(
                            title = email_subjet,
                            date = email_date)
                        photo.post_img.save(filename,ContentFile(part.get_payload(decode=True)))
                        photo.save()
                        fp.close()
                        mail.store(str(i),'+FLAGS','\SEEN')
                        print("Mail on suletud")

@background(schedule=60)
def readmail_schedule():
    readmail()

