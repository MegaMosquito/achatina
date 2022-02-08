function refresh(d_image, d_date, d_classes, d_camtime, d_inftime) {
 var t = 500;
 (async function startRefresh() {
   var address;
   d_image.src = d_image.src.split("?")[0]+"?time="+new Date().getTime();
   const response = await fetch("/json");
   const j = await response.json();
   var when = new Date(j.detect.date * 1000);
   var c = j.detect.entities.length;
   var ct = j["detect"]["cam-time"];
   var it = j["detect"]["inf-time"];
   d_date.innerHTML = when;
   d_classes.innerHTML = c;
   d_camtime.innerHTML = ct;
   d_inftime.innerHTML = it;
   setTimeout(startRefresh, t);
 })();
}
window.onload = function() {
 var d_image = document.getElementById("detect");
 var d_date = document.getElementById("when");
 var d_classes = document.getElementById("classes");
 var d_camtime = document.getElementById("camtime");
 var d_inftime = document.getElementById("inftime");
 refresh(d_image, d_date, d_classes, d_camtime, d_inftime);
}