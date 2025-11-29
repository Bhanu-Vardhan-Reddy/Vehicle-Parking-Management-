from email.message import EmailMessage
import smtplib

def email_alert(subject, body, to, html=''):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['To'] = to
    msg['From'] = "nbhanuvardhanreddy@gmail.com"

    if html:
        msg.set_content(body)
        msg.add_alternative(html, subtype='html')
    else:
        msg.set_content(body)

    user = "nbhanuvardhanreddy@gmail.com"
    password = 'irsi znit bdyl hwcu'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

if __name__ == '__main__':
    email_alert(
        subject='hi',
        body='this is from quizmanager',
        to='23f3002722@ds.study.iitm.ac.in',
        html='<h1>This is from <b>Parking Management System</b></h1>'
    )
