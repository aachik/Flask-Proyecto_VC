from flask import (Flask, g, render_template, flash, redirect, url_for)
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
	return render_template('index.html')


@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
	form = forms.RegistroForm()
	if form.validate_on_submit():
		flash('Registro Exitoso!', 'exito')
		usuario = models.Usuario.nuevo(
			usuario=form.usuario.data,
			email=form.email.data,
			puntos=10,
			password=form.password.data
		)
		login_user(usuario)
		return redirect(url_for('main'))
	return render_template('registro.html', form=form)


@app.route('/vacantes/subir', methods=['GET', 'POST'])
@login_required
def subir_vacante():
	form = forms.VacanteForm()
	if form.validate_on_submit():
		flash('Registro Exitoso!', 'exito')
		img = form.imagen.data
		path=os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
		with open(path, 'wb+') as f:
			f.write(img.read())

		models.Vacante.nueva(
			titulo=form.titulo.data,
			descripcion=form.descripcion.data,
			contacto=form.contacto.data,
			direccion=form.direccion.data,
			usuario=g.user._get_current_object(),
			imagen=img.filename
		)
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
				flash('Haz iniciado sesion exitosamente!', 'success')
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
			return redirect(url_for('vacantes', usuario=g.user._get_current_object()))
		except models.IntegrityError:
			pass
		else:
			flash("Gracias por aplicar {}!".format(aplicante.username), "success")
	
@app.route('/puntaje')
def puntaje():
	return render_template('puntuaje.html')


if __name__ == '__main__':
	#models.drop()
	models.initialize()
	#models.Usuario.nuevo(
	#	usuario='Abdul',
	#	email='abdulhamid@outlook.com',
	#	password='aa121292',
	#	admin=True)
	app.run(
    	debug=DEBUG, 
    	port=PORT, 
    	host=HOST
    )