# server/app.py
from flask import Flask, jsonify, make_response, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizza_restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Pizza Restaurant API</h1>'

class RestaurantList(Resource):
    def get(self):
        """Get all restaurants"""
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])

class RestaurantResource(Resource):
    def get(self, id):
        """Get a specific restaurant with its pizzas"""
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        
        return jsonify(restaurant.to_dict(include_pizzas=True))
    
    def delete(self, id):
        """Delete a restaurant and its associations"""
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class PizzaList(Resource):
    def get(self):
        """Get all pizzas"""
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])

class RestaurantPizzaResource(Resource):
    def post(self):
        """Create a new restaurant-pizza association"""
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['price', 'pizza_id', 'restaurant_id']
        if not all(field in data for field in required_fields):
            return make_response(jsonify({"errors": ["Missing required fields"]}), 400)
        
        price = data['price']
        pizza_id = data['pizza_id']
        restaurant_id = data['restaurant_id']
        
        # Check if restaurant and pizza exist
        restaurant = Restaurant.query.get(restaurant_id)
        pizza = Pizza.query.get(pizza_id)
        if not restaurant or not pizza:
            return make_response(jsonify({"errors": ["Restaurant or Pizza not found"]}), 400)
        
        # Create new association
        try:
            rp = RestaurantPizza(
                price=price,
                restaurant_id=restaurant_id,
                pizza_id=pizza_id
            )
            db.session.add(rp)
            db.session.commit()
        except ValueError as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)
        
        # Return the associated pizza details
        return jsonify(pizza.to_dict()), 201

# Register resources
api.add_resource(RestaurantList, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaList, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)