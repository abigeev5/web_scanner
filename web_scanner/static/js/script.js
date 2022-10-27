document.addEventListener("click", function (e) {
    if (e.target.classList.contains("result-item")) {
        var parent = e.target.parentElement;
        
        const str = parent.querySelector('.card-img-top').getAttribute("alt").replaceAll("\'", "\"", );
        const data = JSON.parse(str);

        document.querySelector("#modal-title").innerText = data['image'].split('/')[data['image'].split('/').length - 1]; 
        document.querySelector("#modal-canvas").alt = parent.querySelector('.card-img-top').getAttribute("alt");
        //document.querySelector("#modal-img").src = data['image'];
        //document.querySelector("#modal-img").alt = parent.querySelector('.card-img-top').getAttribute("alt");
        //document.querySelector("#modal-barcode").innerText = data['barcode'];
        document.querySelector("#modal-date-field").innerHTML = data['time'];
        document.querySelector("#modal-scanner-field").innerHTML = data['scanner'];
        document.querySelector("#modal-user-field").innerHTML = data['user'];

        var myCanvas = document.getElementById('modal-canvas');
        var context = myCanvas.getContext('2d');
        var img = new Image;
        img.onload = function(){
            var canvas = context.canvas ;
            var hRatio = canvas.width  / img.width;
            var vRatio =  canvas.height / img.height;
            var ratio  = Math.min ( hRatio, vRatio );
            var centerShift_x = ( canvas.width - img.width*ratio ) / 2;
            var centerShift_y = ( canvas.height - img.height*ratio ) / 2;  
            context.clearRect(0,0,canvas.width, canvas.height);
            context.drawImage(img, 0,0, img.width, img.height,
            centerShift_x,centerShift_y,img.width*ratio, img.height*ratio);  
        };
        img.src = data['image'];


        const myModal = new bootstrap.Modal(document.getElementById('viewer-modal'));
        myModal.show();
    }

    if (e.target.id == "modal-show") {
        const data = JSON.parse(document.querySelector("#modal-canvas").alt.replaceAll("\'", "\"", ));
        var canvas = document.getElementById('modal-canvas');
        var context = canvas.getContext('2d');
        if (e.target.classList.contains("active")) {
            var img = new Image;
            img.onload = function(){
                var canvas = context.canvas ;
                var hRatio = canvas.width  / img.width;
                var vRatio =  canvas.height / img.height;
                var ratio  = Math.min ( hRatio, vRatio );
                var centerShift_x = ( canvas.width - img.width*ratio ) / 2;
                var centerShift_y = ( canvas.height - img.height*ratio ) / 2;  
                context.clearRect(0,0,canvas.width, canvas.height);
                context.drawImage(img, 0,0, img.width, img.height,
                centerShift_x,centerShift_y,img.width*ratio, img.height*ratio);  
            };
            img.src = data['image'];
            e.target.classList.remove('active');
        } else {
            context.beginPath();
            var img = new Image;
            img.src = data['image'];
            for (var i = 0; i < data['bboxes'].length; i++) {
                NewTop    = ((data['bboxes'][i][0]) * canvas.height / img.height);
                NewLeft   = ((data['bboxes'][i][1]) * canvas.width  / img.width);

                NewBottom = ((data['bboxes'][i][0] + data['bboxes'][i][2] + 1) * canvas.height / img.height) - 1;
                NewRight  = ((data['bboxes'][i][1] + data['bboxes'][i][3] + 1) * canvas.width  / img.width) - 1;
                //context.rect(data['bboxes'][i][0], data['bboxes'][i][1], data['bboxes'][i][2], data['bboxes'][i][3]);
                context.rect(NewTop, NewLeft, NewBottom - NewTop, NewRight - NewLeft);
                context.lineWidth = 5;
                context.strokeStyle = 'green';
                context.stroke();
            }
            e.target.classList.add('active');
        }
    }
})