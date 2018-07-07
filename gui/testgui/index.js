ajaxRequest=function(url,callback){
    var oReq = new XMLHttpRequest();
    oReq.addEventListener("load", function(){
        callback(this.responseText);
    });
    oReq.open("GET", url);
    oReq.send();
};

updateStatus=function(){
    var oReq = new XMLHttpRequest();
    ajaxRequest("/control?request=status", function(data){
        var ct=document.getElementById('statusContent');
        ct.innerText=data;
    });
};
window.onload=function(){
   setInterval(updateStatus,3000);
   document.getElementById('startTimerButton').addEventListener('click',function(ev){
       console.log("startTimer");
       var url="/control?request=start&channel=";
       url+=encodeURIComponent(this.form.children.namedItem('channel').value);
       url+="&duration="+encodeURIComponent(this.form.children.namedItem('duration').value);
       ev.preventDefault();
       ajaxRequest(url,function(data){
           var rt=JSON.parse(data);
           if (rt.status !== "OK"){
               alert("unable to start: "+rt.info)
           }
       })
   });
   document.getElementById('stopTimerButton').addEventListener('click',function(ev){
        console.log("stopTimer");
        ev.preventDefault();
        var url="/control?request=stop";
        ajaxRequest(url,function(data){
           var rt=JSON.parse(data);
           if (rt.status !== "OK"){
               alert("unable to stop: "+rt.info)
           }
        })

    });
   updateStatus();
};

