import test from 'node:test';
import assert from 'node:assert/strict';
import { salesPage, snapshot } from '../../web/workspace.js';
test('ledger filtering clamps pages and preserves zero sales', () => {
  const rows = [{date:'2025-01-01',sales:0},{date:'2025-02-01',sales:2}];
  assert.equal(salesPage(rows, '2025-01', 99, 1).rows[0].sales, 0);
  assert.deepEqual(salesPage(rows, 'missing').rows, []);
  assert.equal(salesPage(rows, '', -1, 1).page, 0);
});
test('scenario takes an independent copy and rejects invalid calculation', () => {
  const settings = {onHand: 20};
  const saved = snapshot('  Baseline  ', settings, {order: 12,target:32,buffer:4});
  settings.onHand = 99;
  assert.equal(saved.settings.onHand,20);
  assert.equal(saved.name,'Baseline');
  assert.throws(() => snapshot('bad',{lead:NaN},{order:1}));
  assert.throws(() => snapshot('bad',{},null));
});
