# Relatório Consolidado de Implementações

**Projeto:** Agenda do Médico

**Data do relatório:** 19 de junho de 2026

**Branch:** `codex/tema-medico-correto`

## 1. Objetivo

Este documento consolida as alterações realizadas a partir da análise de layout e
usabilidade do sistema Agenda do Médico, além da investigação e correção do erro
de envio de mensagens do WhatsApp para pacientes.

As implementações foram divididas em duas entregas:

1. Melhorias de interface no dashboard, pacientes, perfil e instalação PWA.
2. Diagnóstico e correção dos parâmetros do template de WhatsApp do paciente.

## 2. Melhorias de Layout e Usabilidade

### 2.1. Dashboard

Os cards de resumo foram aprimorados para facilitar a identificação visual das
informações:

- ícone de calendário no card de consultas do dia;
- indicador vermelho no card de consultas canceladas;
- indicador verde no card de consultas concluídas;
- bordas, cores e elementos decorativos coerentes com cada situação;
- preservação da compatibilidade com os temas claro e escuro.

Quando não existe próxima consulta no dia, a área deixou de apresentar somente
uma mensagem vazia e passou a exibir:

- ícone de calendário;
- explicação curta sobre a ausência de consultas;
- botão `+ Agendar nova consulta`;
- link direto para a agenda na data atual.

Os horários livres passaram a ser organizados em:

- Manhã;
- Tarde;
- Noite.

Cada período mostra a quantidade de horários disponíveis e uma grade de botões
com acesso direto ao agendamento.

### 2.2. Tela de Pacientes

A listagem de pacientes foi reorganizada para oferecer mais recursos de busca e
acompanhamento.

Foram adicionados:

- filtro `Todos`;
- filtro `Atendidos recentemente`;
- filtro `Com pendências`;
- ordenação por nome;
- ordenação pelo atendimento mais recente;
- ordenação pelo cadastro mais recente;
- paginação de dez registros;
- contador de registros e páginas;
- coluna de contato;
- coluna de último atendimento;
- indicador de consulta pendente;
- indicador de paciente em dia;
- estado vazio quando nenhum registro corresponde aos filtros.

No celular, a tabela se adapta para cards compactos, mantendo nome, telefone,
avatar e menu de ações.

### 2.3. Dados Adicionais na API de Pacientes

A API de pacientes passou a retornar dados calculados para apoiar os novos
filtros:

- `ultimo_atendimento`: data da consulta concluída mais recente;
- `tem_pendencia`: informa se o paciente possui consulta futura agendada ou
  confirmada.

A consulta foi implementada de forma agrupada, evitando consultas repetidas ao
banco para cada paciente.

O endpoint também recebeu um parâmetro `limit`, validado entre 1 e 500 registros.

### 2.4. Tela de Perfil

As configurações do perfil foram divididas em quatro abas:

- Dados pessoais;
- Segurança;
- Notificações;
- Aparência.

Distribuição das configurações:

- **Dados pessoais:** foto, nome, CRM, especialidade, clínica, telefone e e-mail;
- **Segurança:** alteração de senha e informações do plano;
- **Notificações:** lembretes, mensagens do WhatsApp, push e testes de canais;
- **Aparência:** seleção dos temas claro e escuro.

A última aba utilizada é preservada durante a sessão do navegador.

### 2.5. Instalação PWA

O aviso de instalação foi reduzido para não ocupar toda a largura da tela no
desktop.

Também foi incluída a ação `Instalar aplicativo` no menu do perfil quando o
navegador disponibiliza a instalação.

O comportamento de descarte do aviso na sessão foi preservado.

### 2.6. Responsividade

As novas interfaces foram verificadas nos formatos desktop e celular.

Foram feitos ajustes específicos para:

- cards do dashboard;
- estado vazio de próxima consulta;
- agrupamento de horários;
- filtros horizontais;
- listagem de pacientes;
- paginação;
- navegação por abas;
- banner de instalação PWA.

## 3. Investigação do WhatsApp

### 3.1. Erro Relatado

O teste retornava:

```text
Médico: enviado com sucesso via template 'agenda_medico_resumo_v2'.
Paciente: WhatsApp Cloud API erro 400 (132018):
There's an issue with the parameters in your template.
```

O sucesso do envio ao médico confirmou que:

- o token de acesso estava válido;
- o Phone Number ID estava correto;
- a integração com a Cloud API estava funcionando;
- o problema estava restrito ao payload do template do paciente.

### 3.2. Definição Consultada na Meta

O template aprovado do paciente é:

```text
agenda_paciente_lembrete
```

Sua definição possui:

- idioma `pt_BR`;
- status `APPROVED`;
- formato de parâmetros `POSITIONAL`;
- cinco parâmetros no componente `BODY`;
- nenhum botão ou quick reply.

Ordem esperada:

1. primeiro nome do paciente;
2. data;
3. hora;
4. clínica;
5. médico.

O template aprovado do médico possui cinco parâmetros e nenhum botão.

### 3.3. Causa do Erro

O sistema enviava corretamente os cinco parâmetros do corpo, mas acrescentava
dois componentes de botão:

