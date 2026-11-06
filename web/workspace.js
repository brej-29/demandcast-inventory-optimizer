export function salesPage(series, query = '', page = 0, size = 20) {
  const rows = series.filter(row => row.date.includes(query.trim()));
  const pages = Math.max(1, Math.ceil(rows.length / size));
  const index = Math.min(Math.max(0, page), pages - 1);
  return { rows: rows.slice(index * size, (index + 1) * size), total: rows.length, pages, page: index };
}
export function snapshot(name, settings, result) {
  if (!result || !Object.values(settings).every(Number.isFinite)) throw new Error('A valid calculation is required.');
  return { name: name.trim().slice(0, 60) || 'Untitled scenario', settings: { ...settings }, order: result.order, target: result.target, buffer: result.buffer };
}
