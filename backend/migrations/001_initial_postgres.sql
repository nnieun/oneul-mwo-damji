-- 오늘 뭐 담지: Supabase PostgreSQL initial schema
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price INTEGER NOT NULL CHECK (price >= 0),
  ingredient TEXT NOT NULL,
  emoji TEXT NOT NULL DEFAULT '🛒'
);
CREATE TABLE IF NOT EXISTS recipes (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  ingredients TEXT NOT NULL,
  cooking_time TEXT NOT NULL,
  minutes INTEGER NOT NULL DEFAULT 10,
  servings INTEGER NOT NULL DEFAULT 1,
  steps TEXT NOT NULL DEFAULT '[]',
  is_dummy BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS ingredients (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS product_ingredients (
  product_id INTEGER NOT NULL REFERENCES products(id),
  ingredient_id BIGINT NOT NULL REFERENCES ingredients(id),
  PRIMARY KEY (product_id, ingredient_id)
);
CREATE TABLE IF NOT EXISTS product_labels (
  model_version TEXT NOT NULL,
  label TEXT NOT NULL,
  product_id INTEGER NOT NULL REFERENCES products(id),
  PRIMARY KEY (model_version, label)
);
CREATE TABLE IF NOT EXISTS recipe_ingredients (
  recipe_id INTEGER NOT NULL REFERENCES recipes(id),
  ingredient_id BIGINT NOT NULL REFERENCES ingredients(id),
  amount TEXT NOT NULL,
  required BOOLEAN NOT NULL,
  position INTEGER NOT NULL,
  PRIMARY KEY (recipe_id, ingredient_id)
);
CREATE TABLE IF NOT EXISTS carts (
  id TEXT PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','closed')),
  revision INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS cart_items (
  cart_id TEXT NOT NULL REFERENCES carts(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL CHECK (quantity BETWEEN 1 AND 999),
  unit_price INTEGER NOT NULL CHECK (unit_price >= 0),
  PRIMARY KEY (cart_id, product_id)
);
CREATE TABLE IF NOT EXISTS recognition_candidates (
  id TEXT PRIMARY KEY,
  scan_id TEXT NOT NULL,
  product_id INTEGER NOT NULL REFERENCES products(id),
  confidence DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  position TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending','confirmed','dismissed','expired')),
  expires_at DOUBLE PRECISION NOT NULL
);
CREATE TABLE IF NOT EXISTS processed_requests (
  cart_id TEXT NOT NULL REFERENCES carts(id),
  request_key TEXT NOT NULL,
  payload TEXT NOT NULL,
  response TEXT NOT NULL,
  PRIMARY KEY (cart_id, request_key)
);
