// Run: node scripts/test_tracker_merge.js
// Guards the data-loss path where a tracker page opened before a push used to PUT its
// whole stale array back, deleting rows the push added and reverting phone-side edits.
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const src = fs.readFileSync(path.join(__dirname, '..', 'static', 'js', 'storage.js'), 'utf8');
const ctx = { fetch: async () => ({ ok: false }), localStorage: { getItem: () => null, setItem() {}, removeItem() {} } };
vm.createContext(ctx);
vm.runInContext(src, ctx);
const mergeRows = ctx.mergeRows;

const assert = (cond, msg) => { if (!cond) { console.error('FAIL: ' + msg); process.exit(1); } };
const clone = v => JSON.parse(JSON.stringify(v));

// base: what the page loaded. local: user tapped "Applied". fresh: server after a push
// that added a row and (elsewhere) set another row's link.
const base = [
  { id: 'a', company: 'IBM', role: 'SWE', status: 'saved', link: 'https://ibm.example/job' },
  { id: 'b', company: 'Movate', role: 'Trainee', status: 'saved', link: '' },
];
const local = clone(base);
local[0].status = 'applied';                       // the only thing the user changed
const fresh = clone(base);
fresh[1].link = 'https://movate.example/job';      // typed on the phone from another tab
fresh.push({ id: 'virtusa', company: 'Virtusa', role: 'Associate Engineer', status: 'saved' });

const out = mergeRows(base, local, fresh);
assert(out.length === 3, 'push row must survive: got ' + out.length);
assert(out[0].status === 'applied', 'user status edit must land');
assert(out[0].link === 'https://ibm.example/job', 'untouched link must stay');
assert(out[1].link === 'https://movate.example/job', 'other-tab link must not be reverted');
assert(out[1].status === 'saved', 'other-tab status must not move');

// delete here still deletes
assert(mergeRows(base, [local[0]], fresh).length === 2, 'delete must propagate');

// undo re-adds
const deleted = [local[0]];
assert(mergeRows(deleted, local, fresh).length === 3, 'undo must re-add the row');

// server unreachable -> caller gets nothing to write
assert(Array.isArray(ctx.mergeRows(base, local, null)) && ctx.mergeRows(base, local, null).length === 2,
  'null server value must not blank the array');

console.log('ok: tracker merge preserves push rows and cross-device edits');