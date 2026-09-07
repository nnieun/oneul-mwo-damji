import json
import time
from uuid import uuid4
from fastapi import APIRouter, Header, HTTPException
from .schemas import AddItem, Cart, Quantity


def read_cart(c, cart_id):
    row = c.execute('SELECT * FROM carts WHERE id=?', (cart_id,)).fetchone()
    if row is None:
        raise HTTPException(404, '장바구니를 찾을 수 없습니다.')
    items=[]
    for item in c.execute('SELECT ci.*,p.name,p.emoji FROM cart_items ci JOIN products p ON p.id=ci.product_id WHERE cart_id=? ORDER BY p.id', (cart_id,)).fetchall():
        line=dict(item)
        line.pop('cart_id')
        line['ingredients']=[r[0] for r in c.execute('SELECT i.name FROM ingredients i JOIN product_ingredients pi ON pi.ingredient_id=i.id WHERE pi.product_id=? ORDER BY i.id', (line['product_id'],))]
        line['subtotal']=line['quantity']*line['unit_price']
        items.append(line)
    return dict(id=row['id'],status=row['status'],revision=row['revision'],items=items,total=sum(i['subtotal'] for i in items),item_count=sum(i['quantity'] for i in items))


def writable(c, cart_id):
    cart=read_cart(c,cart_id)
    if cart['status'] != 'active':
        raise HTTPException(409,'종료된 장바구니입니다.')
    return cart


def bump(c, cart_id):
    c.execute('UPDATE carts SET revision=revision+1,updated_at=CURRENT_TIMESTAMP WHERE id=?',(cart_id,))


def router(db):
    api=APIRouter(prefix='/api/carts',tags=['Cart'])

    @api.post('',response_model=Cart,summary='활성 장바구니 생성 또는 기존 장바구니 반환')
    def create_cart():
        with db.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute("SELECT id FROM carts WHERE status='active'").fetchone()
            cid=row['id'] if row else str(uuid4())
            if not row:
                c.execute('INSERT INTO carts(id) VALUES (?)',(cid,))
            return read_cart(c,cid)

    @api.get('/active',response_model=Cart,summary='현재 활성 장바구니 조회')
    def active_cart():
        with db.connect() as c:
            row=c.execute("SELECT id FROM carts WHERE status='active'").fetchone()
            if row is None:
                raise HTTPException(404,'활성 장바구니가 없습니다.')
            return read_cart(c,row['id'])

    @api.get('/{cart_id}',response_model=Cart,summary='장바구니와 서버 계산 금액 조회')
    def get_cart(cart_id: str):
        with db.connect() as c:
            return read_cart(c,cart_id)

    @api.post('/{cart_id}/items',response_model=Cart,summary='확인한 후보 또는 수동 상품 담기',description='Idempotency-Key는 같은 동작의 재시도에 재사용합니다. 같은 키의 다른 내용은 409입니다. 후보와 상품을 함께 변경하여 오인식을 수정할 수 있습니다.')
    def add_item(cart_id: str, body: AddItem, idempotency_key: str = Header(min_length=8,max_length=128)):
        payload=json.dumps(body.model_dump(),sort_keys=True)
        with db.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            writable(c,cart_id)
            previous=c.execute('SELECT * FROM processed_requests WHERE cart_id=? AND request_key=?',(cart_id,idempotency_key)).fetchone()
            if previous:
                if previous['payload'] != payload:
                    raise HTTPException(409,'같은 요청 키에 다른 내용을 사용할 수 없습니다.')
                return json.loads(previous['response'])
            product=c.execute('SELECT price FROM products WHERE id=?',(body.product_id,)).fetchone()
            if not product:
                raise HTTPException(404,'상품을 찾을 수 없습니다.')
            if body.candidate_id:
                candidate=c.execute('SELECT * FROM recognition_candidates WHERE id=?',(body.candidate_id,)).fetchone()
                if candidate is None:
                    raise HTTPException(404,'인식 후보를 찾을 수 없습니다.')
                if candidate['status'] != 'pending' or candidate['expires_at'] <= time.time():
                    raise HTTPException(409,'처리되었거나 만료된 후보입니다. 다시 스캔해 주세요.')
            old=c.execute('SELECT quantity FROM cart_items WHERE cart_id=? AND product_id=?',(cart_id,body.product_id)).fetchone()
            if (old['quantity'] if old else 0)+body.quantity > 999:
                raise HTTPException(409,'상품 수량은 999개를 초과할 수 없습니다.')
            c.execute('INSERT INTO cart_items VALUES (?,?,?,?) ON CONFLICT(cart_id,product_id) DO UPDATE SET quantity=quantity+excluded.quantity',(cart_id,body.product_id,body.quantity,product['price']))
            if body.candidate_id:
                c.execute("UPDATE recognition_candidates SET status='confirmed' WHERE id=?",(body.candidate_id,))
            bump(c,cart_id)
            result=read_cart(c,cart_id)
            c.execute('INSERT INTO processed_requests VALUES (?,?,?,?)',(cart_id,idempotency_key,payload,json.dumps(result,ensure_ascii=False)))
            return result

    @api.patch('/{cart_id}/items/{product_id}',response_model=Cart,summary='상품의 최종 수량 설정')
    def change_quantity(cart_id: str, product_id: int, body: Quantity):
        with db.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            writable(c,cart_id)
            result=c.execute('UPDATE cart_items SET quantity=? WHERE cart_id=? AND product_id=?',(body.quantity,cart_id,product_id))
            if not result.rowcount:
                raise HTTPException(404,'장바구니 항목을 찾을 수 없습니다.')
            bump(c,cart_id)
            return read_cart(c,cart_id)

    @api.delete('/{cart_id}/items/{product_id}',response_model=Cart,summary='장바구니 상품 삭제')
    def delete_item(cart_id: str, product_id: int):
        with db.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            writable(c,cart_id)
            result=c.execute('DELETE FROM cart_items WHERE cart_id=? AND product_id=?',(cart_id,product_id))
            if not result.rowcount:
                raise HTTPException(404,'장바구니 항목을 찾을 수 없습니다.')
            bump(c,cart_id)
            return read_cart(c,cart_id)
    return api
