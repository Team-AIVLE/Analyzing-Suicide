$.ajax({
    type: 'GET',
    url: "/api/related_info",
    data: {},
    dataType: 'json',
    success: function (data){
        var edges;
        var nodes;
        var allNodes;
        var allEdges;
        var nodeColors;
        var originalNodes;
        var network;
        var container;
        var options, network_data;
        var filter = {
            item : '',
            property : '',
            value : []
        };
        var container = document.getElementById('info_related_network');

        nodes = new vis.DataSet(data['nodes']);
        edges = new vis.DataSet(data['edges']);

        console.log(nodes)

        nodeColors = {};
        allNodes = nodes.get({ returnType: "Object" });
        for (nodeId in allNodes) {
            nodeColors[nodeId] = allNodes[nodeId].color;
        }
        allEdges = edges.get({ returnType: "Object" });
        // adding nodes and edges to the graph
        network_data = {nodes: nodes, edges: edges};

        var options = {
            "configure": {
                "enabled": false
            },
            "edges": {
                "color": {
                    "inherit": true
                },
                "smooth": {
                    "enabled": true,
                    "type": "dynamic"
                }
            },
            "interaction": {
                "dragNodes": true,
                "hideEdgesOnDrag": false,
                "hideNodesOnDrag": false
            },
            "physics": {
                "enabled": true,
                "stabilization": {
                    "enabled": true,
                    "fit": true,
                    "iterations": 1000,
                    "onlyDynamicEdges": false,
                    "updateInterval": 50
                }
            }
        };

        network = new vis.Network(container, network_data, options);
        return network;
    }
});