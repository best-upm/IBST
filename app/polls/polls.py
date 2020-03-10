from flask import render_template, flash, redirect, url_for, jsonify
from app import app, db
from flask_login import login_required
from app.functions import roles_required, role_necessary
from app.polls import bp
from app.polls.PollForms import NewPollForm
from app.models import Poll, PollOption
from datetime import date, datetime
from itertools import permutations

"""
Hay tres tipos de votaciones Si/No/Blanco G:2/3 Votos, Si/No/Blanco Simple, Instant Runoff Voting IRV
"""

@bp.route('/newpoll', methods=['GET', 'POST'])
@login_required
@role_necessary(rol=['Admin', 'Full', 'Baby'])  #Se debe cambiar a los que realmente tengan permisos
def newPoll():
    title = 'Crear nueva votación'
    poll = Poll(start_date=datetime.utcnow())
    form = NewPollForm(obj=poll)
    if(form.validate_on_submit()):
        form.populate_obj(poll)
        options = list(form.Opciones.data.split("; "))
        permutaciones = list(permutations(options))
        """for option in options:
            opcion = PollOption(option_name=option)
            poll.options.append(opcion)"""
        for permutacion in permutaciones:
            opcion = PollOption(option_name=permutacion)
            poll.options.append(opcion)
        db.session.add(poll)
        db.session.commit()
		#print(options, flush=True)
        return render_template('ShowNewPoll.html', options=options)
    return render_template('Newpoll.html', title=title, form=form)
@bp.route('/')
@bp.route('polls')
@role_necessary(rol=['Admin', 'Full', 'Baby'])
def Polls():
    title = 'Tabla de Votaciones'
    data_OpenPolls = Poll.query.all()
    return render_template('Show_Polls.html', data_OpenPolls=data_OpenPolls, title=title)

@bp.route('/votepoll')
@bp.route('/votepoll/<int:id>', methods=['GET', 'POST'])
@role_necessary(rol=['Admin', 'Full', 'Baby'])
def VotePoll(id=None):
    if id == None:
        title = 'Pagina de votaciones'
        return render_template('GoToPoll.html', title=title)
    print(Poll.query.get_or_404(id).to_dict(), flush=True)
    return jsonify(Poll.query.get_or_404(id).to_dict())
    #return 'Opcion para Votar'
