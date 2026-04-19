from datetime import timedelta
import json
from flask import Flask, render_template,request,make_response,redirect,url_for,session,flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from forms.Login_Form import Login_Form
from forms.Post_Form import Post_Form
from forms.Filtro_Form import Filtro_Form
from forms.Comentario_Form import Comentario_Form


app = Flask(__name__)

app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

@app.route("/", methods=["POST", "GET"])
def logar():
    formulario = Login_Form()

    if formulario.validate_on_submit():
        novo_usuario = {
            'nome': formulario.nome.data,
            'senha': formulario.senha.data
        }
        cookies = request.cookies.get('lista_usuarios')

        if cookies:
            lst_usuarios = json.loads(cookies)

            usuario_encontrado = False
            for usuario in lst_usuarios:
                if usuario['nome'] == novo_usuario['nome']:
                    usuario_encontrado = True

                    if usuario['senha'] == novo_usuario['senha']:
                        session['usuario_logado'] = usuario['nome']
                        flash("Usuário logado com sucesso!")
                    else:
                        flash("Senha incorreta")
                        
            if not usuario_encontrado:
                flash("Usuário não encontrado")
               
        else:
            criar_conta()

        resposta = redirect(url_for('logar'))
        resposta.set_cookie('lista_usuarios', json.dumps(lst_usuarios), max_age=36000)

        return resposta
    
    return render_template("tela_login.html", form = formulario)

@app.route("/criar-conta", methods=["GET", "POST"])
def criar_conta():
    formulario = Login_Form()

    if formulario.validate_on_submit():
        novo_usuario = {
            'nome': formulario.nome.data,
            'senha': formulario.senha.data
        }
        cookies = request.cookies.get('lista_usuarios')

        if cookies:
            lst_usuarios = json.loads(cookies)

            nome_disponivel = True
            for usuario in lst_usuarios:
                if usuario['nome'] == novo_usuario['nome']:
                    nome_disponivel = False

            if nome_disponivel:
                lst_usuarios.append(novo_usuario)
                session['usuario_logado'] = novo_usuario['nome']
                flash("Usuário criado com sucesso")
            else:
                flash("O nome de usuário informado já está sendo utilizado!")

        else:
            lst_usuarios = [novo_usuario]
            session['usuario_logado'] = novo_usuario['nome']

        resposta = redirect(url_for('criar_conta'))
        resposta.set_cookie('lista_usuarios', json.dumps(lst_usuarios), max_age=36000)

        return resposta
    
    return render_template("index.html",form=formulario)

@app.route("/sair", methods=["GET"])
def sair():
    if 'usuario_logado' in session:
        session.clear()

        resposta = redirect(url_for('logar'))
        return resposta
    
    return redirect(url_for('logar'))


@app.route("/publicar-post", methods=["POST","GET"])
def publicar_post():
    formulario = Post_Form()
    if formulario.validate_on_submit():
        novo_post = {
            'autor': session.get('usuario_logado'),
            'escola': formulario.escola.data,
            'titulo': formulario.titulo.data,
            'texto': formulario.texto.data,
            'data': datetime.now().strftime("%d/%m/%Y"),
            'comentarios': []
        }
        cookies = request.cookies.get('lista_posts')

        if 'usuario_logado' in session:
            if cookies:
                lst_posts = json.loads(cookies)
                lst_posts.append(novo_post)
            else:
                lst_posts = [novo_post]
                
            resposta = redirect(url_for('publicar_post'))
            resposta.set_cookie('lista_posts', json.dumps(lst_posts), max_age=36000)

            return resposta
        
        else:
            flash("Não é possível publicar o post pois não há usuário logado!")
            
    return render_template("criar_post.html", form=formulario, usuario_logado=session.get('usuario_logado'))

@app.route("/posts", methods=["POST","GET"])
def exibir_posts():
    cookies = request.cookies.get('lista_posts')
    print(f"cookies: {cookies}")

    if cookies:
        lst_posts = json.loads(cookies)
    else:
        lst_posts = []

    filtro = Filtro_Form()
    if filtro.validate_on_submit():
        escola = filtro.escola.data
        lst_posts = filtrar_posts(escola, lst_posts)

    existe_posts = len(lst_posts) > 0

    return render_template("feed.html", posts=lst_posts,existe_posts=existe_posts,form=filtro)

