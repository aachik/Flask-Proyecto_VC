from flask import (Flask, g, render_template, flash, redirect, url_for, request)
from flask.ext.login import (LoginManager, login_user, logout_user, login_required, current_user)
from flask.ext.bcrypt import check_password_hash
import forms
import models
from werkzeug import secure_filename
import os

DEBUG = True
PORT = 8000
HOST = '127.0.0.1'
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/static/media/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'daniela_omg'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def cargar_usuario(usuarioid):
    try:
        return models.Usuario.get(models.Usuario.id == usuarioid)
    except models.DoesNotExist:
        return None


@app.before_request
def antes_request():
	"""Conectarse a la base de datos """
	g.db = models.DATABASE
	g.db.connect()
	g.user = current_user
	

	
@app.after_request
def despues_request(response):
	"""Cerrar la conexion despues de cada request"""
	g.db.close()
	return response


@app.route('/')
def main():
	usuario=g.user._get_current_object()
	return render_template('index.html')


@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
	form = forms.RegistroForm()
	if form.validate_on_submit():
		flash('Registro Exitoso!', 'exito')
		usuario = models.Usuario.nuevo(
			usuario=form.usuario.data,
			email=form.email.data,
			twitter_id=form.twitter_id.data,
			bio=form.bio.data,
			puntos=10,
			password=form.password.data
		)
		return redirect(url_for('iniciar_sesion'))
	return render_template('registro.html', form=form)


@app.route('/vacantes/subir', methods=['GET', 'POST'])
@login_required
def subir_vacante():
	form = forms.VacanteForm()
	if form.validate_on_submit():
		flash('Gracias por subir una vacante! +10!', 'exito')
		usuario = models.Usuario.get(models.Usuario.id**g.user.id)
		img1 = form.imagen1.data
		img2 = form.imagen2.data
		img3 = form.imagen3.data
		path1=os.path.join(app.config['UPLOAD_FOLDER'], img1.filename)
		print(path1)
		path2=os.path.join(app.config['UPLOAD_FOLDER'], img2.filename)
		print(path2)
		path3=os.path.join(app.config['UPLOAD_FOLDER'], img3.filename)
		print(path3)
		with open(path1, 'wb+') as f1:
			f1.write(img1.read())
		with open(path2, 'wb+') as f2:
			f2.write(img2.read())
		with open(path3, 'wb+') as f3:
			f3.write(img3.read())
		models.Vacante.nueva(
			titulo=form.titulo.data,
			descripcion=form.descripcion.data,
			contacto=form.contacto.data,
			direccion=form.direccion.data,
			usuario=usuario,
			descripcion_imagen1=form.descripcion_imagen1.data,
			imagen1=img1.filename,
			descripcion_imagen2=form.descripcion_imagen2.data,
			imagen2=img2.filename,
			descripcion_imagen3=form.descripcion_imagen3.data,
			imagen3=img3.filename
		)
		q = models.Usuario.update(puntos = models.Usuario.puntos + 10).where(models.Usuario.id == g.user.id)
		q.execute()

		return redirect(url_for('main'))
	
	return render_template('agregar_vacantes.html', form=form)


@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
	form = forms.LoginForm()
	if form.validate_on_submit():
		try:
			usuario = models.Usuario.get(models.Usuario.email == form.email.data)
			
		except models.DoesNotExist:
			flash('Tu email o el password no coinciden!', 'error')
		else:
			if check_password_hash(usuario.password, form.password.data):
				login_user(usuario)
				q = models.Usuario.update(puntos = models.Usuario.puntos + 5).where(models.Usuario.id == g.user.id)
				q.execute()
				flash('Haz iniciado sesion exitosamente! +5!', 'success')
				return redirect(url_for('main'))
			else:
				flash('Tu email o el password no coinciden!', 'error')
	return render_template('login.html', form=form)


@app.route('/vacantes')
def vacantes():
	vacantes = models.Vacante.select()
	return render_template('vacantes.html', vacantes=vacantes)


@app.route('/vacantes/<int:ident>')
def vacante(ident):
	try:
		vacante = models.Vacante.get(models.Vacante.id**ident)
		return render_template('vacante.html', vacante=vacante)
	except models.DoesNotExist:
		pass

	
@app.route('/cerrar_sesion')
@login_required
def cerrar_sesion():
	logout_user()
	flash('Haz salido de la sesion exitosamente!', 'success')
	return redirect(url_for('main'))


@app.route('/aplicar/<vacante>')
@login_required
def aplicar(vacante):
	try:
		vacante = models.Vacante.get(models.Vacante.id**vacante)
	except models.DoesNotExist:
		pass
	else:
		try:
			models.Aplicantes.create(
				aplicante=g.user._get_current_object(),
				vacante=vacante
			)
			q = models.Usuario.update(puntos = models.Usuario.puntos + 10).where(models.Usuario.id == g.user.id)
			q.execute()
			flash("Gracias por aplicar {}! toma 15 puntos!".format(g.user._get_current_object().usuario), "success")
			return redirect(url_for('vacantes', usuario=g.user._get_current_object()))
		except models.IntegrityError:
			pass


@app.route('/finalizar/<vacante>', methods=['POST'])
@login_required
def finalizar(vacante):
	vacante = models.Vacante.get(models.Vacante.id**vacante)
	q = models.Vacante.update(finalizada = True).where(models.Vacante.id == vacante.id)
	q.execute()
	q = models.Usuario.update(puntos = models.Usuario.puntos + int(request.form['puntos'])).where(models.Usuario.id == g.user.id)
	q.execute()
	flash('Vacante finalizada, gracias! +20!','success')
	return render_template(url_for('perfil'))


@app.route('/perfil')
@login_required
def perfil():
	usuario = g.user._get_current_object()
	usuario = models.Usuario.get(models.Usuario.id**usuario.id)

	vacantes = usuario.vacantes_creadas()
	aplicaciones = models.Aplicantes.select().where(models.Aplicantes.aplicante== usuario)
	return render_template('perfil.html', usuario=usuario, vacantes=vacantes, aplicaciones=aplicaciones)
	

@app.route('/puntaje')
def puntaje():
	usuarios = models.Usuario.select().order_by(-models.Usuario.puntos)
	return render_template('puntuaje.html', usuarios=usuarios)


if __name__ == '__main__':
	models.initialize()
	
	app.run(
    	debug=DEBUG, 
    	port=PORT, 
    	host=HOST
    )