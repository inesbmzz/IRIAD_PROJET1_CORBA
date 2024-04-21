#!/usr/bin/env python

import sys
from omniORB import CORBA, PortableServer

# Import the stubs and skeletons for the Example module
import CosNaming, M, M__POA

import numpy as np
import pandas as pd
from sklearn import tree
from main import get_prediction_graph
from datetime import datetime

# Define an implementation of the M interface
class Bac_i (M__POA.Bac):
    clf = None
    anything = 2
    init = 0
    x = None
    y = None

    def startPredict(self):
        if (self.anything == 0):
            return True
        else:
            return False
               
    def getData(self, path):
        dataset = pd.read_csv(path, names=["T1", "T2", "T3", "result"])
        dataset = dataset.dropna()
        x = np.array(dataset.iloc[1:,:-1])
        y = np.array(dataset.iloc[1:,-1])
        if self.init == 0:
            self.x = x
            self.y = y
            self.init = 1
        else: 
            self.x = np.concatenate((self.x, x))
            self.y = np.concatenate((self.y, y))
       
        if (self.anything <= 1):
            # global clf
            df = pd.DataFrame(np.concatenate((self.x, np.array(np.expand_dims(self.y, axis=1))), axis=1), columns=["T1", "T2", "T3", "result"])
            df.to_csv("datasets/dataset.csv", index=False)
            
            self.clf = tree.DecisionTreeRegressor()
            self.clf = self.clf.fit(self.x, self.y)
            self.anything = 0
        else: 
            self.anything = self.anything -1

    def predict(self, note1, note2, note3):
        result = self.clf.predict([[note1,  note2, note3]])
        decision_path = self.clf.decision_path([[note1,  note2, note3]])
        print(result)
        graph = get_prediction_graph(self.clf, decision_path)
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = "./static/tree_"+unique_id+".png"
        graph.write_png(filename)

        prediction = result[0]
        return prediction

# Initialise the ORB
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)

# Find the root POA
poa = orb.resolve_initial_references("RootPOA")

# Create an instance of Bac_i
ei = Bac_i()

# Create an object reference, and implicitly activate the object
eo = ei._this()

# Obtain a reference to the root naming context
obj         = orb.resolve_initial_references("NameService")
rootContext = obj._narrow(CosNaming.NamingContext)

if rootContext is None:
    print ("Failed to narrow the root naming context")
    sys.exit(1)

# Bind a context named "test.my_context" to the root context
name = [CosNaming.NameComponent("project", "my_context")]

try:
    projectContext = rootContext.bind_new_context(name)
    print ("New project context bound")
    
except CosNaming.NamingContext.AlreadyBound, ex:
    print ("Project context already exists")
    obj = rootContext.resolve(name)
    projectContext = obj._narrow(CosNaming.NamingContext)
    if projectContext is None:
        print ("projet.mycontext exists but is not a NamingContext")
        sys.exit(1)

# Bind the Echo object to the test context
name = [CosNaming.NameComponent("Exampleproject", "Object")]

try:
    projectContext.bind(name, eo)
    print ("New Exampleproject object bound")

except CosNaming.NamingContext.AlreadyBound:
    projectContext.rebind(name, eo)
    print ("Exampleproject binding already existed -- rebound")

# Activate the POA
poaManager = poa._get_the_POAManager()
poaManager.activate()


# Everything is running now, but if this thread drops out of the end
# of the file, the process will exit. orb.run() just blocks until the
# ORB is shut down
orb.run()



