-- Database schema for WoW Auction House data

-- Auctions table to store auction house data
CREATE TABLE IF NOT EXISTS auctions (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    buyout BIGINT NOT NULL,  -- Price in copper
    time_left TEXT NOT NULL, -- 'SHORT', 'MEDIUM', 'LONG', 'VERY_LONG'
    last_seen TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Items table to cache item information
CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    icon_url TEXT
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_auctions_item_id ON auctions(item_id);
CREATE INDEX IF NOT EXISTS idx_auctions_last_seen ON auctions(last_seen);
CREATE INDEX IF NOT EXISTS idx_auctions_buyout ON auctions(buyout);

-- Comments for documentation
COMMENT ON TABLE auctions IS 'Stores auction house data from WoW API';
COMMENT ON TABLE items IS 'Caches item names and icons to avoid repeated API calls';
COMMENT ON COLUMN auctions.buyout IS 'Price in copper (1 gold = 10000 copper)';
COMMENT ON COLUMN auctions.time_left IS 'Auction duration: SHORT, MEDIUM, LONG, VERY_LONG';
