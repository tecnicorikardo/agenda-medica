"""Templates HTML para e-mails da Agenda Médica."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Sao_Paulo")

STATUS_MAP = {
    "agendada": "Agendada",
    "confirmada": "Confirmada",
    "concluida": "Concluída",
    "cancelada": "Cancelada",
    "faltou": "Faltou",
}

# Variáveis disponíveis nas mensagens personalizadas
MSG_VARS_PACIENTE = "{nome}, {primeiro_nome}, {data}, {hora}, {clinica}, {medico}"
MSG_VARS_MEDICO   = "{paciente}, {data}, {hora}, {clinica}, {total_dia}"

MSG_PADRAO_PACIENTE = (
    "Olá, {primeiro_nome}! 😊\n\n"
    "Lembramos que você tem uma consulta marcada para {data} às {hora}.\n\n"
    "Confirme sua presença ou entre em contato com antecedência caso precise remarcar.\n\n"
    "Até lá! 🏥"
)

MSG_PADRAO_MEDICO = (
    "Olá! 👋\n\n"
    "Lembrete automático: você tem uma consulta com {paciente} em {data} às {hora}.\n\n"
    "Tenha um ótimo atendimento! 🩺"
)

_BASE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{subject}</title>
<style>
  body{{margin:0;padding:0;background:#f0f4ff;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#1a2540}}
  .wrap{{max-width:600px;margin:32px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(26,58,107,.12)}}
  .header{{background:linear-gradient(135deg,#1a3a6b 0%,#2563eb 100%);padding:32px 32px 24px;text-align:center}}
  .header h1{{margin:0;color:#fff;font-size:22px;font-weight:800;letter-spacing:.3px}}
  .header p{{margin:6px 0 0;color:rgba(255,255,255,.75);font-size:13px}}
  .body{{padding:28px 32px}}
  .greeting{{font-size:18px;font-weight:700;margin-bottom:6px}}
  .intro{{color:#4b5a7a;font-size:14px;margin-bottom:24px;line-height:1.6;white-space:pre-line}}
  .card{{background:#f5f8ff;border:1px solid #dce8ff;border-radius:12px;padding:20px 24px;margin-bottom:20px}}
  .card-row{{display:flex;gap:8px;margin-bottom:10px;align-items:flex-start}}
  .card-row:last-child{{margin-bottom:0}}
  .card-label{{font-size:11px;font-weight:700;color:#6b7fa8;text-transform:uppercase;letter-spacing:.5px;min-width:90px;padding-top:2px}}
  .card-value{{font-size:14px;color:#1a2540;font-weight:600;flex:1}}
  .badge{{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;background:#dce8ff;color:#1a3a6b}}
  .badge-ok{{background:#d1fae5;color:#065f46}}
  .section-title{{font-size:14px;font-weight:700;color:#1a3a6b;margin:24px 0 12px;border-bottom:2px solid #dce8ff;padding-bottom:6px}}
  table.hist{{width:100%;border-collapse:collapse;font-size:13px}}
  table.hist th{{background:#1a3a6b;color:#fff;padding:8px 10px;text-align:left;font-weight:600;font-size:12px}}
  table.hist td{{padding:8px 10px;border-bottom:1px solid #e8eeff;vertical-align:top}}
  table.hist tr:last-child td{{border-bottom:none}}
  table.hist tr:nth-child(even) td{{background:#f5f8ff}}
  .obs{{color:#6b7fa8;font-size:12px}}
  .agenda-item{{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #e8eeff}}
  .agenda-item:last-child{{border-bottom:none}}
  .agenda-time{{font-size:20px;font-weight:900;color:#1a3a6b;min-width:52px}}
  .agenda-info{{flex:1}}
  .agenda-name{{font-weight:700;font-size:14px}}
  .agenda-sub{{font-size:12px;color:#6b7fa8;margin-top:2px}}
  .footer{{background:#f5f8ff;border-top:1px solid #dce8ff;padding:18px 32px;text-align:center;font-size:12px;color:#8a9bbf}}
  @media(max-width:600px){{
    .body{{padding:20px 16px}}
    .header{{padding:24px 16px 18px}}
    .card{{padding:14px 16px}}
  }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>🏥 {clinic_name}</h1>
    <p>{doctor_line}</p>
  </div>
  <div class="body">
    {content}
  </div>
  <div class="footer">
    Este e-mail foi enviado automaticamente pela <strong>Agenda Médica</strong>.<br/>
    Em caso de dúvidas, entre em contato com o consultório.
  </div>
</div>
</body>
</html>"""


def _fmt_dt(dt: datetime) -> str:
    return dt.astimezone(TZ).strftime("%d/%m/%Y %H:%M")


def _fmt_date_br(dt: datetime) -> str:
    return dt.astimezone(TZ).strftime("%d/%m/%Y")


def _fmt_hora(dt: datetime) -> str:
    return dt.astimezone(TZ).strftime("%H:%M")


def _fmt_date(d) -> str:
    if not d:
        return "—"
    if hasattr(d, "strftime"):
        return d.strftime("%d/%m/%Y")
    return str(d)


def _render_msg(template: str | None, default: str, **kwargs) -> str:
    """Renderiza mensagem personalizada substituindo variáveis."""
    tpl = (template or default).strip()
    try:
        return tpl.format(**kwargs)
    except (KeyError, ValueError):
        return default.format(**kwargs)


