const CV_TEXT = `Lennon Mueller
Home/Work: (419) 283-3243
Email: muellerlennon@gmail.com
 

EDUCATION
 
2025    Certification in Applied Data Science & AI, Massachusetts Institute of Technology Professional Education

2023     MS in Data Analytics, Southern New Hampshire University
2013     B.A. in Psychology, Ohio Christian University
 
EMPLOYMENT

 Present, Independent Consultant, Upwork
-	Support client AI/ML projects from initial vision to finished product
-	Working with diverse clients around the world to map out the road from idea to implementation
-	Consulting with clients to identify threats to project success and the best way to deal with them
-	Reviewing client’s code when necessary and providing documentation or my own code to resolve issues on the road to implementation
October 2022 –Present, Data Scientist, Western Governors University
-	Engineered AI/ML solutions for the Learning Analytics (LA) team leveraging Databricks resources to their fullest extent. Successfully completed 3 major reworks of existing ML pipelines across the LA team to scale up and automate recommendation engines, increasing student coverage by 190% (25% coverage to 73% coverage).
-	Led WGU in utilizing Databricks emerging tech to develop and scale LLM solutions. Collaborated closely with Databricks solutions architects and several teams across WGU to overcome technical challenges and then pass learned lessons onto other teams within WGU and present LLM to Databricks.

August 2019 – October 2022, Data Analyst, Indiana Wesleyan University
-	Duties: Leveraging AI and machine-learning tools and techniques to provide analytical support to decision-makers. Database query and data analysis using R, Python, SQL and Veera Construct, Microsoft Power Bi, Excel, and SPSS. Quantitative data analysis including parametric (t-test, F-test, Pearson correlation) and non-parametric (Spearman correlation, U-test) significance testing, linear regression, machine-learning algorithms, predictive modeling, and forecasting.

RESEARCH AND PROJECT EXPERIENCE
 
December 2022-Present, Sequencing Recommendation Engine, Western Governors University
▪ Inherited a proof-of-concept recommendation engine for recommending the order in which students should take courses. Scaled from 15% to 50% coverage in first year of ownership.
▪ Modeling involves K-means clustering and XGboost regression. Python modeling code loops through program data applying program-specific preprocessing and relying on Lasson regularization for feature selection for each program. Modeling is fully automated with regular performance monitoring and automated alert system.

December 2021-April 2022, H.O.P.E. Dashboard, Indiana Wesleyan University
▪ Constructed a student risk algorithm to detect at-risk students. Model detects future withdrawals with 91.7% accuracy (last accuracy assessment on 8/22/22 with risk data on 1,099 students).
▪ Algorithm and accompanying student academic, demographic, and contact info were built into a Power BI dashboard. Dashboard was then piloted with advising teams and successfully implemented in April 2022. Mass communication feature added to dashboard allowing advisors to quickly identify and reach out to at-risk students. Dashboard is now main tool for advisors and has increased student contacts by more than 10x and reduced time required to identify and reach out to at-risk students by nearly 100%.
▪ Risk algorithm was used to produce a risk history for every enrolled student. Risk history displays the daily evolution of a student’s risk score throughout their academic journey and has enabled the use of AI and machine-learning techniques to identify patterns of risk score behavior indicative of future withdrawal. 
`;
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
    body: JSON.stringify({model:'gpt-4.1-mini', messages: chatMessages})
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
