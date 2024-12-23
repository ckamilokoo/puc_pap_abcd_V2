//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;
let gumStream;

let rec;

let input;

let AudioContext = window.AudioContext || window.webkitAudioContext;
let audioContext;

// Click on mic
let clickMic = document.getElementById("recordVoice");
clickMic.addEventListener("click", processVoice);

let flag = false;
let flagTrigger = false;
function processVoice() {
  flag = !flag;
  const filterColor = flag ? "invert(1)" : "grayscale(100%)";
  document.getElementById("recordVoice").style.filter = filterColor;
  if (flag) {
    startRecording();
  } else {
    flagTrigger = true;
    stopRecording();
  }
}

function startRecording() {
  let constraints = {
    audio: true,
    video: false,
  };

  audioContext = new AudioContext();

  navigator.mediaDevices
    .getUserMedia(constraints)
    .then(function (stream) {
      console.log(
        "getUserMedia() success, stream created, initializing Recorder.js ..."
      );

      gumStream = stream;

      input = audioContext.createMediaStreamSource(stream);

      rec = new Recorder(input, {
        numChannels: 1,
      });

      rec.record();
      console.log("Recording started");
    })
    .catch(function (err) {
      console.log(err);
    });
}

function stopRecording() {
  console.log("stopButton clicked");
  rec.stop(); //stop microphone access
  gumStream.getAudioTracks()[0].stop();
  //create the wav blob and pass it on to createDownloadLink
  rec.exportWAV(invokeSTT);
}

let recordVoice;
function invokeSTT(blob) {
  let file = new File([blob], new Date().toISOString() + ".wav");
  let myHeaders = new Headers();
  myHeaders.append(
    "Authorization",
    "Basic YXBpa2V5Oll1cHNBZU5ENGQwTVRKamFIVVdlRHlGbkFzWmxUNGRkbmhaTXVSRkRBVlVt"
  );
  myHeaders.append("Content-Type", "audio/wav");
  let requestOptions = {
    method: "POST",
    headers: myHeaders,
    body: file,
    redirect: "follow",
  };

  const baseUrl = new URL(
    "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/ef7be3c6-c3f9-4f42-8389-23ed6e468b66/v1/recognize?model=es-LA_Telephony&background_audio_suppression=0.3"
  );

  fetch(baseUrl.href, requestOptions)
    .then((response) => response.text())
    .then((result) => {
      let output = JSON.parse(result);

      recordVoice = output.results[0].alternatives[0].transcript;
      recordVoice = recordVoice.replace("%HESITATION", "");
    })
    .catch((error) => console.log("error", error));
}

async function preReceiveHandler(event) {
  if (event.data.output.generic != null) {
    for (const element of event.data.output.generic) {
      await playAudio(element.text);
    }
  }
}

window.watsonAssistantChatOptions = {
  integrationID: "b30166c3-cbb9-4245-a645-59c50a69c58f", // The ID of this integration.
  region: "us-south", // The region your integration is hosted in.
  serviceInstanceID: "d74071f8-3574-4894-bb15-cf419fc89077", // The ID of your service instance.
  onLoad: function (instance) {
    instance.on({ type: "receive", handler: preReceiveHandler });

    document
      .getElementById("recordVoice")
      .addEventListener("click", function () {
        if (flagTrigger) {
          flagTrigger = false;
          setTimeout(function () {
            const sendObject_input = {
              input: {
                message_type: "text",
                text: recordVoice,
              },
            };
            const sendOptions_input = {
              silent: false,
            };
            instance
              .send(sendObject_input, sendOptions_input)
              .catch(function () {
                console.error("This message did not send!");
                console.log("Speechsent!");
              });
          }, 5000);
        }
      });

    instance.render();
  },
};
setTimeout(function () {
  const t = document.createElement("script");
  t.src =
    "https://web-chat.global.assistant.watson.appdomain.cloud/versions/" +
    (window.watsonAssistantChatOptions.clientVersion || "latest") +
    "/WatsonAssistantChatEntry.js";
  document.head.appendChild(t);
});

async function playAudio(text2speechContent) {
  let myHeaders = new Headers();
  var host = window.location.protocol + "//" + window.location.host;
  myHeaders.append(
    "Authorization",
    "Basic YXBpa2V5OndpODdVX1R4RmMyenU5Z3ZFT2V2WGozOFRVc24tdWM3OFpjSjdoLVZTZklC"
  );
  //myHeaders.append("Access-Control-Allow-Origin", host);

  let requestOptions = {
    method: "GET",
    headers: myHeaders,
    redirect: "follow",
  };

  const baseUrl = new URL(
    "https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/e423d1f9-4bd1-49e2-a163-51f61c13c832/v1/synthesize"
  );
  baseUrl.searchParams.append("accept", "audio/mp3");
  baseUrl.searchParams.append("voice", "es-LA_DanielaExpressive");
  baseUrl.searchParams.append("text", text2speechContent);

  await fetch(baseUrl.href, requestOptions)
    .then((result) => {
      return playon(result);
    })

    .catch((error) => console.log("error", error));
}

function blobToFile(theBlob, fileName) {
  theBlob.lastModifiedDate = new Date();
  theBlob.name = fileName;
  return theBlob;
}

async function playon(result) {
  let file;
  await result.blob().then((data) => {
    file = blobToFile(data, "received.mp3");
  });
  return new Promise(function (resolve, reject) {
    let objectUrl = window.URL.createObjectURL(file);
    document.getElementById("log").innerHTML = "";
    document.getElementById("log").innerHTML +=
      '<audio id="audio" hidden crossOrigin="anonymous" controls src=' +
      objectUrl +
      ">";

    let audio = document.getElementById("audio");
    audio.load();
    audio.play();

    audio.onerror = reject;
    audio.onended = resolve;
  });
}
