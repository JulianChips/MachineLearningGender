// runs a short java script file to process the image
document.getElementById("image").addEventListener("change", handleChange)

function handleChange(){
    var fileReader = new FileReader();
    fileReader.onload = function(event){
        var str = event.target.result;
        console.log(str)
    }
    var image = document.getElementById('output');
    image.src = URL.createObjectURL(event.target.files[0]);
}

