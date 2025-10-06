from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired(), Length(min=1, max=50)])
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description')

class LocationForm(FlaskForm):
    location_id = StringField('Location ID', validators=[DataRequired(), Length(min=1, max=50)])
    location_name = StringField('Location Name', validators=[DataRequired(), Length(min=1, max=100)])

class ProductMovementForm(FlaskForm):
    product_id = SelectField('Product', validators=[DataRequired()])
    from_location = SelectField('From Location', validators=[Optional()], choices=[('', '-- Select Location --')])
    to_location = SelectField('To Location', validators=[Optional()], choices=[('', '-- Select Location --')])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
