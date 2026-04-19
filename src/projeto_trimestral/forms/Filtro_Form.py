from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Filtro_Form(FlaskForm):
    escola = StringField('Escola: ')
    submit = SubmitField('Filtrar')