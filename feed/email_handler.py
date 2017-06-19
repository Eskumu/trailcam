import os
import imaplib
from uuid import uuid4

from django.core.files.base import ContentFile

import setup
import email

parsedate_to_datetime = email.utils.parsedate_to_datetime

from trailcam.settings import BASE_DIR
from background_task import background

from .models import Photo


def readmail():
    detach_dir = os.path.join(BASE_DIR, "media", 'pictures', "thumb")
    mail = imaplib.IMAP4_SSL(setup.SMTP_SERVER)
    mail.login(setup.FROM_EMAIL, setup.FROM_PWD)

    mail.select("inbox")

    # Filter unseen messages
    type, data = mail.search(None, "ALL", '(UNSEEN)')
    mail_ids = data[0]
    if len(mail_ids) == 0:
        print("LEN 0")
        return None

    # Read all new messages
    for num in data[0].split():
        typ, data = mail.fetch(str(int(num)), '(RFC822)')

        msg = email.message_from_bytes(data[0][1])
        email_subjet = msg['subject']
        email_from = msg['from']
        email_date_pre = msg['date']
        email_date = parsedate_to_datetime(email_date_pre)

        print(email_subjet, email_from, email_date)
        if msg.get_content_maintype() != "multipart":
            continue

            # search if message contains files
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue

            if part.get('Content-Disposition') is None:
                continue
            name = part.get_filename()
            filename = "{}{}".format(name, uuid4())

        if not filename:
            name = "noname"
            filename = '{}{}'.format(name, uuid4())

        att_path = os.path.join(detach_dir, filename)

        # check if name is unique
        while os.path.isfile(att_path):
            if not name:
                name = "noname"
            filename = '{}{}'.format(name, uuid4())
            att_path = os.path.join(detach_dir, filename)

        # save file as a photo instance
        if not os.path.isfile(att_path):
            fp = open(att_path, 'wb')
            payload = (part.get_payload(decode=True))
            print(payload)
            # payload is bytes (isinstance(payload,bytes)) == True
            # payload "b'\xff\xd8\xff\xdb\x00\x84\x00\x14\x0e\x0f\x12"
            fp.write(part.get_payload(decode=True))
            photo = Photo(
                title=email_subjet,
                date=email_date)
            photo.post_img.save(filename, ContentFile(part.get_payload(decode=True)))
            photo.save()
            fp.close()
            mail.store(str(int(num)), '+FLAGS', '\SEEN')
            print("Mail on suletud")


@background(schedule=60)
def readmail_schedule():
    readmail()
