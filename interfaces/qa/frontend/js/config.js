/***************************************************************/
/****** Development ********************************************/
/***************************************************************/
// const debug = true;
const debug = false;

const serverURL = 'http://writingwithai.stanford.edu:5555';  // NOTE Change to 5000 for Hannah

var contactEmail = ''
/***************************************************************/
/****** Domain: story & replay *********************************/
/***************************************************************/
const baseModel = 'openai/davinci';

/***************************************************************/
/****** Domain: copywriting ************************************/
/***************************************************************/
var sortSuggestions = false;  // NOTE Set to be false in copywriting.js
var isCounterEnabled = false;  // NOTE Set to be true in copywriting.js
var page = '';

/***************************************************************/
/****** Domain: interactive QA *********************************/
/***************************************************************/
var questionBank = null;

/***************************************************************/
/****** Domain: text summarization *****************************/
/***************************************************************/
var exampleBank = null;

/***************************************************************/
/****** Session ************************************************/
/***************************************************************/
var session = null;  // Changed when refreshed
var sessionId = '';  // Changed when refreshed
var example = '';
var exampleActualText = '';
var stop = new Array();
var engine = '';
var model = '';
var crfm = '';
var crfmBase = '';
var promptLength = 0;
var promptText = 0;

/***************************************************************/
/****** Editor *************************************************/
/***************************************************************/
var quill;
var Delta = Quill.import('delta');

let items = null;
let numItems = 0;

let currentIndex = 0;
let currentHoverIndex = '';
let prevCursorIndex = 0;

var originalSuggestions = [];

/***************************************************************/
/****** Reply **************************************************/
/***************************************************************/
let speedUpReplayTime = 5;
let slowDownSuggestionTime = 2000;
let maximumElapsedTime = 1000;

SUCCESS = 1
FAILURE = 0

/***************************************************************/
/****** Logging ************************************************/
/***************************************************************/
const EventName = {
  SYSTEM_INITIALIZE: 'system-initialize',
  TEXT_INSERT: 'text-insert',
  TEXT_DELETE: 'text-delete',
  CURSOR_BACKWARD: 'cursor-backward',
  CURSOR_FORWARD: 'cursor-forward',
  CURSOR_SELECT: 'cursor-select',
  SUGGESTION_GET: 'suggestion-get',
  SUGGESTION_OPEN: 'suggestion-open',
  SUGGESTION_REOPEN: 'suggestion-reopen',
  SUGGESTION_UP: 'suggestion-up',
  SUGGESTION_DOWN: 'suggestion-down',
  SUGGESTION_HOVER: 'suggestion-hover',
  SUGGESTION_SELECT: 'suggestion-select',
  SUGGESTION_CLOSE: 'suggestion-close',
  SKIP: 'skip',

  // Interactive QA
  BUTTON_GENERATE: 'button-generate', // Replayed as SUGGESTION_GET
  SUGGESTION_SHOWN: 'suggestion-shown',  // TODO

  BUTTON_ANSWER_A: 'button-answer-a', // Not replayed
  BUTTON_ANSWER_B: 'button-answer-b', // Not replayed
  BUTTON_ANSWER_C: 'button-answer-c', // Not replayed
  BUTTON_ANSWER_D: 'button-answer-d', // Not replayed
  BUTTON_NEXT: 'button-next', // Not replayed

  WINDOW_BLUR: 'window-blur', // Not replayed
  WINDOW_FOCUS: 'window-focus', // Not replayed

  // Copywriting
  BUTTON_SUMMARY: 'button-summary',
  BUTTON_DETAIL: 'button-detail',
  BUTTON_EXAMPLE: 'button-example',
  BUTTON_ADS: 'button-ads',
  BUTTON_SAVE: 'button-save',

  SUGGESTION_GET_AUTOCOMPLETE: 'suggestion-get-autocomplete',
  SUGGESTION_GET_EXAMPLE: 'suggestion-get-example',

  EXAMPLE_CLICK: 'example-click',
  EXAMPLE_DBLCLICK: 'example-dblclick',
  EXAMPLE_MOUSE_ENTER: 'example-mouse-enter',
  EXAMPLE_MOUSE_LEAVE: 'example-mouse-leave',
  EXAMPLE_DELETE: 'example-delete',

  IDLE_ALERT: 'idle-alert',
  IDLE_ALERT_CONFIRM: 'idle-alert-confirm',

  AD_ADD: 'ad-add',
  AD_DELETE: 'ad-delete',

  // Template
  TEMPLATE_ADD: 'template-add',
  TEMPLATE_DELETE: 'template-delete',

  // Summarization
  SUMMARY_ORIGINAL_RATING: 'summary-original-rating',
  SUMMARY_EDITING: 'summary-editing',
  SUMMARY_EDITED_RATING: 'summary-edited-rating',
  SUMMARY_CONSISTENT: 'summary-consistent',
  SUMMARY_COHERENT: 'summary-coherent',
  SUMMARY_RELEVANT: 'summary-relevant',
  SUMMARY_ADD: 'summary-add',

  // Filtering
  SUGGESTION_FAIL: 'suggestion-fail',
}

const EventSource = {
  USER: 'user',
  API: 'api',
}

const ReplayableEvents = [
  EventName.SYSTEM_INITIALIZE,
  EventName.TEXT_INSERT, EventName.TEXT_DELETE,
  EventName.CURSOR_FORWARD, EventName.CURSOR_BACKWARD, EventName.CURSOR_SELECT,
  EventName.SUGGESTION_GET, EventName.SUGGESTION_OPEN, EventName.SUGGESTION_REOPEN,
  EventName.SUGGESTION_UP, EventName.SUGGESTION_DOWN, EventName.SUGGESTION_HOVER,
  EventName.SUGGESTION_SELECT, EventName.SUGGESTION_CLOSE,
];

Object.freeze(EventName);
Object.freeze(EventSource);

function sourceToEventSource(source) {
  if (source == 'user') {
    return EventSource.USER;
  }
  else if (source == 'api') {
    return EventSource.API;
  }
  else {
    alert('Unknown source: ' + source);
  }
}

/***************************************************************/
/****** Domain *************************************************/
/***************************************************************/
console.log('Domain: ' + domain);

/***************************************************************/
/****** Condition (interface) **********************************/
/***************************************************************/

let urlString = window.location.href;
let url = new URL(urlString);
let condition = url.searchParams.get("cond");

if (condition == 'human') {
  console.log('Condition (URL): human-only');
  $('#shortcuts').addClass('hidden');

  if (domain == 'copywriting'){
    $('#generate-btn').addClass('do-not-display');
    $('#header-text').text('Text Editor');
  }

} else if (condition == 'machine') {
  console.log('Condition (URL): machine-only');

} else {
  if (domain == 'interactiveqa' || domain == 'template') {
    condition = 'human';
    console.log('Condition (forced): human-only');
  } else if (domain.indexOf('copywriting') >= 0) {
    if (domain == 'copywriting-long') {
      condition = 'human';
      console.log('Condition (forced): human-only');
    } else {
      console.log('Condition (URL): human-and-machine');
    }
  } else {
    console.log('Condition (URL): human-and-machine');
  }
}
