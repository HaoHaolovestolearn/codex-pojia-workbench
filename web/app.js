'use strict';
const $ = (id) => document.getElementById(id);
let catalog = { recipes: [], errors: [] };
let generated = null;
let noticeTimer;
function notice(message, error = false) {
  $('notice').textContent = message;
  $('notice').className = error ? 'error' : '';
  clearTimeout(noticeTimer);
  noticeTimer = setTimeout(() => { $('notice').textContent = ''; }, 6500);
}
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
  });
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || `HTTP ${response.status}`);
  return value;
}
function showView(name) {
  const valid = ['home', 'prompts', 'requests', 'budget', 'errors'];
  if (!valid.includes(name)) name = 'home';
  document.querySelectorAll('.view').forEach((node) => node.classList.toggle('active', node.id === name));
  document.querySelectorAll('nav button').forEach((node) => node.classList.toggle('active', node.dataset.view === name));
  const names = { home: '概览', prompts: '任务模板', requests: '请求构建器', budget: '费用估算', errors: '错误排查' };
  $('breadcrumb').textContent = '工作台 / ' + names[name];
  if (location.hash !== '#' + name) location.hash = name;
}
document.querySelectorAll('[data-view], [data-open]').forEach((node) => {
  node.addEventListener('click', () => showView(node.dataset.view || node.dataset.open));
});
window.addEventListener('hashchange', () => showView(location.hash.slice(1)));
function profile() { return { base: $('base').value, model: $('model').value, protocol: $('protocol').value }; }
function download(name, body, type) {
  const url = URL.createObjectURL(new Blob([body], { type }));
  const link = document.createElement('a');
  link.href = url; link.download = name; document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}
async function copy(id) {
  try { await navigator.clipboard.writeText($(id).textContent); notice('已复制'); }
  catch (_) { notice('浏览器未允许剪贴板访问，请选中文字手动复制。', true); }
}
function renderRecipes() {
  const search = $('recipe-search').value.toLowerCase();
  $('recipe').replaceChildren();
  catalog.recipes.filter((item) => (item.title + item.summary + item.category).toLowerCase().includes(search)).forEach((item) => {
    const option = document.createElement('option'); option.value = item.id; option.textContent = item.category + ' / ' + item.title;
    $('recipe').append(option);
  });
  updateRecipe();
}
function updateRecipe() {
  const item = catalog.recipes.find((r) => r.id === $('recipe').value);
  $('recipe-summary').textContent = item ? item.summary : '没有匹配模板，请尝试其他关键词。';
}
$('recipe-search').addEventListener('input', renderRecipes);
$('recipe').addEventListener('change', updateRecipe);
$('prompt-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const result = await api('/api/prompt', { recipe: $('recipe').value, goal: $('goal').value, context: $('context').value });
    $('prompt-output').textContent = result.prompt; notice('任务说明已生成');
  } catch (error) { notice(error.message, true); }
});
$('copy-prompt').addEventListener('click', () => copy('prompt-output'));
$('export-prompt').addEventListener('click', () => download('codex-task.md', '# Codex task\n\n' + $('prompt-output').textContent, 'text/markdown;charset=utf-8'));
$('provider').addEventListener('change', () => {
  if ($('provider').value === 'openai') { $('base').value = 'https://api.openai.com/v1'; $('model').value = 'your-model-id'; $('protocol').value = 'responses'; }
  if ($('provider').value === 'deepseek') { $('base').value = 'https://api.deepseek.com'; $('model').value = 'your-deepseek-model-id'; $('protocol').value = 'chat'; }
  if ($('provider').value === 'custom') { $('base').value = 'https://example.com/v1'; $('model').value = 'your-model-id'; }
});
function renderCode() {
  if (!generated) return;
  $('code-output').textContent = generated.snippets[$('language').value];
  $('endpoint').textContent = generated.endpoint;
}
$('request-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    generated = await api('/api/generate', { ...profile(), prompt: $('request-prompt').value });
    renderCode(); notice('地址检查通过，代码示例已生成；未执行网络请求。');
  } catch (error) { notice(error.message, true); }
});
$('language').addEventListener('change', renderCode);
$('copy-code').addEventListener('click', () => copy('code-output'));
$('save-profile').addEventListener('click', async () => {
  try { const value = await api('/api/validate', profile()); localStorage.setItem('nb.workbench.profile.v1', JSON.stringify(value)); notice('非敏感配置已保存在当前浏览器'); }
  catch (error) { notice(error.message, true); }
});
$('export-profile').addEventListener('click', async () => {
  try { const value = await api('/api/validate', profile()); download('codex-provider.json', JSON.stringify(value, null, 2), 'application/json'); }
  catch (error) { notice(error.message, true); }
});
$('reset-profile').addEventListener('click', () => {
  try { localStorage.removeItem('nb.workbench.profile.v1'); }
  catch (_) { notice('浏览器存储不可用，已重置当前页面。', true); }
  $('provider').value = 'custom'; $('base').value = 'https://example.com/v1'; $('model').value = 'your-model-id'; $('protocol').value = 'responses';
  generated = null; $('code-output').textContent = '配置已重置，请重新生成示例。'; $('endpoint').textContent = '';
});
$('budget-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const result = await api('/api/estimate', { input_tokens: $('input-tokens').value, output_tokens: $('output-tokens').value,
      input_price: $('input-price').value, output_price: $('output-price').value, requests: $('requests-count').value });
    $('budget-total').textContent = result.total; $('budget-single').textContent = result.per_request; $('budget-note').textContent = result.note;
  } catch (error) { notice(error.message, true); }
});
function renderErrors() {
  const search = $('error-search').value.toLowerCase(); $('error-cards').replaceChildren();
  const items = catalog.errors.filter((item) => (item.code + item.title + item.detail).toLowerCase().includes(search));
  for (const item of items) {
    const card = document.createElement('article'); card.className = 'error-card';
    const code = document.createElement('span'); code.textContent = item.code;
    const title = document.createElement('h2'); title.textContent = item.title;
    const description = document.createElement('p'); description.textContent = item.detail;
    card.append(code, title, description); $('error-cards').append(card);
  }
  if (!items.length) { const empty = document.createElement('p'); empty.textContent = '没有匹配项，请尝试状态码或其他关键词。'; $('error-cards').append(empty); }
}
$('error-search').addEventListener('input', renderErrors);
(async () => {
  showView(location.hash.slice(1));
  try { catalog = await api('/api/catalog'); renderRecipes(); renderErrors(); }
  catch (_) { notice('资源加载失败，请检查本地服务是否正在运行。', true); }
  try {
    const saved = JSON.parse(localStorage.getItem('nb.workbench.profile.v1') || 'null');
    if (saved) { const value = await api('/api/validate', saved); $('base').value = value.base; $('model').value = value.model; $('protocol').value = value.protocol; }
  } catch (_) { notice('已忽略无效的本地配置，可在请求构建器中重置。', true); }
})();
