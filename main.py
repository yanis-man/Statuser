from flask import Flask, redirect, render_template, url_for, request
import threading
from time import sleep
from turbo_flask import Turbo
import os

from utils import get_list_status, add_ip, remove_ip

app = Flask(__name__, template_folder="templates")
app.config["UPLOAD_FOLDER"] = os.path.join('static', 'status_image')
turbo = Turbo(app)
PING_INTERVAL = 5

@app.route("/", methods=["POST", "GET", "DELETE"])
def home():
    # conventionnally using POST as an INSERT method
    if request.method == 'POST':
        new_address =  request.form.get('address')
        new_display_name = request.form.get('display_name')
        if add_ip(new_address, new_display_name):
            return redirect("/")
    # deletion for an entry
    if request.method == "DELETE":
        if remove_ip(request.form.get('address'), request.form.get('display_name')):
            return redirect("/")
    return render_template("index.html")

# starts the display update loop
@app.before_first_request
def before_first_request():
    threading.Thread(target=update_display).start()

def update_display():
    with app.app_context():
        while True:
            status_list_raw = get_list_status()
            turbo.push(turbo.replace(render_template("status.html", status_list = status_list_raw), 'status_container'))
            sleep(PING_INTERVAL)

if __name__ == "__main__":
    app.run(debug=True)