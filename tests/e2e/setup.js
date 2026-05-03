/**
 * Setup global dos testes E2E.
 * - Verifica se o servidor está rodando
 * - Faz login uma vez e salva o storage state (cookies)
 *   para que os testes de UI não precisem fazer login a cada execução
 */
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const BASE_URL = 'http://localhost:8000';
const TEST_EMAIL    = process.env.TEST_EMAIL    || 'playwright.teste@gmail.com';
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'Playwright@2026';

const STORAGE_STATE = path.resolve(__dirname, '.auth-state.json');

async function globalSetup() {
  const http = require('http');

  // 1. Verifica servidor
  await new Promise((resolve, reject) => {
    const req = http.get(`${BASE_URL}/api/health`, (res) => {
      if (res.statusCode === 200) { console.log('✅ Servidor rodando em', BASE_URL); resolve(); }
      else reject(new Error(`Servidor retornou ${res.statusCode}`));
    });
    req.on('error', () => reject(new Error(`Servidor não está rodando em ${BASE_URL}`)));
    req.setTimeout(5000, () => reject(new Error('Timeout ao conectar ao servidor')));
  });

  // 2. Login via API para obter cookie
  const res = await fetch(`${BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: TEST_EMAIL, senha: TEST_PASSWORD }),
  });

  if (res.status !== 200) {
    console.warn(`⚠️  Login falhou (${res.status}). Execute: python tests/e2e/create_test_user.py`);
    return;
  }

  // 3. Extrai o cookie de sessão
  const setCookie = res.headers.get('set-cookie') || '';
  const cookieMatch = setCookie.match(/agendamedica_token=([^;]+)/);
  if (!cookieMatch) {
    console.warn('⚠️  Cookie de sessão não encontrado na resposta');
    return;
  }

  // 4. Salva storage state com o cookie
  const fs = require('fs');
  const storageState = {
    cookies: [{
      name: 'agendamedica_token',
      value: cookieMatch[1],
      domain: 'localhost',
      path: '/',
      expires: -1,
      httpOnly: true,
      secure: false,
      sameSite: 'Lax',
    }],
    origins: [],
  };
  fs.writeFileSync(STORAGE_STATE, JSON.stringify(storageState, null, 2));
  console.log('✅ Sessão salva em', STORAGE_STATE);
  console.log('✅ Credenciais de teste válidas para:', TEST_EMAIL);
}

module.exports = globalSetup;
module.exports.STORAGE_STATE = STORAGE_STATE;
