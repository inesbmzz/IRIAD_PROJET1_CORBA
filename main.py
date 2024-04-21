import pydotplus
from sklearn import tree
from sklearn.tree import export_graphviz

def get_prediction_graph(clf, decision_path):
    dot_data = export_graphviz(clf, out_file=None,
                                    feature_names=["T1", "T2", "T3"],
                                    filled=True, rounded=True,
                                    special_characters=True)
    graph = pydotplus.graph_from_dot_data(dot_data)

    for node in graph.get_node_list():
        if node.get_attributes().get('label') is None:
            continue
        if 'samples = ' in node.get_attributes()['label']:
            labels = node.get_attributes()['label'].split('<br/>')
            for i, label in enumerate(labels):
                if label.startswith('samples = '):
                    labels[i] = 'samples = 0'
            node.set('label', '<br/>'.join(labels))
            node.set_fillcolor('white')

            
    for n, node_value in enumerate(decision_path.toarray()[0]):
            node = graph.get_node(str(n))[0]            
            if node_value == 0:
                node.set_label("")
                node.set_width(0)
                node.set_height(0)
                continue
            node.set_fillcolor('#1e4c91')
            labels = node.get_attributes()['label'].split('<br/>')
                
            node.set('label', '<br/>'.join([labels[0], labels[-1]]))
    return graph