const video = document.getElementById("video");

// LOAD ALL MODELS ASYNCHRONOUSLY

// timyFaceDetector - make it fast
// faceLandmark - detect the nose mouth eye etc
// faceRecognitionNet - all the api to locate the face, surround with the box
// faceExpression - recoginse teh expression

Promise.all([
	faceapi.nets.tinyFaceDetector.loadFromUri('/models')
]).then(startVideo)

 
function startVideo(){
	navigator.mediaDevices.getUserMedia({ video: {}})
		.then((stream) => {
				// console the result
				console.log("Camera Found");

				// use the stream
				video.srcObject = stream;
				// video.onloadedmetadata = (e) => {
					// console.log(e);
					// video.play();
				// }
		})
		.catch((err) => {
			// handle the error
				console.error(err.name + ": " + err.message);
		})
}

video.addEventListener('playing', () => {

	console.log("Video Start playing");
	const canvas = faceapi.createCanvasFromMedia(video);
	document.body.append(canvas);
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
		}
		console.log(detections.length)
	}, 1000);

})