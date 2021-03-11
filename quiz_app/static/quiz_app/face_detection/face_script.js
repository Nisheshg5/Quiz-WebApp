//  Script file for the face detection

let video = document.getElementById("video");

// LOAD ALL MODELS ASYNCHRONOUSLY
// tinyFaceDetector - make it fast
Promise.all([
	faceapi.nets.tinyFaceDetector.loadFromUri('/static/quiz_app/face_detection/models')
]).then(startVideo)

 
// start the web camera
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
				Swal.fire({
					icon: 'error',
					title: `Can't access the camera`,
					html: `Error: ${err.message}<br>Please fix the problem and refresh the page.`,
					position: 'center',
					showConfirmButton: false,
					allowOutsideClick: false,
					allowEscapeKey: false,
				});
		})
}


// when the video starts playing create a canvas of same dimenstions as of video at a specific time interval
// the canvas should exactly be above the video
// creates a blue rectangle around the face of the user which means that the camera detected a face

// get the no of people detected by the camera by the detections.length
video.addEventListener('playing', () => {

	console.log("Video Start playing");
	const canvas = faceapi.createCanvasFromMedia(video);
	document.getElementById("video-inner").append(canvas);
	// document.body.append(canvas);
	const displaySize = { width: video.width, height: video.height};
	console.log(displaySize);
	faceapi.matchDimensions(canvas, displaySize);


	// detect the faces at a specific interval
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

