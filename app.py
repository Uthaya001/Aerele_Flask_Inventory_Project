from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect, generate_csrf
from models import db, Product, Location, ProductMovement
from forms import ProductForm, LocationForm, ProductMovementForm
from sqlalchemy import func
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
csrf = CSRFProtect(app)

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/products/view/<product_id>')
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_view.html', product=product)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        existing_product = Product.query.get(form.product_id.data)
        if existing_product:
            flash(f'Product ID "{form.product_id.data}" already exists!', 'danger')
            return render_template('product_form.html', form=form, action='Add')
        
        product = Product(
            product_id=form.product_id.data,
            product_name=form.product_name.data,
            description=form.description.data
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{product.product_name}" added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('product_form.html', form=form, action='Add')

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.product_name = form.product_name.data
        product.description = form.description.data
        db.session.commit()
        flash(f'Product "{product.product_name}" updated successfully!', 'success')
        return redirect(url_for('products'))
    
    form.product_id.render_kw = {'readonly': True}
    return render_template('product_form.html', form=form, action='Edit', product=product)

@app.route('/products/delete/<product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_name = product.product_name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product_name}" deleted successfully!', 'success')
    return redirect(url_for('products'))

@app.route('/locations')
def locations():
    all_locations = Location.query.all()
    return render_template('locations.html', locations=all_locations)

@app.route('/locations/view/<location_id>')
def view_location(location_id):
    location = Location.query.get_or_404(location_id)
    return render_template('location_view.html', location=location)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        existing_location = Location.query.get(form.location_id.data)
        if existing_location:
            flash(f'Location ID "{form.location_id.data}" already exists!', 'danger')
            return render_template('location_form.html', form=form, action='Add')
        
        location = Location(
            location_id=form.location_id.data,
            location_name=form.location_name.data
        )
        db.session.add(location)
        db.session.commit()
        flash(f'Location "{location.location_name}" added successfully!', 'success')
        return redirect(url_for('locations'))
    return render_template('location_form.html', form=form, action='Add')

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    form = LocationForm(obj=location)
    
    if form.validate_on_submit():
        location.location_name = form.location_name.data
        db.session.commit()
        flash(f'Location "{location.location_name}" updated successfully!', 'success')
        return redirect(url_for('locations'))
    
    form.location_id.render_kw = {'readonly': True}
    return render_template('location_form.html', form=form, action='Edit', location=location)

@app.route('/locations/delete/<location_id>', methods=['POST'])
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    location_name = location.location_name
    db.session.delete(location)
    db.session.commit()
    flash(f'Location "{location_name}" deleted successfully!', 'success')
    return redirect(url_for('locations'))

@app.route('/movements')
def movements():
    all_movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', movements=all_movements)

@app.route('/movements/view/<int:movement_id>')
def view_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    return render_template('movement_view.html', movement=movement)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    form = ProductMovementForm()
    
    products = Product.query.all()
    locations = Location.query.all()
    
    form.product_id.choices = [(p.product_id, f'{p.product_id} - {p.product_name}') for p in products]
    form.from_location.choices = [('', '-- Select Location --')] + [(l.location_id, f'{l.location_id} - {l.location_name}') for l in locations]
    form.to_location.choices = [('', '-- Select Location --')] + [(l.location_id, f'{l.location_id} - {l.location_name}') for l in locations]
    
    if form.validate_on_submit():
        from_loc = form.from_location.data if form.from_location.data else None
        to_loc = form.to_location.data if form.to_location.data else None
        
        if not from_loc and not to_loc:
            flash('Either "From Location" or "To Location" must be selected!', 'danger')
            return render_template('movement_form.html', form=form, action='Add')
        
        movement = ProductMovement(
            product_id=form.product_id.data,
            from_location=from_loc,
            to_location=to_loc,
            qty=form.qty.data
        )
        db.session.add(movement)
        db.session.commit()
        flash('Product movement recorded successfully!', 'success')
        return redirect(url_for('movements'))
    
    return render_template('movement_form.html', form=form, action='Add')

@app.route('/movements/edit/<int:movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    form = ProductMovementForm(obj=movement)
    
    products = Product.query.all()
    locations = Location.query.all()
    
    form.product_id.choices = [(p.product_id, f'{p.product_id} - {p.product_name}') for p in products]
    form.from_location.choices = [('', '-- Select Location --')] + [(l.location_id, f'{l.location_id} - {l.location_name}') for l in locations]
    form.to_location.choices = [('', '-- Select Location --')] + [(l.location_id, f'{l.location_id} - {l.location_name}') for l in locations]
    
    if form.validate_on_submit():
        from_loc = form.from_location.data if form.from_location.data else None
        to_loc = form.to_location.data if form.to_location.data else None
        
        if not from_loc and not to_loc:
            flash('Either "From Location" or "To Location" must be selected!', 'danger')
            return render_template('movement_form.html', form=form, action='Edit', movement=movement)
        
        movement.product_id = form.product_id.data
        movement.from_location = from_loc
        movement.to_location = to_loc
        movement.qty = form.qty.data
        db.session.commit()
        flash('Product movement updated successfully!', 'success')
        return redirect(url_for('movements'))
    
    if not form.is_submitted():
        form.from_location.data = movement.from_location or ''
        form.to_location.data = movement.to_location or ''
    
    return render_template('movement_form.html', form=form, action='Edit', movement=movement)

@app.route('/movements/delete/<int:movement_id>', methods=['POST'])
def delete_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    db.session.delete(movement)
    db.session.commit()
    flash('Product movement deleted successfully!', 'success')
    return redirect(url_for('movements'))

@app.route('/report')
def report():
    balance_query = db.session.query(
        Product.product_id,
        Product.product_name,
        Location.location_id,
        Location.location_name,
        func.coalesce(
            func.sum(
                db.case(
                    (ProductMovement.to_location == Location.location_id, ProductMovement.qty),
                    else_=0
                )
            ) -
            func.sum(
                db.case(
                    (ProductMovement.from_location == Location.location_id, ProductMovement.qty),
                    else_=0
                )
            ),
            0
        ).label('balance')
    ).select_from(Product).join(
        ProductMovement, Product.product_id == ProductMovement.product_id
    ).join(
        Location,
        db.or_(
            ProductMovement.to_location == Location.location_id,
            ProductMovement.from_location == Location.location_id
        )
    ).group_by(
        Product.product_id,
        Product.product_name,
        Location.location_id,
        Location.location_name
    ).order_by(
        Product.product_id,
        Location.location_id
    ).all()
    
    return render_template('report.html', balances=balance_query)

def init_sample_data():
    if Product.query.count() > 0:
        return
    
    products = [
        Product(product_id='P001', product_name='Laptop', description='Dell Latitude 15 inch'),
        Product(product_id='P002', product_name='Mouse', description='Wireless optical mouse'),
        Product(product_id='P003', product_name='Keyboard', description='Mechanical keyboard'),
        Product(product_id='P004', product_name='Monitor', description='24 inch LED monitor')
    ]
    
    locations = [
        Location(location_id='WH-A', location_name='Warehouse A'),
        Location(location_id='WH-B', location_name='Warehouse B'),
        Location(location_id='WH-C', location_name='Warehouse C'),
        Location(location_id='STORE', location_name='Retail Store')
    ]
    
    for p in products:
        db.session.add(p)
    for l in locations:
        db.session.add(l)
    db.session.commit()
    
    movements = [
        ProductMovement(product_id='P001', to_location='WH-A', qty=50),
        ProductMovement(product_id='P002', to_location='WH-A', qty=100),
        ProductMovement(product_id='P003', to_location='WH-B', qty=75),
        ProductMovement(product_id='P004', to_location='WH-C', qty=30),
        ProductMovement(product_id='P001', from_location='WH-A', to_location='WH-B', qty=15),
        ProductMovement(product_id='P002', from_location='WH-A', to_location='STORE', qty=30),
        ProductMovement(product_id='P003', from_location='WH-B', to_location='WH-A', qty=20),
        ProductMovement(product_id='P004', from_location='WH-C', to_location='STORE', qty=10),
        ProductMovement(product_id='P001', to_location='WH-C', qty=25),
        ProductMovement(product_id='P002', to_location='WH-B', qty=50),
        ProductMovement(product_id='P003', from_location='WH-A', to_location='STORE', qty=15),
        ProductMovement(product_id='P004', to_location='WH-A', qty=20),
        ProductMovement(product_id='P001', from_location='WH-B', to_location='STORE', qty=10),
        ProductMovement(product_id='P002', from_location='STORE', to_location='WH-C', qty=5),
        ProductMovement(product_id='P003', to_location='WH-C', qty=40),
        ProductMovement(product_id='P004', from_location='WH-A', to_location='WH-B', qty=8),
        ProductMovement(product_id='P001', from_location='WH-C', qty=5),
        ProductMovement(product_id='P002', from_location='WH-B', to_location='WH-A', qty=15),
        ProductMovement(product_id='P003', from_location='WH-C', to_location='WH-B', qty=10),
        ProductMovement(product_id='P004', to_location='STORE', qty=15),
        ProductMovement(product_id='P001', from_location='STORE', qty=3),
        ProductMovement(product_id='P002', to_location='WH-C', qty=20),
    ]
    
    for m in movements:
        db.session.add(m)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
