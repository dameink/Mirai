"""Operator-only local CLI. Never expose database access or output publicly.

python -m core.review_reports list
python -m core.review_reports show MESSAGE_UUID
python -m core.review_reports resolve MESSAGE_UUID
"""
import argparse
import json
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from db.database import SessionLocal
from core.reports import ContentReport

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['list', 'show', 'resolve'])
    parser.add_argument('message_id', nargs='?', type=UUID)
    args = parser.parse_args()
    if args.action != 'list' and args.message_id is None:
        parser.error('message_id is required')
    with SessionLocal() as db:
        if args.action == 'list':
            rows = db.scalars(select(ContentReport).where(ContentReport.reviewed_at.is_(None)).order_by(ContentReport.created_at).limit(100)).all()
            print(json.dumps([{'message_id': r.message_id, 'reason': r.reason, 'created_at': r.created_at.isoformat()} for r in rows]))
        else:
            report = db.get(ContentReport, str(args.message_id))
            if report is None:
                raise SystemExit('Report not found')
            if args.action == 'show':
                print(json.dumps({'reason': report.reason, 'content': report.content}, ensure_ascii=True))
            else:
                report.reviewed_at = datetime.now(timezone.utc)
                db.commit()
                print('Marked reviewed')

if __name__ == '__main__':
    main()
