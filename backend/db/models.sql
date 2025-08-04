-- Database schema for WoW Auction House data

-- Current auctions table (last hour only)
CREATE TABLE IF NOT EXISTS auctions (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    buyout BIGINT NOT NULL,  -- Price in copper
    time_left TEXT NOT NULL, -- 'SHORT', 'MEDIUM', 'LONG', 'VERY_LONG'
    last_seen TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Historical auctions table (for analytics and trends)
CREATE TABLE IF NOT EXISTS auction_history (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    buyout BIGINT NOT NULL,  -- Price in copper
    time_left TEXT NOT NULL, -- 'SHORT', 'MEDIUM', 'LONG', 'VERY_LONG'
    snapshot_time TIMESTAMP NOT NULL, -- When this snapshot was taken
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
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

CREATE INDEX IF NOT EXISTS idx_auction_history_item_id ON auction_history(item_id);
CREATE INDEX IF NOT EXISTS idx_auction_history_snapshot_time ON auction_history(snapshot_time);
CREATE INDEX IF NOT EXISTS idx_auction_history_buyout ON auction_history(buyout);

-- Comments for documentation
COMMENT ON TABLE auctions IS 'Stores current auction house data (last hour only)';
COMMENT ON TABLE auction_history IS 'Stores historical auction data for analytics and trends';
COMMENT ON TABLE items IS 'Caches item names and icons to avoid repeated API calls';
COMMENT ON COLUMN auctions.buyout IS 'Price in copper (1 gold = 10000 copper)';
COMMENT ON COLUMN auctions.time_left IS 'Auction duration: SHORT, MEDIUM, LONG, VERY_LONG';
COMMENT ON COLUMN auction_history.snapshot_time IS 'Timestamp when this auction snapshot was taken';
