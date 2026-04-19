from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Login_Form(FlaskForm):
    nome = StringField('Nome: ', validators=[DataRequired()])
    senha = StringField('Senha: ', validators=[DataRequired()])
    
    submit = SubmitField('Entrar')