from flask_wtf import Form
from wtforms import StringField, PasswordField, FileField, TextField, TextAreaField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo)

from models import Usuario, Vacante


def nombre_existe(form, field):
    if Usuario.select().where(Usuario.usuario == field.data).exists():
        raise ValidationError('el usuario con ese nombre ya existe.')


def email_existe(form, field):
    if Usuario.select().where(Usuario.email == field.data).exists():
        raise ValidationError('el usuario con ese correo ya existe.')

def titulo_existe(form, field):
    if Vacante.select().where(Vacante.titulo == field.data).exists():
        raise ValidationError('el titulo para esa vacante ya existe')



class RegistroForm(Form):
    usuario = StringField(
        'Usuario',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("El usuario puede contener solo letras, "
                         "numeros y guiones bajos")
            ),
            nombre_existe
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_existe
        ])
    twitter = StringField('Twitter')

    bio = TextAreaField('Biografia:')
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Los passwords deben ser iguales')
        ])
    password2 = PasswordField(
        'Confirmar Password',
        validators=[DataRequired()]
    )


class VacanteForm(Form):
    titulo = StringField(
        'Titulo',
        validators=[
            DataRequired(),
            titulo_existe
        ])
    descripcion = TextAreaField(
        'Descripcion',
        validators=[
            DataRequired(),
        ])
    contacto = TextAreaField(
        'Informacion de contacto',
        validators=[
            DataRequired(),
        ])

    direccion = StringField('Direccion', validators=[DataRequired(),])
    descripcion_imagen1 = StringField('Titulo de la imagen 1', validators=[DataRequired(),])
    imagen1 = FileField('Imagen 1', validators=[DataRequired(),])
    descripcion_imagen2 = StringField('Titulo de la imagen 2', validators=[DataRequired(),])
    imagen2 = FileField('Imagen 2',validators=[DataRequired(),])
    descripcion_imagen3 = StringField('Titulo de la imagen 3', validators=[DataRequired(),])
    imagen3 = FileField('Imagen 3', validators=[DataRequired(),])

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])