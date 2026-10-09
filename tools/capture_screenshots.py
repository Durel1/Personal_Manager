"""Capture the real Windows UI using only disposable demonstration data."""
import os
import sys
import tempfile
import time
from datetime import date,timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    if sys.platform != 'win32':
        raise SystemExit('Lancez cet outil dans une session Windows avec un bureau visible.')
    from PIL import ImageGrab
    from ui.application import PersonalManager
    from backend.auth import register_user
    from backend.management import save_record
    output = ROOT/'docs'/'images'
    output.mkdir(parents=True,exist_ok=True)
    previous = os.environ.get('PERSONAL_MANAGER_DB')
    app = None
    try:
        with tempfile.TemporaryDirectory(prefix='personalmanager-screens-') as directory:
            os.environ['PERSONAL_MANAGER_DB'] = str(Path(directory)/'demo.db')
            app = PersonalManager()
            app.geometry('1180x700+30+30')
            def wait():
                deadline = time.monotonic()+30
                while app.polls or app.search_timer is not None:
                    app.update()
                    if time.monotonic() > deadline:
                        raise RuntimeError('La préparation des captures a pris trop de temps.')
                    time.sleep(0.01)
                app.update()
            wait()
            identifier = register_user('Démo PersonalManager','CaptureDemo123!','demo@example.com','001234567','Homme')
            for name,city in (('Atelier Horizon','Douala'),('Studio Lumière','Yaoundé'),('Maison Émeraude','Bafoussam')):
                save_record('clients',dict(fullname=name,email='contact@example.com',phone='001234567',
                    city=city,sector='Services',gender='Femme',quater='Centre'),actor_id=identifier)
            today = date.today()
            for days in (-60,-30,0,2):
                save_record('events',dict(meet_with='Atelier Horizon',gender='Homme',phone='001234567',
                    place='Bureau',event_status='Non Effectué',reason_event='Suivi du projet',
                    eventdate=(today+timedelta(days=days)).isoformat(),hour_event='09:30'),actor_id=identifier)
            for reason,amount,status in (('Matériel','45000','Payée'),('Transport','12000','Payée'),('Prestation','80000','Non Payée')):
                save_record('finances',dict(reason=reason,amount=amount,date=(today-timedelta(days=10)).isoformat(),
                    due_date=(today-timedelta(days=1)).isoformat(),status=status,type='Décaissement'),actor_id=identifier)
            app.user = {'id':identifier,'fullname':'Démo PersonalManager'}
            app.show_shell()
            wait()
            for view,filename in (('home','dashboard'),('clients','clients'),('finances','finances')):
                app.navigate(view)
                wait()
                app.lift()
                app.update()
                until = time.monotonic()+0.35
                while time.monotonic() < until:
                    app.update()
                    time.sleep(0.01)
                x,y = app.winfo_rootx(),app.winfo_rooty()
                ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height())).save(output/(filename+'.png'))
            app.executor.shutdown(wait=True,cancel_futures=True)
            app.close()
            app = None
        readme = ROOT/'README.md'
        text = readme.read_text(encoding='utf-8')
        start,end = '<!-- screenshots:start -->','<!-- screenshots:end -->'
        left,rest = text.split(start,1)
        _,right = rest.split(end,1)
        gallery = '\nCaptures du vrai logiciel, avec des données de démonstration temporaires.\n\n'
        for title,name in (('Tableau de bord','dashboard'),('Clients','clients'),('Finances et alertes','finances')):
            gallery += f'![{title}](docs/images/{name}.png)\n\n'
        readme.write_text(left+start+gallery+end+right,encoding='utf-8')
        print('Trois captures créées dans docs/images et ajoutées au README.')
    finally:
        if app is not None:
            app.executor.shutdown(wait=True,cancel_futures=True)
            app.close()
        if previous is None:
            os.environ.pop('PERSONAL_MANAGER_DB',None)
        else:
            os.environ['PERSONAL_MANAGER_DB'] = previous

if __name__ == '__main__':
    main()
