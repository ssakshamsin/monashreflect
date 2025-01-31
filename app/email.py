from flask_mail import Message
from flask import render_template
from app import mail
from threading import Thread
from flask import current_app

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_verification_email(user):
    token = user.get_verification_token()
    send_email('Verify Your Email',
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/verify_email.txt',
                                       user=user, token=token),
               html_body=render_template('email/verify_email.html',
                                       user=user, token=token))