```text
confirmar:{consulta_id}
cancelar:{consulta_id}
```

Como esses botões não existem no template aprovado
`agenda_paciente_lembrete`, a Meta rejeitava o payload com o código `132018`.

Portanto, o problema não era o telefone do paciente nem os cinco valores do
corpo. A incompatibilidade estava nos componentes extras de quick reply.

### 3.4. Correção Aplicada

Foi adicionada a configuração:

```env
WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT=0
```

Com o template atual, o sistema envia:

- um componente `BODY`;
- exatamente cinco parâmetros;
- nenhum botão.

O suporte aos botões foi mantido para um futuro template aprovado:

```env
WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT=2
```

O valor `2` somente deve ser utilizado quando o template aprovado realmente
possuir os botões:

1. `Confirmar Consulta`;
2. `Cancelar Consulta`.

### 3.5. Modo dos Parâmetros

O sistema suporta:

- `standard`: envia os cinco parâmetros posicionais;
- `message`: envia uma única mensagem renderizada.

Também foi mantida compatibilidade com o valor antigo digitado como `standart`,
mas a documentação e o `render.yaml` utilizam o valor correto `standard`.

Valores desconhecidos agora geram um erro de configuração explícito.

### 3.6. Mensagens de Erro da Meta

O tratamento de erros passou a incluir o campo de detalhes retornado em
`error_data.details`.

Isso permite identificar com mais precisão situações como:

- quantidade incorreta de parâmetros;
- botão inexistente;
- componente incompatível;
- divergência entre o payload e a versão aprovada do template.

### 3.7. Verificador de Templates

O script abaixo foi aprimorado:

```bash
python -m backend.scripts.check_whatsapp_templates
```

Agora ele informa:

- nome do template;
- status;
- categoria;
- idioma;
- prévia do conteúdo;
- quantidade de parâmetros no corpo;
- quantidade de quick replies;
- comparação entre o template aprovado e a configuração da aplicação.

Na verificação realizada, os templates configurados estavam aprovados e o
template do paciente foi confirmado com cinco parâmetros e zero botões.

## 4. Qualidade de Código

Durante a implementação também foram corrigidos avisos de lint já existentes no
repositório:

- imports não utilizados;
- variáveis não utilizadas;
- f-strings sem interpolação;
- imports fora da ordem;
- imports múltiplos na mesma linha;
- organização do script de criação do usuário de testes.

Essas alterações não modificaram as regras funcionais desses arquivos.

## 5. Testes Realizados

### 5.1. Lint

Comando:

```bash
python -m ruff check backend tests
```

Resultado:

```text
All checks passed!
```

### 5.2. Testes Unitários

Após as melhorias de layout:

```text
12 testes executados com sucesso.
```

Após a correção do WhatsApp:

```text
16 testes executados com sucesso.
```

Foram incluídos testes para:

- template do paciente sem botões;
- template com dois botões;
- ordem dos payloads de confirmação e cancelamento;
- rejeição de modo de parâmetros inválido;
- inclusão dos detalhes de erro retornados pela Meta.

### 5.3. Compilação e Sintaxe

Foram executadas:

- compilação dos módulos Python com `compileall`;
- validação de sintaxe do JavaScript com `node --check`;
- verificação de espaços e conflitos com `git diff --check`.

Todos os comandos concluíram com sucesso.

### 5.4. Testes Visuais

As seguintes telas foram verificadas no navegador em desktop e celular:

- dashboard;
- pacientes;
- perfil.

Também foram testados:

- filtro de pacientes com pendências;
- paginação;
- troca das abas do perfil;
- presença do botão de teste do WhatsApp;
- agrupamento dos horários livres;
- comportamento responsivo.

### 5.5. Validação do Payload do WhatsApp

O payload corrigido foi inspecionado sem realizar envio real.

Resultado:

```text
BODY:
1. Ricardo
2. data da consulta
3. horário
4. clínica
5. médico

Botões enviados: nenhum
```

Essa estrutura corresponde ao template aprovado na Meta.

### 5.6. Limitação Encontrada no E2E Local

O conjunto completo de testes E2E autenticados não pôde ser concluído contra o
banco configurado no `.env` local porque a conexão existente apresentou erro de
codificação no `DATABASE_URL`.

Para não bloquear a validação da interface:

- os testes unitários foram executados normalmente;
- as telas foram validadas com respostas controladas;
- nenhum dado real foi alterado;
- nenhuma mensagem real de WhatsApp foi enviada durante os testes.

## 6. Arquivos Alterados

### 6.1. Configuração e Documentação

- `.env.example`
- `SITUACAO_WHATSAPP.md`
- `render.yaml`

### 6.2. Backend

- `backend/app/api/routes/email_test.py`
- `backend/app/api/routes/patients.py`
- `backend/app/api/routes/whatsapp_test.py`
- `backend/app/core/config.py`
- `backend/app/crud/patients.py`
- `backend/app/schemas/patient.py`
- `backend/app/services/email_templates.py`
- `backend/app/services/whatsapp.py`
- `backend/app/services/whatsapp_reminders.py`
- `backend/app/services/whatsapp_templates.py`
- `backend/app/utils/pdf.py`

