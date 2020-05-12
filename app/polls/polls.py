from flask import render_template, flash, redirect, url_for, jsonify, request
from app import app, db
from flask_login import login_required, current_user
from app.functions import roles_required, role_necessary
from app.polls import bp
from app.polls.PollForms import NewPollForm
from app.models import Poll, PollOption, User
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
        try:
            for option in options:
                if("$user: " in option):
                    #Supongo que lo adecuado seria que devolviese "user_id: x" para clasificar
                    analized_option=option.split(" ", 1)[1];
                    user = User.query.filter_by(Usuario=analized_option).first_or_404()
                    if(user is not None):
                        option="user_id: "+str(user.id) #
                elif("$date: " in option):
                        #Y aqui un elemento "date" Aunque, quizas habria que hacer el template_html mas dinamico
                    analized_option=option.split(" ", 1)[1];
                opcion = PollOption(option_name=option)
                poll.options.append(opcion)
                db.session.add(poll)
                db.session.commit()
		            #print(options, flush=True)
                return render_template('ShowNewPoll.html', options=options)
        except:
            flash('Error!!! Ha sucedido un error, revisa que todos los datos han sido introducidos correctamente')
            return render_template('Newpoll.html', title=title, form=form)
    return render_template('Newpoll.html', title=title, form=form)
@bp.route('/')
@bp.route('polls')
@login_required
@role_necessary(rol=['Admin', 'Full', 'Baby'])
def Polls():
    title = 'Tabla de Votaciones'
    data_OpenPolls = Poll.query.all()
    return render_template('Show_Polls.html', data_OpenPolls=data_OpenPolls, title=title)

@bp.route('/votepoll')
@bp.route('/votepoll/<int:id>', methods=['GET', 'POST'])
@login_required
@role_necessary(rol=['Admin', 'Full', 'Baby'])
def VotePoll(id=None):
    if id == None:
        title = 'Pagina de votaciones'
        return render_template('GoToPoll.html', title=title)
    poll=Poll.query.get_or_404(id);
    return render_template('poll.html', poll=poll, User=User)

@bp.route('/vote', methods=['PUT'])
@bp.route('/vote/<int:id>', methods=['PUT'])
@login_required
def vote(id=None):
    #This function will get the votes in order of preference and
    data = request.get_json() or {}
    user=User.query.get(current_user.id)
    #El primer paso seria comprobar si el usuario ha votado ya con anterioridad en la votacion.
    #Para ello deberia quizas crear una relacion varios a varios
    #El segundo paso, una vez comprobado es meter los datos en la base de datos., con una segunda relacion.
    poll=Poll.query.get_or_404(id)
    outputdata={}
    if(poll not in user.filled_polls):
        try:
            user.filled_polls.append(poll)
            for x_preference in data['optionId_preference']:
                option=PollOption.query.get(x_preference)
                if (option not in poll.options):
                    raise Exception("Somehow an option not in polls options has entered!!!")
                user.votes.append(option) #Guardamos uno a uno los votos
            db.session.commit()
            outputdata["success"]=True
        except:
            outputdata["success"]=False
            outputdata["reason"]="INTERNAL ERROR"
    else:
        #En este caso, la encuesta ya ha sido realizada con anterioridad, y no debe ser rellenada de nuevo.
        outputdata["success"]=False;
        outputdata["reason"]="User has already voted!!!"
    return jsonify(outputdata)

@bp.route('/deletePoll', methods=['DELETE'])
@bp.route('/deletePoll/<int:id>', methods=['DELETE'])
@login_required
@role_necessary(rol=['Admin'])
def deletePoll(id=None):
    try:
        poll = Poll.query.get_or_404(id)
        db.session.delete(poll)
        db.session.commit()
        data={'success':'true'}
    except:
        data={'success':'false'}
    finally:
        return jsonify(data)
