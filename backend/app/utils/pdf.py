"""Geração de PDF do histórico do paciente usando reportlab."""
from __future__ import annotations

import io
from datetime import datetime
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

TZ = ZoneInfo("America/Sao_Paulo")

STATUS_MAP = {
    "agendada": "Agendada",
    "confirmada": "Confirmada",
    "concluida": "Concluída",
    "cancelada": "Cancelada",
    "faltou": "Faltou",
}


def _fmt_dt(dt: datetime) -> str:
    local = dt.astimezone(TZ)
    return local.strftime("%d/%m/%Y %H:%M")


def _fmt_date(d) -> str:
    if not d:
        return "—"
    if hasattr(d, "strftime"):
        return d.strftime("%d/%m/%Y")
    return str(d)


def gerar_historico_pdf(paciente, consultas: list) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Histórico - {paciente.nome_completo}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#1a3a6b"),
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "sub",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
    )
    label_style = ParagraphStyle(
        "label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#888888"),
    )

    story = []

    # Cabeçalho
    story.append(Paragraph("Agenda Médica", label_style))
    story.append(Paragraph(f"Histórico do Paciente", title_style))
    story.append(Spacer(1, 0.3 * cm))

    # Dados do paciente
    dados = [
        ["Nome:", paciente.nome_completo],
        ["Telefone:", paciente.telefone or "—"],
        ["E-mail:", paciente.email or "—"],
        ["Nascimento:", _fmt_date(paciente.data_nascimento)],
        ["Observações:", paciente.observacoes or "—"],
    ]
    t = Table(dados, colWidths=[3.5 * cm, 13 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a3a6b")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    # Linha divisória
    story.append(Table(
        [[""]],
        colWidths=[16.5 * cm],
        style=TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#ccddff")),
        ]),
    ))
    story.append(Spacer(1, 0.4 * cm))

    # Tabela de consultas
    story.append(Paragraph(f"Consultas ({len(consultas)} registros)", ParagraphStyle(
        "sec", parent=styles["Heading2"], fontSize=11,
        textColor=colors.HexColor("#1a3a6b"), spaceAfter=6,
    )))

    if not consultas:
        story.append(Paragraph("Nenhuma consulta registrada.", sub_style))
    else:
        header = ["Data / Hora", "Status", "Observações"]
        rows = [header]
        for c in consultas:
            rows.append([
                _fmt_dt(c.inicio),
                STATUS_MAP.get(c.status, c.status),
                c.observacoes or "—",
            ])

        tbl = Table(rows, colWidths=[4.5 * cm, 3 * cm, 9 * cm])
        tbl.setStyle(TableStyle([
            # Cabeçalho
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a6b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Corpo
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f5ff")]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#ccddff")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)

    story.append(Spacer(1, 0.8 * cm))
    now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"Gerado em {now}", label_style))

    doc.build(story)
    return buf.getvalue()
