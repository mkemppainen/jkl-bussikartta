from __future__ import print_function
from flask import Flask
from flask import render_template
from flask import request
import requests
import json
import sys

app = Flask(__name__)

@app.route('/')
def hello():
   return render_template('index.html')

@app.route('/get_route', methods=['GET', 'POST'])
def get_route():
    print('success', file=sys.stderr)
   
    if request.method == 'POST':
        """
        f = request.files['route_data']
        
        f.save('https://api.mapbox.com/v4/directions/mapbox.driving/25.70022,62.25287;25.70514,62.24816;25.736,62.244.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false')
        """
        
        r = requests.get('https://api.mapbox.com/v4/directions/mapbox.driving/25.70022,62.25287;25.70514,62.24816;25.736,62.244.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false')
        print('success2', file=sys.stderr)
        print(r.content, file=sys.stderr)
        
    return render_template('index.html')  
if __name__ == '__main__':
   app.run(debug=True)
