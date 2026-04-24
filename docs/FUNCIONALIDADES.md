# Agenda Médica — Guia Completo de Funcionalidades

> Documento gerado automaticamente a partir do código-fonte.  
> Versão: Abril/2026

---

## Índice

1. [Acesso e Segurança](#1-acesso-e-segurança)
2. [Perfil do Médico](#2-perfil-do-médico)
3. [Dashboard](#3-dashboard)
4. [Agenda e Consultas](#4-agenda-e-consultas)
5. [Pacientes](#5-pacientes)
6. [Lembretes e Notificações](#6-lembretes-e-notificações)
7. [Exportação e Importação](#7-exportação-e-importação)
8. [Interface e Experiência Mobile](#8-interface-e-experiência-mobile)
9. [PWA — App Instalável](#9-pwa--app-instalável)
10. [Resumo das Rotas da API](#10-resumo-das-rotas-da-api)

---

## 1. Acesso e Segurança

### Login com e-mail e senha
O médico acessa o sistema com e-mail e senha. A sessão é mantida via cookie HTTP-only seguro. Há opção de "Lembrar e-mail" para agilizar o próximo acesso.

### Cadastro de conta
Novos usuários podem criar conta diretamente na tela de login. O sistema valida e-mail duplicado e exige senha com mínimo de 6 caracteres.

### Login biométrico (Face ID / Impressão digital)
Após o primeiro login, o sistema oferece ativar autenticação biométrica via WebAuthn. Nos acessos seguintes, basta usar o sensor do dispositivo — sem digitar senha.

### Recuperação de senha
Ao clicar em "Esqueci minha senha", o sistema envia uma senha temporária por e-mail. O médico pode alterá-la depois no perfil.

### Alteração de senha
Disponível na página de Perfil. Exige confirmação da senha atual e digitação da nova senha duas vezes.

### Logout
Encerra a sessão e invalida o cookie de autenticação.

---

## 2. Perfil do Médico

### Dados profissionais
O médico pode preencher e atualizar:
- Nome completo
- CRM
- Especialidade
- Nome da clínica
- Telefone de contato
- E-mail para lembretes (pode ser diferente do e-mail de login)

Essas informações aparecem no cabeçalho do sistema e nos e-mails enviados aos pacientes.

### Foto de perfil / logo da clínica
Upload de imagem (JPEG, PNG, WebP ou GIF, máx. 2 MB). A foto aparece no cabeçalho e na tela de boas-vindas. Pode ser removida a qualquer momento.

### Tema claro / escuro
Alternância entre tema escuro (padrão) e claro. A preferência é salva no dispositivo.

---

## 3. Dashboard

A tela inicial apresenta um resumo do dia atual assim que o médico faz login.

### Saudação dinâmica
"Bom dia", "Boa tarde" ou "Boa noite" conforme o horário, com o primeiro nome do médico.

### KPIs do dia
Quatro indicadores em destaque:
- **Consultas hoje** — total de consultas agendadas para o dia
- **Canceladas** — total de cancelamentos no período
- **Concluídas** — total de atendimentos realizados
- **Pacientes cadastrados** — total geral na base

### Próximo paciente
Exibe nome, horário e status da próxima consulta do dia. Se não houver mais consultas, informa isso claramente.

### Horários livres
Lista os próximos slots disponíveis do dia (intervalos de 30 min, entre 08:00 e 18:00). Clicar em um horário abre diretamente o modal de agendamento com aquele horário pré-preenchido.

### Acesso rápido
Dois cards grandes na tela inicial levam diretamente para **Agenda** e **Pacientes** com um toque.

---

## 4. Agenda e Consultas

### Visualizar consultas do dia
Lista todas as consultas de um dia específico. O dia padrão é o dia atual. Cada card mostra:
- Horário de início e fim
- Nome e telefone do paciente
- Status (com cor)
- Botões de ação rápida

### Filtros de período
Atalhos rápidos na barra da agenda:
- **Hoje** — consultas do dia atual
- **Amanhã** — consultas do dia seguinte
- **7 dias** — próximos 7 dias
- **Este mês** — mês corrente

### Busca em tempo real
Campo de busca filtra a lista instantaneamente por nome do paciente, telefone ou status.

### Criar consulta
Botão **+ Agendar** abre o modal de agendamento com:
- Busca de paciente por nome ou telefone (a partir de 3 caracteres)
- Seletor de data (não permite datas passadas)
- Horário de início e fim lado a lado
- Validação automática: fim não pode ser anterior ao início
- Validação de horário passado: se a data for hoje, o horário de início não pode ser anterior à hora atual
- Campo de observações

### Editar consulta
Clique em ✏️ no card abre o modal de edição com todos os campos preenchidos. Permite alterar data, horários, status e observações. Ao editar, datas passadas são permitidas (a consulta já existe).

### Alterar status com 1 toque
O badge de status em cada card é clicável. Ao tocar, abre um menu rápido com as opções:
- ✅ Confirmar
- 📅 Agendado
- ✔️ Atendimento realizado
- 🚫 Faltou
- ❌ Cancelar

O status é atualizado imediatamente, sem recarregar a tela.

### Cancelamento com motivo
Ao cancelar, o sistema pede confirmação e depois oferece registrar o motivo (opcional). Motivos pré-definidos:
- Paciente desistiu
- Sem resposta
- Remarcado
- Problema pessoal
- Outro (campo livre)

### Ações rápidas no card
Cada card de consulta tem botões de ação direta:
- **✏️ Editar** — abre o modal de edição
- **📞 Ligar** — abre o discador do celular com o número do paciente
- **💬 WhatsApp** — abre conversa no WhatsApp com o paciente

Os botões de ligar e WhatsApp só aparecem se o paciente tiver telefone cadastrado.

### Swipe (gesto de deslize)
No celular, é possível deslizar o card:
- **→ Direita** — confirma a consulta instantaneamente
- **← Esquerda** — abre o fluxo de cancelamento

### Horários de encaixe
A barra de encaixe mostra os slots livres do dia. Quando a aba selecionada é **Hoje**, apenas horários futuros são exibidos — horários que já passaram são ocultados automaticamente. Se todos os horários do dia já passaram, exibe a mensagem "Não há mais horários disponíveis hoje".

---

## 5. Pacientes

### Listar pacientes
Exibe todos os pacientes cadastrados com nome, telefone e avatar com iniciais. Busca em tempo real por nome ou telefone.

### Cadastrar paciente
Formulário com os campos:
- Nome completo (obrigatório)
- Telefone (obrigatório)
- E-mail
- Data de nascimento
- Observações

### Editar dados do paciente
Todos os campos podem ser atualizados a qualquer momento.

### Excluir paciente
Remove o paciente após confirmação. A exclusão é permanente.

### Histórico do paciente
Página dedicada com todas as consultas do paciente (últimas 50), mostrando data, horário, status e observações.

### Agendar retorno
Diretamente da página de histórico, o médico pode agendar uma nova consulta para o mesmo paciente com um toque.

### Ações rápidas na lista
Cada paciente na lista tem botões para:
- ✏️ Editar dados
- 📞 Ligar
- 💬 WhatsApp
- ⋯ Menu com mais opções (editar, excluir, exportar PDF)

---

## 6. Lembretes e Notificações

### Lembretes por e-mail para o paciente
O sistema envia automaticamente um e-mail de lembrete para o paciente antes da consulta. O médico configura:
- Ativar ou desativar
- Quantos dias antes enviar (1 dia, 2 dias ou ambos)
- Texto personalizado da mensagem

Variáveis disponíveis na mensagem:
`{primeiro_nome}`, `{nome}`, `{data}`, `{hora}`, `{clinica}`, `{medico}`

O e-mail também inclui as últimas 10 consultas concluídas do paciente como histórico.

### Lembretes por e-mail para o médico
Junto com o lembrete do paciente, o médico recebe um resumo com o total de consultas do dia e o paciente em destaque. A mensagem também é personalizável.

Variáveis disponíveis: `{paciente}`, `{data}`, `{hora}`, `{total_dia}`, `{clinica}`

### Lembretes via WhatsApp
Script que gera links `wa.me` com mensagem pré-formatada para envio manual. O médico executa o script e os links abrem no navegador para envio com um clique.

### Notificações push (Web Push)
O sistema suporta notificações push no navegador e em dispositivos com o app instalado (PWA). O médico pode:
- Ativar notificações push no perfil
- Testar o envio com um botão dedicado
- Receber notificações mesmo com o app fechado

### Envio de e-mail
O sistema suporta dois provedores:
- **Resend API** — recomendado para produção em cloud
- **SMTP direto** — para uso local ou servidores próprios

---

## 7. Exportação e Importação

### Exportar pacientes para Excel
Gera um arquivo `.xlsx` com todos os pacientes cadastrados. A planilha tem cabeçalho colorido, linhas alternadas e colunas ajustadas automaticamente.

### Importar pacientes de Excel
Upload de planilha para criar ou atualizar pacientes em lote. O sistema:
- Identifica pacientes pelo telefone (upsert)
- Ignora linhas vazias
- Aceita múltiplos formatos de data
- Exibe relatório com quantidade de criados, atualizados e ignorados

### Exportar histórico do paciente em PDF
Gera um PDF profissional com os dados do paciente e tabela completa de consultas. Inclui data de geração e formatação com cores por status.

---

## 8. Interface e Experiência Mobile

O sistema foi projetado com foco em uso no celular durante o atendimento.

### Layout responsivo
Todos os elementos se adaptam a telas pequenas. Modais abrem como bottom-sheets (folha que sobe da parte inferior), facilitando o alcance com o polegar.

### Fontes e inputs grandes
Todos os campos de texto, seletores de data e horário têm fonte mínima de 16px e altura mínima de 48px, evitando zoom automático no iOS e facilitando o toque.

### FAB (botão flutuante)
Botão circular fixo no canto inferior direito para acesso rápido ao Dashboard, visível em todas as telas.

### Seletor de data
Calendário customizado que abre como bottom-sheet no mobile. Permite navegar por mês e ano com toque. Datas passadas ficam desabilitadas nos formulários de novo agendamento.

### Seletor de horário
Dois campos de horário (início e fim) lado a lado, com fonte grande e fácil de tocar. Ajuste automático quando o horário de fim é inválido.

### Tela de boas-vindas
Animação de entrada após o login com avatar, nome e nome da clínica. Dura 2,8 segundos antes de entrar no dashboard.

---

## 9. PWA — App Instalável

O sistema funciona como um Progressive Web App, o que significa que pode ser instalado na tela inicial do celular como um aplicativo nativo.

### Instalação
No Android e iOS, o navegador oferece a opção "Adicionar à tela inicial". Após instalado, o app abre em tela cheia sem barra do navegador.

### Funcionamento offline
O Service Worker faz cache dos arquivos principais, permitindo que o app carregue mesmo sem conexão (os dados da agenda ainda precisam de internet).

### Ícones
Ícones em múltiplos tamanhos (72, 96, 128, 144, 152, 192, 384 e 512px) para compatibilidade com todos os dispositivos.

### Notificações push em background
Com o app instalado, as notificações push chegam mesmo com o app fechado, como em qualquer aplicativo nativo.

---

## 10. Resumo das Rotas da API

### Autenticação
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/login` | Login |
| POST | `/auth/logout` | Logout |
| POST | `/auth/cadastro` | Criar conta |
| GET | `/auth/me` | Dados do usuário logado |
| POST | `/auth/esqueci-senha` | Enviar senha temporária |
| POST | `/auth/alterar-senha` | Alterar senha |
| PUT | `/auth/perfil` | Atualizar perfil |
| POST | `/auth/perfil/avatar` | Upload de foto |
| DELETE | `/auth/perfil/avatar` | Remover foto |

### Consultas
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/appointments?day=YYYY-MM-DD` | Consultas do dia |
| GET | `/appointments/range?start=...&end=...` | Consultas por período |
| GET | `/appointments/upcoming` | Próximas consultas |
| POST | `/appointments` | Criar consulta |
| PUT | `/appointments/{id}` | Editar consulta |
| POST | `/appointments/{id}/cancel` | Cancelar consulta |

### Pacientes
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/patients` | Listar pacientes |
| POST | `/patients` | Criar paciente |
| GET | `/patients/{id}` | Detalhes do paciente |
| PUT | `/patients/{id}` | Editar paciente |
| DELETE | `/patients/{id}` | Excluir paciente |
| GET | `/patients/{id}/history` | Histórico de consultas |
| GET | `/patients/{id}/history/pdf` | PDF do histórico |
| GET | `/patients/export/excel` | Exportar para Excel |
| POST | `/patients/import/excel` | Importar de Excel |

### Dashboard
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/dashboard?dia=YYYY-MM-DD` | Dados do dashboard |

### Push Notifications
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/push/vapid-public-key` | Chave pública VAPID |
| POST | `/push/subscribe` | Registrar dispositivo |
| POST | `/push/unsubscribe` | Desregistrar dispositivo |
| POST | `/push/test` | Enviar notificação de teste |

---

## Status das Consultas

| Status | Cor | Significado |
|--------|-----|-------------|
| Agendada | Azul | Consulta marcada, aguardando confirmação |
| Confirmada | Verde | Paciente confirmou presença |
| Concluída | Roxo | Atendimento realizado |
| Cancelada | Vermelho | Consulta cancelada |
| Faltou | Laranja | Paciente não compareceu |

---

*Agenda Médica — Sistema de gestão de consultório médico*
