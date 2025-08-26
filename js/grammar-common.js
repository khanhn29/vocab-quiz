// Common JavaScript functions for grammar lessons

// Function to go back to index
function goToIndex() {
  window.location.href = 'index.html';
}

// Function to create lesson header dynamically
function createLessonHeader(lessonNumber, koreanTitle, vietnameseTitle) {
  return `
    <div class="lesson-header">
      <h1 class="lesson-title">Bài ${lessonNumber}: ${koreanTitle} (${vietnameseTitle})</h1>
      <p class="lesson-subtitle">Ngữ Pháp Tiếng Hàn Tổng Hợp Sơ Cấp 1</p>
    </div>
  `;
}

// Function to create header bar
function createHeaderBar(lessonTitle) {
  return `
    <div class="header-bar">
      <button class="back-button" onclick="goToIndex()">
        <span class="back-arrow">←</span>
        <span>Quay lại</span>
      </button>
      <h1 class="header-title">${lessonTitle}</h1>
    </div>
  `;
}

// Function to create grammar section
function createGrammarSection(icon, title, content) {
  return `
    <div class="grammar-section">
      <h2 class="section-title">
        <span class="section-icon">${icon}</span>
        ${title}
      </h2>
      ${content}
    </div>
  `;
}

// Function to create grammar point
function createGrammarPoint(title, description, examples = []) {
  let examplesHtml = examples.map(example => 
    `<div class="example-box">
      <div class="korean-text">${example.korean}</div>
      <div class="translation">${example.translation}</div>
    </div>`
  ).join('');

  return `
    <div class="grammar-point">
      <h3 class="point-title">${title}</h3>
      <p class="point-description">${description}</p>
      ${examplesHtml}
    </div>
  `;
}

// Function to create rule box
function createRuleBox(title, rules) {
  let rulesHtml = '';
  if (Array.isArray(rules)) {
    rulesHtml = `<ul>${rules.map(rule => `<li>${rule}</li>`).join('')}</ul>`;
  } else {
    rulesHtml = `<p>${rules}</p>`;
  }

  return `
    <div class="rule-box">
      <div class="rule-title">${title}</div>
      ${rulesHtml}
    </div>
  `;
}

// Function to create table
function createTable(headers, rows, tableClass = 'number-table') {
  let headersHtml = headers.map(header => `<th>${header}</th>`).join('');
  let rowsHtml = rows.map(row => 
    `<tr>${row.map(cell => `<td${cell.class ? ` class="${cell.class}"` : ''}>${cell.content || cell}</td>`).join('')}</tr>`
  ).join('');

  return `
    <table class="${tableClass}">
      <thead>
        <tr>${headersHtml}</tr>
      </thead>
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>
  `;
}
