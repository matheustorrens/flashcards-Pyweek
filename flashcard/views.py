from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, FlashcardDesafio, Desafio
from django.contrib.messages import constants
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib import auth

def novo_flashcard(request):

    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    # Se a requisição for pela URL:
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        # Pega todos os objetos que for do usuário logado
        flashcards = Flashcard.objects.filter(user=request.user)

        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')

        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar)
        
        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)


        return render(request, 'novo_flashcard.html', {'categorias': categorias,
                                                        'dificuldades': dificuldades, 
                                                        'flashcards': flashcards,})
    
    elif request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta.strip()) == 0 and len(resposta.strip()) >= 1:
            messages.add_message(request, constants.ERROR, "Não tenha medo, faça uma pergunta!")
            return redirect('/flashcard/novo_flashcard/') 
        if len(pergunta.strip()) >= 1 and len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR, "Dê uma resposta à pergunta, horas...")
            return redirect('/flashcard/novo_flashcard/') 
        if len(pergunta.strip()) == 0 and len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR, "Vamos, faça uma pergunta e uma resposta!") 
            return redirect('/flashcard/novo_flashcard/') 

        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade,

        )
        flashcard.save()

        messages.add_message(request, constants.SUCCESS, "Boaaa, sua flashcard foi criada! Dê uma olhada ao lado! ")
        return redirect('/flashcard/novo_flashcard/')

def deletar_flashcard(request, id):

    # Validação para buscar apenas os flashcards do usuário logado
    flashcard_id = Flashcard.objects.filter(user=request.user, id=id)

    if not flashcard_id.exists():
        messages.add_message(request, constants.SUCCESS, 'Da uma de espertinho não, se liga')
        return redirect('/flashcard/novo_flashcard/')
            
    else:
        flashcard_id.delete()

        messages.add_message(request, constants.SUCCESS, 'Ixi, flashcard excluido!')
        return redirect('/flashcard/novo_flashcard/')

def iniciar_desafio(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(request, 'iniciar_desafio.html', {'categorias': categorias, 'dificuldades': dificuldades})
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade,
        )
        desafio.save()

        # O "*" antes de uma lista serve para iterar sobre ela, esse método é chamado de desempacotamento OU unpacking
        # for categoria in categorias:
        # desafio.categoria.add(categoria) -> Funcionaria da mesma forma 
        desafio.categoria.add(*categorias)

        flashcards = (
            Flashcard.objects.filter(user=request.user)
            .filter(dificuldade=dificuldade)
            .filter(categoria_id__in=categorias)
            .order_by('?')
        
        )

        if flashcards.count() < int(qtd_perguntas):
            # messages.add_message(request, constants.ERROR, "Nem tem tantas questões pra essa quantidade toda")
            return redirect('/flashcard/iniciar_desafio/') 
        

        flashcards = flashcards[: int(qtd_perguntas)]

        for flash in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=flash
            )
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)
        desafio.save()
            
        return redirect('/flashcard/listar_desafio/')

def listar_desafio(request):
    desafios = Desafio.objects.filter(user=request.user)
    #TODO: desenvolver os status (feito ou a fazer)

    #TODO: desenvover os filtros
    if request.method == 'GET':
        pass

    return render(request, 'listar_desafio.html', {'desafios': desafios})

def desafio(request, id):
    desafio = Desafio.objects.get(id=id)
    if not desafio.user == request.user:
        raise Http404()

    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
        erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()


        return render(request, 'desafio.html', {'desafio': desafio, 'acertos': acertos, 'erros': erros, 'faltantes': faltantes})

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()
    
    flashcard_desafio.respondido = True

    flashcard_desafio.acertou = True if acertou == "1" else False
    flashcard_desafio.save()

    return redirect(f'/flashcard/desafio/{desafio_id}')