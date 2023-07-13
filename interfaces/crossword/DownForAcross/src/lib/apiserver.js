// Digital Ocean instance: 143.198.226.165
// Important: Change url here when moving machines eventually!

export const apiLogMessage = (message) => {
  console.log(`*** Debug: apiLogMessage: ${message}`);
  return fetch(`http://143.198.226.165:5000/log?message=${encodeURIComponent(message)}`)
    .then((response) => response.text())
    .then((body) => {
      console.debug(body);
    })
    .catch((error) => {
      console.error(error);
    });
};

export const apiAskAI = (query, uid, pid, onChat) => {
  return fetch(
    `http://143.198.226.165:5000/ask?uid=${uid}&pid=${pid}&query=${query}&timestamp=${Date.now()}&url=${
      encodeURIComponent(window.location.href)
    }`
  )
    .then((response) => response.text())
    .then((body) => {
      console.log(`*** Debug: ${body}`);
      onChat('AI', uid + '.AI', body);
    })
    .catch((error) => {
      console.log(error);
      console.error(error);
    });
};
