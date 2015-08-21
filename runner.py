import sys
from os import walk
from os.path import splitext, join
import parser
import token
import json

def select_files(root, files):
    selected_files = []

    for file in files:
        #do concatenation here to get full path 
        full_path = join(root, file)
        ext = splitext(file)[1]
        
        if ext == ".py":
            print(full_path)
            selected_files.append(full_path)

    return selected_files

def build_recursive_dir_tree(path):
    selected_files = []

    for root, dirs, files in walk(path):
        selected_files += select_files(root, files)

    return selected_files

def search(st, result_array):
    if not isinstance(st, list):
        return
    
    if st[0] in [token.NAME]:
        result_array.append([st[1], st[2]])
    else:
        for s in st[1:]:
            search(s, result_array)

rootdir = sys.argv[1]

files = build_recursive_dir_tree(rootdir)
results_arrays = []

for file in files:
    result_array = [file, []]
    results_arrays.append(result_array)

    fd = open(file, "r")
    
    st = parser.suite(fd.read())


    st_list = parser.st2list(st, line_info=True)
    
    search(st_list, result_array[1])

    fd.close()



nodes_by_name = {}
nodes_by_id = []
num_nodes = 0 

for results_for_file in results_arrays:
    file_name = results_for_file[0]
     
    for results_for_name in results_for_file[1]:
        if results_for_name[0] not in nodes_by_name:
            nodes_by_name[results_for_name[0]] = []


        nodes_by_id.append({"id": num_nodes + 1, "label": file_name + ": " + results_for_name[0] + " -> " + str(results_for_name[1])})
        nodes_by_name[results_for_name[0]].append(nodes_by_id[num_nodes])

        num_nodes += 1

print(json.dumps(nodes_by_name))
              
edges = []

for node_name in nodes_by_name:
    nodes = nodes_by_name[node_name]
 
    index = 0
    for node in nodes:
        if index == 0:
            nodes_by_id.append({"id": num_nodes + 1, "label": node_name})
            num_nodes += 1
   
        edges.append({"from": num_nodes, "to": node["id"]})
        index += 1
    
print(json.dumps(edges))


html = """<!doctype html>
<html>
<head>
  <title>Network | Basic usage</title>

  <script type="text/javascript" src="vis.js"></script>
  <link href="vis.css" rel="stylesheet" type="text/css" />

  <style type="text/css">
    #mynetwork {
      width: 600px;
      height: 400px;
      border: 1px solid lightgray;
    }
  </style>
</head>
<body>

<p>
  Create a simple network with some nodes and edges.
</p>

<div id="mynetwork"></div>

<script type="text/javascript">
  // create an array with nodes
  var nodes = new vis.DataSet(""" + json.dumps(nodes_by_id) + """);

  // create an array with edges
  var edges = new vis.DataSet(""" + json.dumps(edges) + """);

  // create a network
  var container = document.getElementById('mynetwork');
  var data = {
    nodes: nodes,
    edges: edges
  };
  var options = {};
  var network = new vis.Network(container, data, options);
</script>

</body>
</html>
"""

html_out = open("test.html", "w")

html_out.write(html)

html_out.close()
