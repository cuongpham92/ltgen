import imaplib
import socket
import ssl
import sys
import email

user = sys.argv[1]
passwd = sys.argv[2]

ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
mail =  imaplib.IMAP4_SSL('10.0.1.14', 993, ssl_context=ctx)
mail.login(user, passwd)

mail.list()
# Connect to inbox
mail.select("inbox")
# Out: list of "folders" aka labels in gmail
result, data = mail.search(None, "ALL")

ids = data[0] # data is a list
id_list = ids.split() # ids is a space separated string

for i in range(1, 3):
    latest_email_id = id_list[-i]
    # Fetch the email body (RFC822) for the given ID
    result, data = mail.fetch(latest_email_id, "(RFC822)")
    # Here's the body, which is raw text of the whole email,
    # including headers and alternate payloads
    raw_email = data[0][1].decode('utf-8')
    email_message = email.message_from_string(raw_email)
    #print(email_message)
    receiver = email_message['From']
    print(receiver)

mail.logout() 
del mail