### 6.3. Scripts

- `backend/scripts/check_reminders.py`
- `backend/scripts/check_whatsapp_templates.py`
- `backend/scripts/clear_test_reminders.py`
- `backend/scripts/create_user.py`
- `backend/scripts/gen_vapid.py`
- `backend/scripts/reset_password.py`
- `backend/scripts/seed_data.py`
- `backend/scripts/send_reminders.py`

### 6.4. Frontend

- `frontend/app.css`
- `frontend/app.js`

### 6.5. Testes

- `tests/test_whatsapp.py`
- `tests/e2e/create_test_user.py`
- `tests/e2e/specs/02-dashboard.spec.js`
- `tests/e2e/specs/04-pacientes.spec.js`
- `tests/e2e/specs/06-perfil.spec.js`

## 7. Commits Publicados

### Melhorias de layout

```text
6fbee94 Melhora layout do dashboard pacientes e perfil
```

### Correção do WhatsApp

```text
ea55fee Corrige parametros do template WhatsApp do paciente
```

Ambos foram enviados para:

```text
origin/codex/tema-medico-correto
```

## 8. Configuração Esperada no Render

Para o template atual:

```env
WHATSAPP_TEMPLATE_LANGUAGE=pt_BR
WHATSAPP_PATIENT_TEMPLATE_NAME=agenda_paciente_lembrete
WHATSAPP_PATIENT_TEMPLATE_PARAMETER_MODE=standard
WHATSAPP_PATIENT_TEMPLATE_QUICK_REPLY_COUNT=0
WHATSAPP_DOCTOR_TEMPLATE_NAME=agenda_medico_resumo_v2
```

As mesmas configurações do WhatsApp devem existir no Web Service e no Cron Job
responsável pelos lembretes automáticos.

## 9. Impacto no Sistema

As mudanças afetam:

- apresentação do dashboard;
- navegação e organização do perfil;
- busca e acompanhamento de pacientes;
- experiência em dispositivos móveis;
- instalação do PWA;
- montagem do payload do template de WhatsApp do paciente;
- diagnóstico de falhas da Cloud API.

Não foram removidas funcionalidades existentes. O envio do template do médico
permaneceu inalterado, e o suporte a confirmações por botão continua disponível
para quando um template compatível estiver aprovado.

## 10. Estado Final

- código organizado;
- componentes e funções reutilizados;
- sem duplicação relevante introduzida;
- lint aprovado;
- compilação aprovada;
- testes unitários aprovados;
- interface validada em desktop e celular;
- causa do erro `132018` identificada;
- payload do paciente corrigido;
- commits enviados ao repositório remoto.

## 11. Atualização de 20 de Junho de 2026

### 11.1. Teste de WhatsApp ocultado

O card `Teste de WhatsApp` e o botão `Enviar WhatsApp de teste` foram removidos
da aba de notificações do Perfil.

A rota técnica de teste foi preservada no backend para uma possível retomada
futura da integração, mas não existe mais uma ação visível na interface que
possa disparar mensagens de teste acidentalmente.

### 11.2. Confirmação do paciente por e-mail

Os e-mails enviados ao paciente agora possuem o botão:

```text
Confirmar presença por e-mail
```

O botão foi incluído em:

- confirmação enviada imediatamente após o agendamento;
- lembrete de consulta enviado antes do atendimento;
- e-mail gerado pelo teste de e-mail do Perfil.

Ao clicar, o aplicativo de e-mail do paciente é aberto com uma mensagem
pré-preenchida para o e-mail de contato do médico. A mensagem contém:

- nome do paciente;
- data da consulta;
- horário;
- nome da clínica;
- assunto de confirmação.

O destinatário utilizado é o campo `E-mail para lembretes` do Perfil. Quando
esse campo não estiver preenchido, o sistema utiliza o e-mail principal da
conta do médico.

O paciente precisa revisar e enviar a mensagem no aplicativo de e-mail. O
clique isolado não altera automaticamente o status da consulta no sistema.

### 11.3. Testes desta atualização

- lint completo aprovado;
- compilação Python aprovada;
- sintaxe JavaScript aprovada;
- 19 testes unitários aprovados;
- três novos testes para o botão de confirmação por e-mail;
- teste E2E atualizado para garantir que o teste do WhatsApp permaneça oculto;
- verificação visual do e-mail e da aba de notificações realizada no navegador.

### 11.4. Configurações do WhatsApp ocultadas

Além do card de teste, foram retirados do Perfil enquanto a integração estiver
pausada:

- card `Mensagens do WhatsApp`;
- editores das mensagens de lembrete, confirmação e cancelamento;
- controles de lembrete interativo de 24 e 2 horas;
- chamadas da tela para carregar ou salvar templates do WhatsApp;
- textos do Perfil que indicavam envio automático pelo WhatsApp.

O campo `WhatsApp / Telefone` passou a ser apresentado somente como `Telefone`.
As rotas e serviços do backend foram preservados para permitir uma reativação
futura sem perda da implementação existente.
