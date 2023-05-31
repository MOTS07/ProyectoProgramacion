$(document).ready(function() {
	setInterval(function() {
		$.get("/verificar/", function(data, status) {
			if (status == "success"){
			lista = "";
		for(var i=0; i< data.length; i++){
			lista += "<tr>"+"<td>"+data[i].Servidor+"</td>"+"<td>"+data[i].DireccionIP+"</td>"+"<td>"+data[i].Estado+"</td>"+"<td>"+data[i].Fecha+"</td>"+"</td>"
			}
				$("#datos").html(lista);
			}
		});
	}, 1000) ;
});
