$(document).ready(function() {
	setInterval(function() {
		$.get("/monitorizacion/", function(data, status) {
			if (status == "success"){
			lista = "";
		for(var i=0; i< data.length; i++){
            lista += "<tr>"+"<td>"+data[i].Admin+"</td>"+"<td>"+data[i].DireccionIP+"</td>"+"<td><a href='/server/'>" + "Conectar a Shell" + "<a/></td>"
			}
				$("#datos").html(lista);
			}
		});
	}, 2000) ;
});
