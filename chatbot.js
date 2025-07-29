const CV_TEXT = `PASTE LENNON CV TEXT HERE`;
// OpenAI API key will be injected at build time by the workflow
const OPENAI_API_KEY = '__OPENAI_API_KEY__';

const chatMessages = [
  { role: 'system', content: `You are an enthusiastic assistant for Lennon's portfolio website. Use only the following CV information to answer questions. If you cannot answer based on the CV, say you don't know. CV: ${CV_TEXT}` },
  { role: 'assistant', content: 'Hi there! I\'m excited to tell you about Lennon. Ask me anything about his experience or skills!' }
];

function addMessage(sender, text) {
  const container = document.getElementById('chatMessages');
  const msg = document.createElement('div');
  msg.className = sender;
  msg.textContent = text;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
}

function sendToOpenAI(userText) {
  chatMessages.push({role:'user', content:userText});
  addMessage('user', userText);
  fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + OPENAI_API_KEY
    },
    body: JSON.stringify({model:'gpt-3.5-turbo', messages: chatMessages})
  })
  .then(r => r.json())
  .then(data => {
    const reply = data.choices?.[0]?.message?.content?.trim() || '';
    chatMessages.push({role:'assistant', content: reply});
    addMessage('assistant', reply);
  })
  .catch(err => {
    addMessage('assistant', 'Error: ' + err.message);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const chatbox = document.getElementById('chatbot');
  const sendBtn = document.getElementById('sendBtn');
  const input = document.getElementById('chatInput');

  addMessage('assistant', chatMessages[1].content);

  sendBtn.addEventListener('click', () => {
    const text = input.value.trim();
    if (text) {
      input.value = '';
      sendToOpenAI(text);
    }
  });
});
