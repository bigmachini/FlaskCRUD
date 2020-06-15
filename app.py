import json
import os
from flask_script import Manager
import waitress
from paste.translogger import TransLogger
from flask import Flask, render_template, request, redirect
from flask_wtf.csrf import CSRFProtect
from publisher import QueuePublisherClient
from config import _logger
from datetime import datetime

csrf = CSRFProtect()
app = Flask(__name__)
csrf.init_app(app)

app.config['SECRET_KEY'] = 'a5JnWStv0cqY5KPbx$VMejEBP0REnfpP9PaD^dnECOljHS'


def post_rabbitmq(data, queue_name="mpesa-queue"):
    msg = "post_rabbitmq", "queue: {}  data: {}".format(queue_name, data)
    _logger.info(f'airtime_web API post_rabbitmq: {msg}')
    push = QueuePublisherClient(queue_name, json.dumps(data))  # json.dumps(res).__str__())
    _logger.info(f'airtime_web API post_rabbitmq: {data}')
    push.on_response_connected()


def validate_phone(phone):
    pass


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        _logger.info(f'USSD API POST vals: {request.form}')
        own_phone = request.form['own_phone']
        other_phone = request.form.get('other_phone')
        amount = request.form.get('amount')
        timestamp = datetime.now().timestamp()

        if not own_phone or not amount:
            return "Not sure what are you trying to achieve"

        if not other_phone:
            other_phone = own_phone

        other_phone = f"+254{other_phone[1:]}"

        try:
            data = {'recipient_number': other_phone,
                    'sender_number': f"+254{own_phone[1:]}",
                    'amount': amount,
                    'timestamp': str(timestamp)}

            post_rabbitmq(data)
            res = redirect('/')
            res.set_cookie('own_phone', own_phone)
            return res
        except Exception as ex:
            return f"Contact Admin if issues persists Error: {str(ex)}: info@bigmachini.net"

    else:
        own_phone = request.cookies.get('own_phone', '')
        return render_template('create.html', own_phone=own_phone)


if __name__ == '__main__':
    manager = Manager(app)
    manager.add_command('runserver', waitress.serve(TransLogger(app, setup_console_handler=False),
                                                    url_scheme='http',
                                                    host='0.0.0.0',
                                                    port=int(os.environ.get('PORT', 9006))))

    manager.run()
