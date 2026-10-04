function updateRows() {
  const countInput = document.getElementById('day-count');
  const body = document.getElementById('daily-inputs');
  const template = document.getElementById('day-row-template');
  if (!countInput || !body || !template) return;
  const count = Math.max(1, Math.min(14, Number(countInput.value) || 1));
  while (body.rows.length > count) body.deleteRow(-1);
  while (body.rows.length < count) body.appendChild(template.content.cloneNode(true));
  [...body.rows].forEach((row, index) => {
    [...row.querySelectorAll('input')].forEach((input) => {
      const base = input.dataset.name || input.name.replace(/_\d+$/, '');
      input.name = `${base}_${index}`;
      if (base === 'day' && (input.value === 'Day' || !input.value)) input.value = `Day ${index + 1}`;
    });
  });
  countInput.value = count;
}

function updateLiveSummary() {
  const days = document.getElementById('day-count');
  const budget = document.getElementById('water-budget');
  const daysOutput = document.getElementById('live-days');
  const budgetOutput = document.getElementById('live-budget');
  if (days && daysOutput) daysOutput.textContent = `${days.value || 1} days`;
  if (budget && budgetOutput) budgetOutput.textContent = `${budget.value || 0} L available`;
}

document.getElementById('day-count')?.addEventListener('change', () => {
  updateRows();
  updateLiveSummary();
});
document.getElementById('day-count')?.addEventListener('input', updateLiveSummary);
document.getElementById('water-budget')?.addEventListener('input', updateLiveSummary);
document.getElementById('reset-sample')?.addEventListener('click', () => window.location.reload());

const insightDialog = document.getElementById('insight-dialog');
const dialogTitle = document.getElementById('dialog-title');
const dialogText = document.getElementById('dialog-text');
const dialogTip = document.getElementById('dialog-tip');
const dialogIcon = document.getElementById('dialog-icon');

document.querySelectorAll('[data-insight-title]').forEach((button) => {
  button.addEventListener('click', () => {
    if (!insightDialog) return;
    dialogTitle.textContent = button.dataset.insightTitle;
    dialogText.textContent = button.dataset.insightText;
    dialogTip.textContent = button.dataset.insightTip;
    dialogIcon.textContent = button.dataset.icon || '💡';
    if (typeof insightDialog.showModal === 'function') insightDialog.showModal();
    else insightDialog.setAttribute('open', '');
  });
});

insightDialog?.querySelector('.dialog-close')?.addEventListener('click', () => insightDialog.close());
insightDialog?.addEventListener('click', (event) => {
  const bounds = insightDialog.getBoundingClientRect();
  const outside = event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom;
  if (outside) insightDialog.close();
});

function drawComparisonChart(canvas, data) {
  if (!canvas || !data) return;
  const ctx = canvas.getContext('2d');
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth;
  const height = Number(canvas.getAttribute('height'));
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  ctx.scale(ratio, ratio);
  const pad = { top: 24, right: 20, bottom: 52, left: 45 };
  const graphW = width - pad.left - pad.right;
  const graphH = height - pad.top - pad.bottom;
  const max = Math.max(10, ...data.greedy, ...data.dynamic);
  ctx.font = '12px system-ui';
  ctx.strokeStyle = '#dce7e3';
  ctx.fillStyle = '#63736d';
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + graphH * i / 4;
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(width - pad.right, y); ctx.stroke();
    ctx.fillText(`${Math.round(max * (4 - i) / 4)} L`, 5, y + 4);
  }
  const group = graphW / data.labels.length;
  const barW = Math.min(18, group * 0.3);
  data.labels.forEach((label, i) => {
    const x = pad.left + group * i + group / 2;
    const gh = data.greedy[i] / max * graphH;
    const dh = data.dynamic[i] / max * graphH;
    ctx.fillStyle = '#f4a261'; ctx.fillRect(x - barW, pad.top + graphH - gh, barW, gh);
    ctx.fillStyle = '#16866f'; ctx.fillRect(x, pad.top + graphH - dh, barW, dh);
    ctx.fillStyle = '#63736d'; ctx.textAlign = 'center';
    ctx.fillText(label.replace('Day ', 'D'), x, height - 27);
  });
  ctx.textAlign = 'left'; ctx.fillStyle = '#f4a261'; ctx.fillRect(pad.left, height - 12, 12, 8);
  ctx.fillStyle = '#33433d'; ctx.fillText('Greedy', pad.left + 17, height - 4);
  ctx.fillStyle = '#16866f'; ctx.fillRect(pad.left + 85, height - 12, 12, 8);
  ctx.fillStyle = '#33433d'; ctx.fillText('Dynamic Programming', pad.left + 102, height - 4);
}
