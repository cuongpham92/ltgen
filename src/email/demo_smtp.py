import smtplib
import os.path
from random import randint
from email.mime.text import MIMEText




# The actual mail send
for i in range(1,2):
    num1 = randint(1, 200)
    num2 = randint(1, 200)

    fromaddr = 'user{0}@tsp.com'.format(num1)
    password = 'user{0}'.format(num1)

    toaddrs  = 'user{0}@tsp.com'.format(num2)


    subject = MIMEText("Obsédé par cette crainte, qui grossit en cet endroit, moins fréquenté que les autres étaient acquittés.".encode('utf-8'), 'plain', 'utf-8')
    content = MIMEText("Fixant sur lui ses yeux étincelants voulaient percer la ténébreuse transparence de la grâce et le récompenser largement de toutes ses prétentions sur l'anneau.".encode('utf-8'), 'plain', 'utf-8')

    msg = """From: {0}
To: {1}
Subject: {2}

{3}
    """.format(fromaddr, toaddrs, subject, content)

    msg = "Aussitot couche, je tenais la lanterne immobile, aches, vous etes libre comme l'air, et on entendait seulement un sourd tumulte de voix, de fourchettes et de ses biens."

    server = smtplib.SMTP('10.0.1.14:587')
    server.starttls()
    server.login(fromaddr, password)

    server.sendmail(fromaddr, toaddrs, msg)

    server.quit()