# ─── E-mail para o PACIENTE ───────────────────────────────────────────────────

def lembrete_paciente_html(
    *,
    paciente_nome: str,
    inicio: datetime,
    fim: datetime,
    dias_antes: int,
    clinic_name: str,
    doctor_name: str | None,
    consultas_historico: list | None = None,
    observacoes_consulta: str | None = None,
    msg_personalizada: str | None = None,
) -> tuple[str, str]:
    """Retorna (subject, html) do lembrete para o paciente."""
    primeiro_nome = paciente_nome.split()[0]
    data_str = _fmt_date_br(inicio)
    hora_str = _fmt_hora(inicio)
    hora_fim = _fmt_hora(fim)
    aviso = "amanhã" if dias_antes == 1 else f"em {dias_antes} dias ({data_str})"
    subject = f"Lembrete: sua consulta é {aviso} — {clinic_name}"
    doctor_line = f"Dr(a). {doctor_name}" if doctor_name else clinic_name

    # Mensagem personalizada
    intro_text = _render_msg(
        msg_personalizada,
        MSG_PADRAO_PACIENTE,
        nome=paciente_nome,
        primeiro_nome=primeiro_nome,
        data=data_str,
        hora=hora_str,
        clinica=clinic_name,
        medico=doctor_name or clinic_name,
    )

    # Card da consulta
    obs_row = ""
    if observacoes_consulta:
        obs_row = f"""
        <div class="card-row">
          <span class="card-label">Observações</span>
          <span class="card-value obs">{observacoes_consulta}</span>
        </div>"""

    consulta_card = f"""
    <div class="card">
      <div class="card-row">
        <span class="card-label">Data</span>
        <span class="card-value">{data_str}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Horário</span>
        <span class="card-value">{hora_str} – {hora_fim}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Local</span>
        <span class="card-value">{clinic_name}</span>
      </div>{obs_row}
    </div>"""

    # Histórico de consultas concluídas
    hist_section = ""
    if consultas_historico:
        rows = ""
        for c in consultas_historico[:15]:
            status_label = STATUS_MAP.get(c.status, c.status)
            obs = c.observacoes or "—"
            rows += f"""
            <tr>
              <td>{_fmt_dt(c.inicio)}</td>
              <td><span class="badge">{status_label}</span></td>
              <td class="obs">{obs}</td>
            </tr>"""
        hist_section = f"""
    <p class="section-title">📋 Seu histórico de consultas</p>
    <table class="hist">
      <thead><tr><th>Data / Hora</th><th>Status</th><th>Observações</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>"""

    content = f"""
    <p class="intro">{intro_text}</p>
    {consulta_card}
    {hist_section}
    """

    html = _BASE.format(
        subject=subject,
        clinic_name=clinic_name,
        doctor_line=doctor_line,
        content=content,
    )
    return subject, html


# ─── E-mail para o MÉDICO ─────────────────────────────────────────────────────

def lembrete_medico_html(
    *,
    doctor_name: str | None,
    clinic_name: str,
    data_consultas: datetime,
    consultas_do_dia: list,
    paciente_foco_nome: str,
    inicio_foco: datetime,
    total_dia: int,
    msg_personalizada: str | None = None,
) -> tuple[str, str]:
    """Retorna (subject, html) do resumo diário para o médico."""
    data_str = _fmt_date_br(data_consultas)
    hora_str = _fmt_hora(inicio_foco)
    nome_medico = doctor_name or "Médico(a)"
    subject = f"📅 Agenda do dia {data_str} — {total_dia} consulta(s) — {clinic_name}"
    doctor_line = f"Dr(a). {doctor_name}" if doctor_name else clinic_name

    intro_text = _render_msg(
        msg_personalizada,
        MSG_PADRAO_MEDICO,
        paciente=paciente_foco_nome,
        data=data_str,
        hora=hora_str,
        clinica=clinic_name,
        total_dia=total_dia,
    )

    # Lista de consultas do dia
    agenda_items = ""
    for c in consultas_do_dia:
        paciente = getattr(c, "_paciente_nome", "—")
        telefone = getattr(c, "_paciente_tel", "")
        obs = c.observacoes or ""
        hora_c = _fmt_hora(c.inicio)
        hora_f = _fmt_hora(c.fim)
        status_label = STATUS_MAP.get(c.status, c.status)
        agenda_items += f"""
        <div class="agenda-item">
          <div class="agenda-time">{hora_c}</div>
          <div class="agenda-info">
            <div class="agenda-name">{paciente}</div>
            <div class="agenda-sub">{hora_c}–{hora_f} • {telefone}{' • ' + obs if obs else ''}</div>
          </div>
          <span class="badge">{status_label}</span>
        </div>"""

    content = f"""
    <p class="intro">{intro_text}</p>
    <div class="card">
      <div class="card-row">
        <span class="card-label">Data</span>
        <span class="card-value">{data_str}</span>
      </div>
      <div class="card-row">
        <span class="card-label">Total</span>
        <span class="card-value"><span class="badge badge-ok">{total_dia} consulta(s)</span></span>
      </div>
    </div>
    <p class="section-title">🗓️ Agenda completa do dia</p>
    <div class="card" style="padding:8px 16px">
      {agenda_items}
    </div>
    """

    html = _BASE.format(
        subject=subject,
        clinic_name=clinic_name,
        doctor_line=doctor_line,
        content=content,
    )
    return subject, html