def filtrar_posts(escola, list_posts):
    if (not escola):
        return list_posts

    posts_buscados = []

    for post in list_posts:
        if (post.get("escola").lower() == escola.lower()):
            posts_buscados.append(post)

    return posts_buscados

@app.route("/post/<int:post_id>", methods = ["POST", "GET"])
def abrir_post(post_id):
    post = buscar_post(post_id)

    comentario_form = Comentario_Form()
    if comentario_form.validate_on_submit():
        return comentar(comentario_form, post_id)

    comentarios = post.get('comentarios', [])
    existe_comentarios = len(comentarios) > 0

    return render_template("post.html",post=post,post_id=post_id,form=comentario_form,comentarios=comentarios,
                           existe_comentarios=existe_comentarios,usuario_logado=session.get('usuario_logado'))

def comentar (comentario_form,post_id):
    comentario = {
        'autor': session.get('usuario_logado'),
        'texto': comentario_form.texto.data
    }
    
    if 'usuario_logado' in session:
        cookies = request.cookies.get('lista_posts')
        if cookies:
            lst_posts = json.loads(cookies)
            if "comentarios" not in lst_posts[post_id - 1]:
                lst_posts[post_id - 1]["comentarios"] = []

            lst_posts[post_id - 1]["comentarios"].append(comentario)
            
        resposta = redirect(url_for('abrir_post', post_id=post_id))
        resposta.set_cookie('lista_posts', json.dumps(lst_posts), max_age=36000)
        return resposta
    
    else:
        flash("Não é possível comentar pois não há usuário logado!")

    return redirect(url_for('abrir_post', post_id=post_id))
    
def buscar_post(post_id):
    cookies = request.cookies.get('lista_posts')
    if cookies:
        lst_posts = json.loads(cookies)
        post = lst_posts[post_id - 1]

    return post

@app.route("/editar/<int:post_id>", methods=["POST"])  
def editar_post(post_id):
    cookies = request.cookies.get('lista_posts')
    post = None
    
    if cookies:
            lst_posts = json.loads(cookies)   
            posts_usuario = filtrar_posts_usuario(lst_posts)
            post = posts_usuario[post_id - 1]
            indice_lst = lst_posts.index(post)
             

    formulario = Post_Form()
    if formulario.validate_on_submit():
        edicao_post = {
            'autor': session.get('usuario_logado'),
            'escola': formulario.escola.data,
            'titulo': formulario.titulo.data,
            'texto': formulario.texto.data,
            'data': datetime.now().strftime("%d/%m/%Y"),
            'comentarios': post.get('comentarios')
        }    

        lst_posts[indice_lst] = edicao_post      
    
        resposta = redirect(url_for('abrir_perfil'))
        resposta.set_cookie('lista_posts', json.dumps(lst_posts))

        return resposta
     
    return render_template("editar_post.html",form=formulario,usuario=session.get('usuario_logado'),post=post)


@app.route("/excluir/<int:post_id>", methods=["POST"])
def excluir_post(post_id):
    cookies = request.cookies.get('lista_posts')
    if cookies:
        lst_posts = json.loads(cookies)
        posts_usuario = filtrar_posts_usuario(lst_posts)
        
        post = posts_usuario[post_id - 1]
        lst_posts.remove(post)

        resposta = redirect(url_for('abrir_perfil'))
        resposta.set_cookie('lista_posts', json.dumps(lst_posts))

        return resposta
    
@app.route("/perfil", methods=["GET","POST"])
def abrir_perfil():
    cookies = request.cookies.get('lista_posts')
    print(f"cookies: {cookies}")

    if cookies:
        lst_posts = json.loads(cookies)
        posts_usuario = filtrar_posts_usuario(lst_posts)

    existe_posts = len(posts_usuario) > 0

    return render_template("perfil.html", posts=posts_usuario,existe_posts=existe_posts,usuario=session.get('usuario_logado'))

def filtrar_posts_usuario(lst_posts):
    posts_usuario = []

    for post in lst_posts:
        if (post.get("autor") == session.get('usuario_logado')):
            posts_usuario.append(post)

    return posts_usuario


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)