
import datetime
def generate_order(pk1,pk):
      current_datetime=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
      order_number=current_datetime+str(pk1)+str(pk)
      return order_number