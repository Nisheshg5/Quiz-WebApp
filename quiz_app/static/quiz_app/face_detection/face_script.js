let video = document.getElementById("video");
// LOAD ALL MODELS ASYNCHRONOUSLY
// timyFaceDetector - make it fast


Promise.all([
	faceapi.nets.tinyFaceDetector.loadFromUri('/static/quiz_app/face_detection/models')
]).then(startVideo)

 
function startVideo(){
	navigator.mediaDevices.getUserMedia({ video: {}})
		.then((stream) => {
				// console the result
				video = document.getElementById("video");
				console.log("Camera Found");

				// use the stream
				video.srcObject = stream;				
		})
		.catch((err) => {
			// handle the error
				console.error(err.name + ": " + err.message);
		})
}

// startVideo();


video.addEventListener('playing', () => {

	console.log("Video Start playing");
	const canvas = faceapi.createCanvasFromMedia(video);
	document.getElementById("video-inner").append(canvas);
	// document.body.append(canvas);
	const displaySize = { width: video.width, height: video.height};
	console.log(displaySize);
	faceapi.matchDimensions(canvas, displaySize);

	setInterval(async () => {
		const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
		const resizedDetections = faceapi.resizeResults(detections, displaySize);
		canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
		faceapi.draw.drawDetections(canvas, resizedDetections);
		console.log(detections);
		if(detections.length > 1){
			console.error("Multiple people detected");
		}else if(detections.length == 1){
			console.log("User Found");
		}else{
			console.error("No User Found");
		}
	}, 1000);

})

