/**
 * Testes de Pacientes
 * Usa storage state — já autenticado via setup.js
 */
const { test, expect } = require('@playwright/test');
const { BASE_URL, TEST_EMAIL, TEST_PASSWORD } = require('../helpers/auth');

const PACIENTE_NOME = `Playwright Teste ${Date.now()}`;
const PACIENTE_TEL  = `119${String(Date.now()).slice(-8)}`;

test.describe('Pacientes', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/#/pacientes');
    await expect(page.locator('.patient-list, .muted')).toBeVisible({ timeout: 10_000 });
  });

  test('exibe campo de busca de pacientes', async ({ page }) => {
    await expect(page.locator('input[placeholder*="nome ou telefone"]')).toBeVisible();
  });

  test('exibe botão de novo paciente', async ({ page }) => {
    const btnNovo = page.locator('.btn.primary').filter({ hasText: /novo paciente/i }).first();
    await expect(btnNovo).toBeVisible();
  });

  test('abre modal de novo paciente ao clicar no botão', async ({ page }) => {
    // O botão pode ter texto "+ Novo paciente" ou "Novo paciente"
    const btnNovo = page.locator('button.btn.primary, a.btn.primary').filter({ hasText: /paciente/i }).first();
    await expect(btnNovo).toBeVisible({ timeout: 5_000 });
    await btnNovo.click();
    await expect(page.locator('.modal .panel')).toBeVisible({ timeout: 5_000 });
  });

  test('cria novo paciente com sucesso', async ({ page }) => {
    const btnNovo = page.locator('button.btn.primary, a.btn.primary').filter({ hasText: /paciente/i }).first();
    await btnNovo.click();
    await expect(page.locator('.modal .panel')).toBeVisible({ timeout: 5_000 });

    // Preenche o primeiro input (nome) e o segundo (telefone)
    const inputs = page.locator('.modal input');
    await inputs.first().fill(PACIENTE_NOME);
    const count = await inputs.count();
    if (count >= 2) await inputs.nth(1).fill(PACIENTE_TEL);

    await page.locator('.modal .btn.primary').click();
    await expect(page.locator('.modal .panel')).toBeHidden({ timeout: 8_000 });
  });

  test('busca em tempo real filtra pacientes', async ({ page }) => {
    const busca = page.locator('input[placeholder*="nome ou telefone"]');
    await busca.fill('zzzzinexistente999');
    // Aguarda debounce + resposta
    await page.waitForTimeout(600);
    // Não deve haver nenhum paciente com esse nome
    const pacienteNomes = page.locator('.patient-nome');
    const count = await pacienteNomes.count();
    expect(count).toBe(0);
  });

  test('botão de exportar Excel está visível', async ({ page }) => {
    await expect(page.locator('.btn-excel').first()).toBeVisible();
  });

  test('API de exportação Excel retorna arquivo', async ({ request }) => {
    // O request context do projeto mobile já tem o storageState com o cookie
    const exportRes = await request.get(`${BASE_URL}/api/patients/export/excel`);
    expect(exportRes.status()).toBe(200);
    expect(exportRes.headers()['content-type']).toContain('spreadsheetml');
  });

});
