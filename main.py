from gevent import monkey
monkey.patch_all()
import re
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def get_class_id(url):
    id = url.split('/')[-1].split("?")[0]
    return id

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Extract class ID from submitted URL using regex
        url = request.form['url']
        class_id = get_class_id(url)
        try:
            # Call Skillshare API to retrieve course information
            response = requests.get(f"https://skillshare.knavi.repl.co/api/classes/{class_id}")
            response.raise_for_status()
            course_data = response.json()
            title = course_data['course_info']['course_title']
            # Pass course data to the template for rendering
            return render_template('player.html', course_data=course_data, title=title)
        except requests.exceptions.HTTPError as err:
            # Handle HTTP errors
            return render_template('index.html', error=f"Error: {err}")
        except Exception as err:
            # Handle other exceptions
            return render_template('index.html', error="Error: An unexpected error occurred.")
    else:
        # Render search form on initial GET request
        return render_template('index.html')

if __name__ == '__main__':
    # Run the app using Gunicorn on port 81
    bind_address = "0.0.0.0:81"
    worker_class = "gevent"
    timeout = 120

    from gunicorn.app.base import Application
    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            return {
                'bind': bind_address,
                'worker_class': worker_class,
                'timeout': timeout
            }
        def load(self):
            return app
    FlaskApplication().run()
