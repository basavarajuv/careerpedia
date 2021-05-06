# from django.test import TestCase

# Create your tests here.


import smtplib
import pdb;pdb.set_trace()
s = smtplib.SMTP('smtplib.gmail.com',465)
s.ehlo()
s.starttls()
s.login('sreeni.python@gmail.com','Psa@gm#$!21')
try:
    s.sendmail('sreeni.python@gmail.com','sreeni.python@gmail.com','HiPythontest')
except:
    print (failed)

