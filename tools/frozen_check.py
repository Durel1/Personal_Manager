"""Exercise bundled imports, crypto, SQLite, charts and report assets without Tk windows."""
import json
import os
import tempfile
from pathlib import Path

def run_self_test(destination):
    result = {'ok':False,'checks':[]}
    previous = os.environ.get('PERSONAL_MANAGER_DB')
    try:
        with tempfile.TemporaryDirectory(prefix='personalmanager-check-') as directory:
            os.environ['PERSONAL_MANAGER_DB'] = str(Path(directory)/'check.db')
            from ui.application import PersonalManager
            from backend.migrations import migrate_application
            from backend.auth import register_user,authenticate_user
            from backend.management import save_record
            from backend.reporting import export_report
            from backend.statistics import statistics_snapshot
            from ui.charts import event_figure,spending_figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            from openpyxl import load_workbook
            result['checks'].append('imports')
            migrate_application()
            identifier = register_user('BuildCheck','BuildCheck123!','build@example.invalid','00123','Homme')
            assert authenticate_user('BuildCheck','BuildCheck123!')['id'] == identifier
            result['checks'].append('sqlite_bcrypt')
            save_record('finances',dict(reason='Vérification',amount='1000',date='2026-10-09',
                status='Payée',type='Décaissement',due_date=''),actor_id=identifier)
            data = statistics_snapshot(actor_id=identifier)
            for figure in (event_figure(data['months'],True),spending_figure(data['spending'],True)):
                FigureCanvasAgg(figure).draw()
                figure.clear()
            result['checks'].append('matplotlib')
            for suffix in ('.xlsx','.pdf'):
                path = Path(directory)/('report'+suffix)
                assert export_report('finances',path,identifier) == 1
                assert path.stat().st_size > 100
                if suffix == '.xlsx':
                    book = load_workbook(path)
                    try:
                        assert book.active['B5'].value == 'Vérification'
                    finally:
                        book.close()
            result['checks'].append('excel_pdf_fonts')
            result['ok'] = True
    except Exception as error:
        result['error_type'] = type(error).__name__
    finally:
        if previous is None:
            os.environ.pop('PERSONAL_MANAGER_DB',None)
        else:
            os.environ['PERSONAL_MANAGER_DB'] = previous
    Path(destination).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if result['ok'] else 1
