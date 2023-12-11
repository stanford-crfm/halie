var currentQuestionIndex = 0;
var pauseDetectingBlur = false;
var stopDetectingBlur = false;
var isLocal = false; // !(serverURL.indexOf('writingwithai') > 0);
const stopShowingAlert = true;


// window.setInterval(function(){
//   console.log(pauseDetectingBlur);
// }, 1000);

window.setInterval(function(){
  pauseDetectingBlur = false;
}, 10000);

window.setInterval(function(){
  if (!document.hasFocus()){
    if (!pauseDetectingBlur && !stopDetectingBlur) {
      logEvent(EventName.WINDOW_BLUR, EventSource.USER);
      warnOnWindowBlur();
    }
  }
}, 5000);


$(window).blur(function() {
  if (!pauseDetectingBlur && !stopDetectingBlur) {
    logEvent(EventName.WINDOW_BLUR, EventSource.USER);
    warnOnWindowBlur();
  }
});

$(window).focus(function() {
  logEvent(EventName.WINDOW_FOCUS, EventSource.USER);
  turnOffWarning();
});

$('.answer').click(function(){
  $('.answer').removeClass('selected');
  $(this).addClass('selected');

  let choice = $(this).data('choice');
  switch (choice) {
    case 'a':
      logEvent(EventName.BUTTON_ANSWER_A, EventSource.USER);
      break;
    case 'b':
      logEvent(EventName.BUTTON_ANSWER_B, EventSource.USER);
      break;
    case 'c':
      logEvent(EventName.BUTTON_ANSWER_C, EventSource.USER);
      break;
    case 'd':
      logEvent(EventName.BUTTON_ANSWER_D, EventSource.USER);
      break;
  };
});

$('#generate-button').click(function(){
  prompt = getText();
  if (prompt.length > 0) {
    logEvent(EventName.BUTTON_GENERATE, EventSource.USER);
    queryGPT3forInteractiveQA(prompt);
  } else {
    pauseDetectingBlur = true;
    alert('Please write something to prompt the system before clicking this button!');
  }
});

$('#next-button').click(function(){
  selectedAnswer = $('.selected');
  if (selectedAnswer.length == 1) {
    logEvent(EventName.BUTTON_NEXT, EventSource.USER);

    currentQuestionIndex += 1;
    setQuestionAnswers(currentQuestionIndex);
  } else {
    pauseDetectingBlur = true;
    alert('Please select one of the answers first before proceeding to the next question!');
  }
  $('.selected').removeClass('selected');

  if (currentQuestionIndex == questionBank.length - 1){
    $('#next-button').addClass('do-not-display');
    $('#finish-button').removeClass('do-not-display');
  }
});

$('#finish-button').click(function(e){
  stopDetectingBlur = true;
  endSessionforInteractiveQA();
});

function warnOnWindowBlur (){
  $('#frontend-right').css('box-shadow', 'rgba(189, 32, 49, 0.9) 0px 10px 20px');

  if (!isLocal || !stopShowingAlert) {
    pauseDetectingBlur = true;
    alert('Please do not switch tabs or open a new window during your participation. This is to make sure you do not use a search engine and also that you complete the task in one setting. We can detect if you have siwtched tabs/opened a new window and reserve the right to reject your HIT.');
  } else {
    console.log('Please do not switch tabs or open a new window during your participation. This is to make sure you do not use a search engine and also that you complete the task in one setting. We can detect if you have siwtched tabs/opened a new window and reserve the right to reject your HIT.');
  }
}

async function turnOffWarning () {
  await delay(1500);
  $('#frontend-right').css('box-shadow', 'rgba(0, 0, 0, 0.2) 0px 10px 20px');
}

function disableAssistance() {
  console.log('Mode: without AI assistance');
  $('#frontend-right-overlay').removeClass('do-not-display');
}

function enableAssistance() {
  console.log('Mode: with AI assistance');
  $('#frontend-right-overlay').addClass('do-not-display');
}

function showLoadingSignalRing() {
  $('#loading-signal').removeClass('do-not-display');
  $('#completion-text').text('');
}

function hideLoadingSignalRing() {
  $('#loading-signal').addClass('do-not-display');
}

function setQuestionAnswers(index) {
  $('#currentQuestionIndex').text(index + 1);
  question = questionBank[index];

  $('#question').text(question['question']);
  $('#answer-a').text(question['answer_a']);
  $('#answer-b').text(question['answer_b']);
  $('#answer-c').text(question['answer_c']);
  $('#answer-d').text(question['answer_d']);

  if (question['assistance']){
    enableAssistance();
  } else {
    disableAssistance();
  }
}

async function endSessionforInteractiveQA() {
  const results = await wwai.api.endSession(sessionId, logs);
  const verificationCode = results['verification_code'];

  $('#frontend-right-overlay').text('Verification code: ' + verificationCode);
  $('#frontend-right-overlay').removeClass('do-not-display');
}
