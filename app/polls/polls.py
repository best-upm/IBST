from flask import render_template, flash, redirect, url_for, jsonify, request
from app import app, db
from flask_login import login_required, current_user
from app.functions import roles_required, role_necessary
from app.polls import bp
from app.polls.PollForms import NewPollForm
from app.models import Poll, PollOption, User
import datetime
from itertools import permutations
import json

"""
Hay tres tipos de votaciones Si/No/Blanco G:2/3 Votos, Si/No/Blanco Simple, Instant Runoff Voting IRV
"""

@bp.route('/newpoll', methods=['GET', 'POST'])
@login_required
@role_necessary(rol=['Admin', 'Full', 'Baby'])  #Se debe cambiar a los que realmente tengan permisos
def newPoll():
    title = 'Crear nueva votación'
    poll = Poll(start_date=datetime.datetime.utcnow())
    form = NewPollForm(obj=poll, start_time=datetime.time(18, 15), end_time=datetime.time(18, 30))
    if(form.validate_on_submit()):
        form.populate_obj(poll)
        poll.start_date=datetime.datetime.combine(form.start_date.data,form.start_time.data)
        poll.end_date=datetime.datetime.combine(form.end_date.data,form.end_time.data)
        poll.id_creator=current_user.id
        options = list(form.Opciones.data.split("; "))
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
    data_Polls = Poll.query.all()
    data_OpenPolls=[]
    data_ClosedPolls=[]
    for poll in data_Polls:
        if (poll.start_date<datetime.datetime.utcnow()):
            if(poll.end_date > datetime.datetime.utcnow()):
                data_OpenPolls.append(poll)
            else:
                data_ClosedPolls.append(poll)

    return render_template('Show_Polls.html', data_OpenPolls=data_OpenPolls,data_ClosedPolls=data_ClosedPolls ,title=title)

@bp.route('/votepoll')
@bp.route('/votepoll/<int:id>', methods=['GET', 'POST'])
@login_required
@role_necessary(rol=['Admin', 'Full', 'Baby'])
def VotePoll(id=None):
    if id == None:
        title = 'Pagina de votaciones'
        return render_template('GoToPoll.html', title=title)
    poll=Poll.query.get_or_404(id);
    return render_template('poll.html', poll=poll, User=User, datetime=datetime)

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
    if(poll.start_date > datetime.datetime.utcnow()):
        outputdata["success"]=False
        outputdata["reason"]="POLL IS NOT OPEN"
    elif(poll.end_date < datetime.datetime.utcnow()):
        outputdata["success"]=False
        outputdata["reason"]="POLL IS ALREADY CLOSED"
    elif(poll not in user.filled_polls):
        try:
            user.filled_polls.append(poll)
            for x_preference in data['optionId_preference']:
                option=PollOption.query.get(x_preference)
                if (option not in poll.options):
                    outputdata["ExtraInf"]="Somehow an option not in polls options has entered!!!"
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

@bp.route('/showPollResults/<int:id>', methods=['GET'])
@login_required
@role_necessary(rol=['Admin'])
def showPollResults(id=None):
    poll=Poll.query.get_or_404(id)
    options=poll.options
    optionsDict={ option.id_option : 0 for option in options}   #Un diccionario con option_ID : num de votos
    voters=poll.voters
    iterations=[]
    for x in range(1, len(options)):
        for voter in voters:
            print(voter.votes, flush=True)
            for i in range(x):
                if(voter.votes[i].id_option in optionsDict):
                    optionsDict[voter.votes[i].id_option]=optionsDict[voter.votes[i].id_option]+1
                    break

        print(optionsDict, flush=True)
        #LLegados a este punto tenemos que encontrar el MAX si no supera el 2/3, eliminar la opcion con menos votos
        most_voted=max(optionsDict, key = lambda k: optionsDict[k])
        print(most_voted, flush=True)
        if(optionsDict[most_voted] > 2*len(voters)/3):
            break;
        else:
            #least_voted=min(optionsDict, key = lambda k: optionsDict[k])
            #least_voted=[key for key in optionsDict if all(optionsDict[temp] >= optionsDict[key] for temp in optionsDict)]
            least_voted=min(optionsDict.values())
            res=[key for key in optionsDict if optionsDict[key]==least_voted]
            #iterations.append(optionsDict)
            print(least_voted, flush=True)
            print(res, flush=True)
            print(len(res), flush=True)
            iterations.insert(x, optionsDict.copy())
            if(len(res) == 1):
                #least_voted=min(optionsDict, key = lambda k: optionsDict[k])
                optionsDict.pop(res[0])
            elif(len(res) > 1):
                #Comentario: Que hacemos cuando 2 opciones son las menos votadas? Podemos mirar cual de las 2 es menos preferida
                #Comentario 2: No podemos eliminar las opciones que siguen en votacion, porque dariamos votos de personas que no votaran a ese grupo
                #temp={ id : 0 for id in res}
                y=x+1
                while(y<len(options)):
                    temp=optionsDict.copy()
                    for option in temp:
                        optionsDict[option]=0
                    for voter in voters:
                        for i in range(y):
                            if(voter.votes[i].id_option in res):
                                temp[voter.votes[i].id_option]=temp[voter.votes[i].id_option]+1
                                break
                    #temp.pop(most_voted)
                    deleteDict=temp.copy()
                    for key in deleteDict.keys():
                        if not key in res:
                            temp.pop(key)
                    least_voted=min(temp.values())
                    res_inside=[key for key in temp if temp[key]==least_voted]
                    if(len(res_inside) == 1):
                        optionsDict.pop(min(temp, key = lambda k: temp[k]))
                        break
                    else:
                        y=y+1

                    print(temp, flush=True)

            #optionsDict.pop(least_voted)
            #optionsDict.pop(res)
            for option in optionsDict:
                optionsDict[option]=0
    print(optionsDict, flush=True)
    print(iterations, flush=True)
    return render_template('showResults.html', poll=poll, datetime=datetime, iterations=iterations, list=list, voters=voters)
