import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Bakery as BakeryModel, db

class Bakery(SQLAlchemyObjectType):
    class Meta:
        model = BakeryModel
        
class Query(graphene.ObjectType):
    items = graphene.List(Bakery)
    search_items = graphene.List(Bakery, name=graphene.String(), price=graphene.Decimal(), quantity=graphene.Int(), category=graphene.String())
    
    def resolve_items(self, info):
        return db.session.execute(db.select(BakeryModel)).scalars()
    def resolve_search_items(self, info, name=None, price=None, quantity=None, category=None):
        query = db.select(BakeryModel)
        if name:
            query = query.where(BakeryModel.name.ilike(f"%{name}%"))
        if price:
            query = query.where(BakeryModel.price.ilike(f"%{price}%"))
        if quantity:
            query = query.where(BakeryModel.quantity.ilike(f"%{quantity}%"))
        if category:
            query = query.where(BakeryModel.category.ilike(f"%{category}%"))
        results = db.session.execute(query).scalars().all()
        return results
    
class AddItem(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        quantity = graphene.Int(required=True)
        category = graphene.String(required=True)
        
    item = graphene.Field(Bakery)
    
    def mutate(self, info, name, price, quantity, category):
        item = BakeryModel(name=name, price=price, quantity=quantity, category=category)
        db.session.add(item)
        db.session.commit()
        
        db.session.refresh(item)
        return AddItem(item=item)
    
class UpdateItem(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        quantity = graphene.Int(required=True)
        category = graphene.String(required=True)
    
    item = graphene.Field(Bakery)
    
    def mutate(self, info, id, name=None, price=None, quantity=None, category=None):
        item = db.session.get(BakeryModel, id)
        if not item:
            return None
        if name:
            item.name = name
        if price:
            item.price = price
        if quantity:
            item.quantity = quantity
        if category:
            item.category = category
            
        db.session.add(item)
        db.session.commit()
        return UpdateItem(item=item)

class DeleteItem(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    item = graphene.Field(Bakery)
    
    def mutate(self, info, id):
        item = db.session.get(BakeryModel, id)
        if item:
            db.session.delete(item)
            db.session.commit()
        else:
            return None
        
        return DeleteItem(item=item)
    
class Mutation(graphene.ObjectType):
    create_item = AddItem.Field()
    update_item = UpdateItem.Field()
    delete_item = DeleteItem.Field()