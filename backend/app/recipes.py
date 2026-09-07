import json
from fastapi import APIRouter, HTTPException
from .cart import read_cart
from .schemas import Recipe, Recommendations


def list_recipes(c):
    recipes=[]
    for row in c.execute('SELECT * FROM recipes ORDER BY id').fetchall():
        ingredients=[dict(r) for r in c.execute('SELECT i.id,i.name,ri.amount,ri.required FROM recipe_ingredients ri JOIN ingredients i ON i.id=ri.ingredient_id WHERE recipe_id=? ORDER BY ri.position',(row['id'],))]
        recipes.append(dict(id=row['id'],name=row['name'],cooking_time_minutes=row['minutes'],servings=row['servings'],steps=json.loads(row['steps']),is_dummy=bool(row['is_dummy']),ingredients=ingredients))
    return recipes


def router(db):
    api=APIRouter(tags=['Recipes'])

    @api.get('/api/recipes',response_model=list[Recipe],summary='시연용 레시피 목록과 재료 조회')
    def recipes():
        with db.connect() as c:
            return list_recipes(c)

    @api.get('/api/recipes/{recipe_id}',response_model=Recipe,summary='레시피 상세와 조리 순서 조회')
    def detail(recipe_id: int):
        with db.connect() as c:
            for recipe in list_recipes(c):
                if recipe['id']==recipe_id:
                    return recipe
        raise HTTPException(404,'레시피를 찾을 수 없습니다.')

    @api.get('/api/carts/{cart_id}/recommendations',response_model=Recommendations,summary='장바구니 식재료 기반 추천',description='필수 재료 0개 부족은 ready, 1~2개 부족 및 일치 재료가 있으면 almost. 선택 재료는 분류에서 제외합니다. 분량은 판정하지 않습니다.')
    def recommend(cart_id: str):
        with db.connect() as c:
            cart=read_cart(c,cart_id)
            owned_ids={r[0] for r in c.execute('SELECT DISTINCT pi.ingredient_id FROM cart_items ci JOIN product_ingredients pi ON pi.product_id=ci.product_id WHERE ci.cart_id=?',(cart_id,))}
            owned=sorted({name for item in cart['items'] for name in item['ingredients']})
            results=[]
            if owned_ids:
                for recipe in list_recipes(c):
                    required=[i for i in recipe['ingredients'] if i['required']]
                    matched=[i['name'] for i in required if i['id'] in owned_ids]
                    missing=[i['name'] for i in required if i['id'] not in owned_ids]
                    if not matched or len(missing)>2:
                        continue
                    optional_missing=[i['name'] for i in recipe['ingredients'] if not i['required'] and i['id'] not in owned_ids]
                    results.append(dict(**recipe,matched=matched,missing=missing,optional_missing=optional_missing,match_ratio=len(matched)/len(required),category='ready' if not missing else 'almost'))
            results.sort(key=lambda r:(len(r['missing']),-r['match_ratio'],r['cooking_time_minutes'],r['id']))
            return dict(cart_id=cart_id,revision=cart['revision'],owned=owned,recipes=results)
    return api
