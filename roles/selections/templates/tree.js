
$(function(){
    // Initialize the tree from the <ul> tag inside <div id='tree'>
   $("#tree").fancytree({
       source: $.ajax({ url: "/pits/data",
       //                 data: data,
                        cache: false }),
        checkbox: true,
        activate: function(e, data){
            $("div#statusLine").text("Active node: " + data.node);
        }
    });
    
    // Activate a node, on button click
    $("button#button1").click(function(){
        var tree = $("#tree").fancytree("getTree"),
            node2 = tree.getNodeByKey("id2");
        node2.toggleSelected();
    });
});
