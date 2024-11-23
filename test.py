from datetime import time,datetime,date 

today=datetime.now()
current_time=today.strftime('%H:%M:%S%p')
print(type(current_time))