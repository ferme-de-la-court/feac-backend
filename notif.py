import smtplib
from email.message import EmailMessage

message = """
une nouvelle commande a été enregistré dans le système.

rentrez à la ferme et veuillez la préparer dans les meilleures
délais.
"""

def notify():
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = 'une commande a été soumise'
    msg['From'] = "brun.nicolas21@gmail.com"
    msg['To'] = "brun.nicolas21@gmail.com"

    print(msg)

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
