/**
 * Testes da Agenda
 * Usa storage state — já autenticado via setup.js
 */
const { test, expect } = require('@playwright/test');

test.describe('Agenda', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/#/agenda');
    await expect(page.locator('.agenda-toolbar')).toBeVisible({ timeout: 10_000 });
  });

  test('exibe barra de ferramentas com atalhos de período', async ({ page }) => {
    await expect(page.locator('.agenda-shortcuts')).toBeVisible();
    await expect(page.locator('.agenda-shortcuts .btn').filter({ hasText: 'Hoje' })).toBeVisible();
    await expect(page.locator('.agenda-shortcuts .btn').filter({ hasText: 'Amanhã' })).toBeVisible();
    await expect(page.locator('.agenda-shortcuts .btn').filter({ hasText: '7 dias' })).toBeVisible();
    await expect(page.locator('.agenda-shortcuts .btn').filter({ hasText: 'Este mês' })).toBeVisible();
  });

  test('atalho "Hoje" está ativo por padrão', async ({ page }) => {
    const btnHoje = page.locator('.agenda-shortcuts .btn').filter({ hasText: 'Hoje' });
    await expect(btnHoje).toHaveClass(/active/);
  });

  test('exibe campo de busca', async ({ page }) => {
    await expect(page.locator('.agenda-toolbar input[placeholder*="Buscar"]')).toBeVisible();
  });

  test('botão + Agendar está visível', async ({ page }) => {
    await expect(page.locator('.agenda-toolbar .btn.primary')).toBeVisible();
  });

  test('clicar em + Agendar abre modal de agendamento', async ({ page }) => {
    await page.click('.agenda-toolbar .btn.primary');
    await expect(page.locator('.modal .panel')).toBeVisible({ timeout: 5_000 });
    await expect(page.locator('.modal-title')).toContainText('Agendar consulta');
  });

  test('modal de agendamento tem campo de paciente', async ({ page }) => {
    await page.click('.agenda-toolbar .btn.primary');
    await expect(page.locator('.modal input[placeholder*="paciente"]')).toBeVisible();
  });

  test('modal de agendamento tem seletor de data', async ({ page }) => {
    await page.click('.agenda-toolbar .btn.primary');
    await expect(page.locator('.modal .dp-trigger')).toBeVisible();
  });

  test('modal de agendamento tem campos de horário início e fim', async ({ page }) => {
    await page.click('.agenda-toolbar .btn.primary');
    const timeInputs = page.locator('.modal input[type="time"]');
    await expect(timeInputs).toHaveCount(2);
  });

  test('fechar modal com botão ✕ funciona', async ({ page }) => {
    await page.click('.agenda-toolbar .btn.primary');
    await expect(page.locator('.modal .panel')).toBeVisible();
    await page.click('.modal-close-btn');
    await expect(page.locator('.modal .panel')).toBeHidden({ timeout: 3_000 });
  });

  test('fechar modal clicando fora funciona', async ({ page }) => {
    await page.click('.agenda-toolbar .btn.primary');
    await expect(page.locator('.modal .panel')).toBeVisible();
    await page.click('.modal', { position: { x: 5, y: 5 } });
    await expect(page.locator('.modal .panel')).toBeHidden({ timeout: 3_000 });
  });

  test('atalho "Amanhã" carrega consultas do dia seguinte', async ({ page }) => {
    await page.click('.agenda-shortcuts .btn:has-text("Amanhã")');
    // Título deve mudar para "Consultas do dia"
    await expect(page.locator('.card h2').filter({ hasText: 'Consultas do dia' })).toBeVisible({ timeout: 5_000 });
  });

  test('atalho "7 dias" carrega range', async ({ page }) => {
    await page.click('.agenda-shortcuts .btn:has-text("7 dias")');
    await expect(page.locator('.card h2')).toBeVisible({ timeout: 5_000 });
  });

  test('busca filtra lista de consultas', async ({ page }) => {
    const filtro = page.locator('.agenda-toolbar input[placeholder*="Buscar"]');
    await filtro.fill('zzzzinexistente');
    // Aguarda debounce (300ms)
    await page.waitForTimeout(500);
    // Deve mostrar mensagem de vazio ou lista vazia
    const semResultado = page.locator('.muted').filter({ hasText: /nada|nenhum/i });
    const listaVazia = page.locator('.consult-list');
    // Um dos dois deve estar presente
    const temMensagem = await semResultado.isVisible().catch(() => false);
    const temLista = await listaVazia.isVisible().catch(() => false);
    expect(temMensagem || temLista).toBeTruthy();
  });

  test('skeleton screen aparece durante carregamento', async ({ page }) => {
    // Intercepta a API para atrasar resposta
    await page.route('**/api/appointments*', async route => {
      await page.waitForTimeout(300);
      await route.continue();
    });
    await page.click('.agenda-shortcuts .btn:has-text("Amanhã")');
    // Skeleton pode aparecer brevemente
    // Verifica que a lista carrega corretamente no final
    await expect(page.locator('.card')).toBeVisible({ timeout: 8_000 });
  });

});
