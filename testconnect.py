import smtplib
s = smtplib.SMTP('smtp.gmail.com', 587)
s.ehlo()
s.starttls()
s.login('zayats.roman322@gmail.com', 'zsezrlsblmadeqhx')
print('OK')