/**
 * Testes de API (sem UI)
 * Cobre: todos os endpoints principais via request direto
 */
const { test, expect } = require('@playwright/test');
const { BASE_URL, TEST_EMAIL, TEST_PASSWORD } = require('../helpers/auth');

let authCookies = '';

test.describe('API — Autenticação', () => {

  test('POST /api/auth/login com credenciais válidas retorna 200', async ({ request }) => {
    const res = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { email: TEST_EMAIL, senha: TEST_PASSWORD },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('usuario');
    expect(body.usuario).toHaveProperty('email', TEST_EMAIL);
  });

  test('POST /api/auth/login com senha errada retorna 401', async ({ request }) => {
    const res = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { email: TEST_EMAIL, senha: 'senhaerrada123' },
    });
    expect(res.status()).toBe(401);
  });

  test('GET /api/auth/me sem cookie retorna 401', async ({ browser }) => {
    // Cria contexto limpo sem cookies para testar acesso não autenticado
    const ctx = await browser.newContext({ storageState: undefined });
    const req = await ctx.request;
    const res = await req.get(`${BASE_URL}/api/auth/me`);
    expect(res.status()).toBe(401);
    await ctx.close();
  });

  test('GET /api/auth/me com cookie válido retorna dados do usuário', async ({ request }) => {
    // Login para obter cookie
    const loginRes = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { email: TEST_EMAIL, senha: TEST_PASSWORD },
    });
    expect(loginRes.status()).toBe(200);

    // /me deve funcionar com o cookie da sessão
    const meRes = await request.get(`${BASE_URL}/api/auth/me`);
    expect(meRes.status()).toBe(200);
    const body = await meRes.json();
    expect(body.usuario.email).toBe(TEST_EMAIL);
  });

  test('POST /api/auth/logout retorna 200', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { email: TEST_EMAIL, senha: TEST_PASSWORD },
    });
    const res = await request.post(`${BASE_URL}/api/auth/logout`, { data: {} });
    expect(res.status()).toBe(200);
  });

});

test.describe('API — Dashboard', () => {

  test.beforeEach(async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { email: TEST_EMAIL, senha: TEST_PASSWORD },
    });
  });

  test('GET /api/dashboard retorna estrutura correta', async ({ request }) => {
    const today = new Date().toISOString().slice(0, 10);
    const res = await request.get(`${BASE_URL}/api/dashboard?dia=${today}`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('consultas_do_dia');
    expect(body).toHaveProperty('pacientes_cadastrados');
    expect(body).toHaveProperty('horarios_livres');
    expect(body).toHaveProperty('consultas_canceladas');
    expect(body).toHaveProperty('atendimentos_concluidos');
    expect(Array.isArray(body.horarios_livres)).toBe(true);
  });

  test('GET /api/dashboard sem autenticação retorna 401', async ({ request }) => {
    // Faz logout primeiro
    await request.post(`${BASE_URL}/api/auth/logout`, { data: {} });
    const today = new Date().toISOString().slice(0, 10);
    const res = await request.get(`${BASE_URL}/api/dashboard?dia=${today}`);
    expect(res.status()).toBe(401);
  });

});

test.describe('API — Pacientes', () => {

  test.beforeEach(async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { email: TEST_EMAIL, senha: TEST_PASSWORD },
    });
  });

  test('GET /api/patients retorna lista', async ({ request }) => {
    const res = await request.get(`${BASE_URL}/api/patients`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
  });

  test('POST /api/patients cria paciente', async ({ request }) => {
    const nome = `API Teste ${Date.now()}`;
    const tel  = `119${String(Date.now()).slice(-8)}`;
    const res = await request.post(`${BASE_URL}/api/patients`, {
      data: { nome_completo: nome, telefone: tel },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body.nome_completo).toBe(nome);
    expect(body.telefone).toBe(tel);

    // Limpa: deleta o paciente criado
    await request.delete(`${BASE_URL}/api/patients/${body.id}`);
  });

  test('POST /api/patients sem nome retorna 422', async ({ request }) => {
    const res = await request.post(`${BASE_URL}/api/patients`, {
      data: { telefone: '11999999999' },
    });
    expect(res.status()).toBe(422);
  });

  test('GET /api/patients com busca filtra resultados', async ({ request }) => {
    const res = await request.get(`${BASE_URL}/api/patients?search=zzzzinexistente`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveLength(0);
  });

  test('DELETE /api/patients/{id} inexistente retorna 404', async ({ request }) => {
    const res = await request.delete(`${BASE_URL}/api/patients/00000000-0000-0000-0000-000000000000`);
    expect(res.status()).toBe(404);
  });

});

test.describe('API — Consultas', () => {

  let pacienteId = null;

  test.beforeAll(async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { email: TEST_EMAIL, senha: TEST_PASSWORD },
    });
    // Cria paciente para usar nos testes de consulta
    const res = await request.post(`${BASE_URL}/api/patients`, {
      data: { nome_completo: `Paciente Consulta ${Date.now()}`, telefone: `119${String(Date.now()).slice(-8)}` },
    });
    if (res.status() === 201) {
      const body = await res.json();
      pacienteId = body.id;
    }
  });

  test.afterAll(async ({ request }) => {
    if (pacienteId) {
      await request.delete(`${BASE_URL}/api/patients/${pacienteId}`);
    }
  });

  test.beforeEach(async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { email: TEST_EMAIL, senha: TEST_PASSWORD },
    });
  });

  test('GET /api/appointments?day= retorna lista', async ({ request }) => {
    const today = new Date().toISOString().slice(0, 10);
    const res = await request.get(`${BASE_URL}/api/appointments?day=${today}`);
    expect(res.status()).toBe(200);
    expect(Array.isArray(await res.json())).toBe(true);
  });

  test('POST /api/appointments cria consulta', async ({ request }) => {
    if (!pacienteId) test.skip();

    const amanha = new Date();
    amanha.setDate(amanha.getDate() + 1);
    amanha.setHours(10, 0, 0, 0);
    const fim = new Date(amanha.getTime() + 30 * 60 * 1000);

    const res = await request.post(`${BASE_URL}/api/appointments`, {
      data: {
        paciente_id: pacienteId,
        inicio: amanha.toISOString(),
        fim: fim.toISOString(),
        status: 'agendada',
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body.status).toBe('agendada');
    expect(body.paciente_id).toBe(pacienteId);

    // Cancela para limpar
    await request.post(`${BASE_URL}/api/appointments/${body.id}/cancel`, { data: {} });
  });

  test('GET /api/appointments/upcoming retorna lista', async ({ request }) => {
    const res = await request.get(`${BASE_URL}/api/appointments/upcoming`);
    expect(res.status()).toBe(200);
    expect(Array.isArray(await res.json())).toBe(true);
  });

  test('GET /api/health retorna ok', async ({ request }) => {
    const res = await request.get(`${BASE_URL}/api/health`);
    expect(res.status()).toBe(200);
    expect((await res.json()).ok).toBe(true);
  });

});
