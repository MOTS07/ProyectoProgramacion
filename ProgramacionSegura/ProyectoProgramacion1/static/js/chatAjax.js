$(document).ready(function() {
	setInterval(function() {
		$.get("/monitorizacion/", function(data, status) {
			if (status == "success"){
			lista = "";
		for(var i=0; i< data.length; i++){
            lista += "<tr>"+"<td>"+data[i].Admin+"</td>"+"<td>"+data[i].IP+"</td>"+"<td>"+data[i].Hostname+"</td>"+"<td>"+data[i].Ram+"</td>"+"<td>"+data[i].Cpu+"</td>"+"<td>"+data[i].Disco+"</td>"+"<td><a href='http://" + data[i].IP+ ":6767'>" + "Conectarse a shell" + "<a/></td>"
			}
				$("#datos").html(lista);
			}
		});
	}, 2000) ;
});
