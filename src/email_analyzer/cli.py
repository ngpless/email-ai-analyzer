"""CLI для быстрого ad-hoc-анализа.

Запуск: `python -m email_analyzer.cli analyze --subject "тема" --body "..."`
"""

from __future__ import annotations

import argparse
import json
import sys

from email_analyzer.backend.services.analysis import AnalysisService


def _cmd_analyze(args: argparse.Namespace) -> int:
    service = AnalysisService()
    result = service.analyze(
        subject=args.subject,
        body=args.body,
        sender=args.sender or "",
    )
    data = {
        "category": result.category.value,
        "confidence": result.confidence,
        "is_spam": result.is_spam,
        "is_phishing": result.is_phishing,
        "summary": result.summary,
        "entities": result.entities,
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def _cmd_version(_args: argparse.Namespace) -> int:
    from email_analyzer import __version__
    print(__version__)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="email-analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze_p = sub.add_parser("analyze", help="проанализировать одно письмо")
    analyze_p.add_argument("--subject", default="", help="тема письма")
    analyze_p.add_argument("--body", default="", help="тело письма")
    analyze_p.add_argument("--sender", default="", help="адрес отправителя")
    analyze_p.set_defaults(func=_cmd_analyze)

    version_p = sub.add_parser("version", help="показать версию")
    version_p.set_defaults(func=_cmd_version)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
