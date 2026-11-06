import { salesPage, snapshot } from './workspace.js';
export function createDesk({ getSeries, getResult, getSettings, restore, download }) {
  const root = document.createElement('section');
  root.className = 'decision-desk';
  root.setAttribute('aria-labelledby', 'desk-title');
  root.innerHTML = `<div class="section-intro"><div><h2 id="desk-title">Compare before you commit</h2><p>Keep up to four scenarios for this dataset. Session only; changing datasets clears them.</p></div></div>
    <form class="desk-toolbar" id="scenario-form"><div class="field"><label for="scenario-name">Scenario name</label><input id="scenario-name" maxlength="60" placeholder="e.g. Extra delivery buffer"></div><button class="primary" id="save-scenario" disabled>Save current scenario</button></form>
    <p id="desk-status" role="status">No saved scenarios yet. Adjust assumptions, then save a comparison.</p>
    <p class="table-hint">Scroll to compare all scenarios and actions.</p><div class="table-wrap" tabindex="0" role="region" aria-label="Saved scenarios"><table><caption class="sr-only">Saved assumptions and decisions</caption><thead><tr><th>Scenario</th><th>Lead / review</th><th>Coverage</th><th>Target</th><th>Order</th><th>Actions</th></tr></thead><tbody id="scenario-rows"></tbody></table></div>
    <details class="sales-ledger"><summary>Explore daily sales</summary><div class="desk-toolbar"><div class="field"><label for="sales-search">Filter dates (YYYY-MM-DD)</label><input id="sales-search" type="search" placeholder="2025-01"></div><button class="secondary" type="button" id="sales-export">Export loaded sales</button></div><p id="sales-summary" role="status"></p><div class="table-wrap"><table><caption class="sr-only">Daily observed sales</caption><thead><tr><th>Date</th><th>Units sold</th></tr></thead><tbody id="sales-rows"></tbody></table></div><div class="ledger-pagination"><button class="secondary" id="sales-prev" type="button">Previous page</button><span id="sales-page"></span><button class="secondary" id="sales-next" type="button">Next page</button></div></details>`;
  document.getElementById('workspace').append(root);
  const $ = id => root.querySelector('#' + id);
  let saved = [], page = 0;
  const status = message => { $('desk-status').textContent = message; };
  function renderSales() {
    const data = salesPage(getSeries(), $('sales-search').value, page);
    page = data.page;
    $('sales-rows').replaceChildren(...data.rows.map(row => {
      const tr = document.createElement('tr');
      for (const value of [row.date, row.sales.toLocaleString('en-GB')]) { const td = document.createElement('td'); td.textContent = value; tr.append(td); }
      return tr;
    }));
    $('sales-summary').textContent = `${data.total} matching days. Zero sales are retained.`;
    $('sales-page').textContent = `Page ${page + 1} of ${data.pages}`;
    $('sales-prev').disabled = page === 0;
    $('sales-next').disabled = page + 1 >= data.pages;
  }
  function render() {
    $('scenario-rows').replaceChildren(...saved.map((item, index) => {
      const tr = document.createElement('tr');
      for (const value of [item.name, `${item.settings.lead} / ${item.settings.review} days`, `${item.settings.coverage * 100}%`, item.target.toLocaleString('en-GB'), item.order.toLocaleString('en-GB')]) {
        const td = document.createElement('td'); td.textContent = value; tr.append(td);
      }
      const actions = document.createElement('td');
      for (const label of ['Restore', 'Remove']) {
        const button = document.createElement('button'); button.type = 'button'; button.className = 'text-button'; button.textContent = label; button.setAttribute('aria-label', `${label} ${item.name}`);
        button.onclick = () => {
          if (label === 'Restore') { restore(item.settings); status(`Restored ${item.name}. Recalculating with these assumptions.`); }
          else { saved.splice(index, 1); render(); status(`Removed ${item.name}.`); $('scenario-name').focus(); }
        };
        actions.append(button);
      }
      tr.append(actions); return tr;
    }));
    update();
  }
  function update() { $('save-scenario').disabled = !getResult() || saved.length >= 4; }
  $('scenario-form').onsubmit = event => {
    event.preventDefault(); if (!getResult() || saved.length >= 4) return;
    saved.push(snapshot($('scenario-name').value || `Scenario ${saved.length + 1}`, getSettings(), getResult()));
    $('scenario-name').value = ''; render(); status(`${saved.length} of 4 scenarios saved. Restore any scenario to recalculate.`);
  };
  $('sales-search').oninput = () => { page = 0; renderSales(); };
  $('sales-prev').onclick = () => { page--; renderSales(); };
  $('sales-next').onclick = () => { page++; renderSales(); };
  $('sales-export').onclick = () => download('date,sales\n' + getSeries().map(row => `${row.date},${row.sales}`).join('\n'), 'demandcast-loaded-sales.csv');
  return { update, reset() { saved = []; page = 0; $('sales-search').value = ''; render(); renderSales(); status('No saved scenarios yet. Adjust assumptions, then save a comparison.'); } };
}
