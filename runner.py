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

    fd = open(file, "r", errors="ignore")
    
    st = parser.suite(fd.read())


    st_list = parser.st2list(st, line_info=True)
    
    search(st_list, result_array[1])

    fd.close()


graphs = {}
nodes_by_name = {}
nodes_by_file = {}
nodes_by_id = []
num_nodes = 0 

for results_for_file in results_arrays:
    file_name = results_for_file[0]
    edges = []
    
   

    for results_for_name in results_for_file[1]:
        if results_for_name[0] not in nodes_by_name:
            new_node = {"data": {"id": results_for_name[0]}}
            nodes_by_name[results_for_name[0]] = [new_node]
        
        file_node_line = {"data": {"id": file_name + ": " + str(results_for_name[1])}}

        if file_name not in nodes_by_file:
            nodes_by_file[file_name] = [{"data": {"id": file_name }}]
            nodes_by_file[file_name].append(new_node)
        else:
            nodes_by_file[file_name].append(new_node)
 
                    
        nodes_by_name[results_for_name[0]].append(file_node_line)

            

        num_nodes += 1


for file_name in nodes_by_file:
    nodes_to_work_on = nodes_by_file[file_name]

    edges = []
    nodes = []
    index = 0

    for node in nodes_to_work_on:
        if index == 0:
            source_node = node
        else:
            node_to_link_to = node
            
            edges.append({"data": {"id": str(source_node["data"]["id"]) + '-' + str(node_to_link_to["data"]["id"]),"source": str(source_node["data"]["id"]), "target": str(node_to_link_to["data"]["id"])}})


        num_nodes += 1
        index += 1
        nodes.append(node)
    graphs[file_name] = nodes + edges

for node_name in nodes_by_name:
    nodes_to_work_on = nodes_by_name[node_name]
 
    num_linked_nodes = 0
    nodes = []
    edges = []
    index = 0
    for node in nodes_to_work_on:
        if index == 0:
            source_node = node    
        else:
            node_to_link_to = node
            edges.append({"data": {"id": str(source_node["data"]["id"]) + '-' + str(node_to_link_to["data"]["id"]),"source": str(source_node["data"]["id"]), "target": str(node_to_link_to["data"]["id"])}})
            num_nodes += 1
            
        nodes.append(node)   
        index += 1
    graphs[node_name] = nodes + edges
    


html = """<!doctype html>
<html>
<head>
  <style>
    #cy {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0px;
        left: 0px;
        display: block;
    }
</style>

<script src="http://code.jquery.com/jquery-2.0.3.min.js"></script>
		<script src="cytoscape.js"></script>

<script src="data.js"></script>

<script src="draw.js"></script>
</head>
  <title>Network | Basic usage</title>


<body width="100% height="100%">

<p>
  Create a simple network with some nodes and edges.
</p>

<div id="cy" width="100%" height="100%"></div>



</body>
</html>
"""

nodes_edges_out = open("data.js", "w")
nodes_edges_out.write("var graphs = " + json.dumps(graphs) + ";")
#nodes_edges_out.write("var nodes = " + json.dumps(nodes_by_id) + ";")
#nodes_edges_out.write("var edges = " + json.dumps(edges) + ";")
nodes_edges_out.close()


html_out = open("test.html", "w")

html_out.write(html)

html_out.close()
