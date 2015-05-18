import datetime

from flask.ext.login import UserMixin
from flask.ext.bcrypt import generate_password_hash
from peewee import *

DATABASE = SqliteDatabase('database.db')

class Usuario(UserMixin, Model):
    usuario = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    puntos = IntegerField(default=0)
    twitter_id = CharField(unique=True)
    bio = CharField(max_length=280)
    registro = DateTimeField(default=datetime.datetime.now)
    es_admin = BooleanField(default=False)
    
    class Meta:
        database = DATABASE
        order_by = ('-registro',)

    @classmethod
    def nuevo(cls, usuario, email, password, twitter_id, bio, admin=False, puntos=0):
    	try:
    		cls.create(
	    		usuario=usuario,
	    		email=email,
	    		puntos=puntos,
	    		twitter_id=twitter_id,
	    		bio=bio,
	    		password=generate_password_hash(password),
	    		es_admin=admin
	    	)
    	except IntegrityError:
    		raise ValueError("El usuario ya existe")

    def vacantes(self):
    	return (
    		Usuario.select().join(
    			Aplicantes, on=Aplicantes.vacante).where(
    			Aplicantes.aplicante == self
    			)
    	)

    def mejores_puntajes(self):
    	return (Usuario.select().order_by(-Usuario.puntos))

    def __repr__(self):
    	return '{}'.format(self.usuario)

class Vacante(Model):
	titulo = CharField(null=False, unique=True)
	descripcion = TextField(null=False)
	contacto = TextField(null=False)
	imagen = CharField(null=True)
	finalizada = BooleanField(null=False)
	direccion = TextField(unique=False)
	usuario = ForeignKeyField(Usuario)
	creado = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DATABASE
		order_by = ('-creado',)

	@classmethod
	def nueva(cls, titulo, descripcion, contacto, imagen, direccion, usuario, finalizada=False):
		try:
			cls.create(
				titulo=titulo,
				descripcion=descripcion,
				contacto=contacto,
				finalizada=finalizada,
				direccion=direccion,
				usuario=usuario,
				imagen=imagen
			)
		except IntegrityError:
			raise ValueError("La vacante ya existe")

	def aplicantes(self):
		return (
    		Usuario.select().join(
    			Aplicantes, on=Aplicantes.aplicante).where(
    			Aplicantes.vacante == self
    			)
    	)

class Aplicantes(Model):
	vacante = ForeignKeyField(Vacante, related_name='vacante')
	aplicante = ForeignKeyField(Usuario, related_name='aplicante')

	class Meta:
		database = DATABASE
		indexes = (
			(('vacante','aplicante'), True),
		)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Usuario, Vacante, Aplicantes], safe=True)
    DATABASE.close()

def drop():
	DATABASE.connect()
	DATABASE.drop_tables([Usuario, Vacante, Aplicantes], safe=True)
	DATABASE.close()