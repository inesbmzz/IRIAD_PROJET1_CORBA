#!/usr/bin/env python

import sys


from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from sklearn import tree
from sklearn.tree import export_graphviz
from datetime import datetime


# Import the CORBA module
from omniORB import CORBA
# Import the stubs for the CosNaming and Example modules
import CosNaming, M

# Initialise the ORB
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
# Obtain a reference to the root naming context
obj         = orb.resolve_initial_references("NameService")
rootContext = obj._narrow(CosNaming.NamingContext)
# Resolve the name "project.my_context/ExampleEcho.Object"
name = [CosNaming.NameComponent("project", "my_context"),
        CosNaming.NameComponent("Exampleproject", "Object")]
obj = rootContext.resolve(name)
# Narrow the object
eo = obj._narrow(M.Bac)

if eo is None:
    print "Object reference is not an Example::Echo"
    sys.exit(1)


app = Flask(__name__)

clf = None

@app.route('/')
def home(): 
    startPredict = eo.startPredict()
    return render_template('home.html', start_predict=startPredict)


@app.route('/data')
def index():
    return render_template('index.html')


@app.route('/merci', methods=['POST'])
def thankYou():
    # file = request.form["dataset"]
    file = request.files["dataset"]
    print(file)
    dataset = pd.read_csv(file, names=["T1", "T2", "T3", "result"])
    unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
    dataset.to_csv("datasets/data_"+unique_id+".csv")
    eo.getData("datasets/data_"+unique_id+".csv")
    return render_template('transition.html')


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        t1 = request.form["T1"]
        t2 = request.form["T2"]
        t3 = request.form["T3"]
        print(t1,t2,t3)
        result = eo.predict(float(t1), float(t2), float(t3))
        return render_template('predict.html', prediction=result, prediction_path=True)
    elif request.method == 'GET':
        startPredict = eo.startPredict()
        if (startPredict):
            return render_template('predict.html') 
        else:
            return render_template('error.html')
    

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=0)

