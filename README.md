# WoW Auction House Data Tracker

A comprehensive World of Warcraft auction house data tracking and analysis system that fetches real-time auction data from Blizzard's API, stores it in PostgreSQL, and provides a modern web interface for price analysis and trends.

## 🌟 Features

### Data Collection
- **Real-time Auction Data**: Fetches current auction house data from Blizzard's EU API
- **Commodity Tracking**: Supports both regular auctions and commodity auctions
- **Historical Data**: Maintains price history for trend analysis and market insights
- **Automated Updates**: Scheduled data fetching with cleanup and maintenance

### Web Interface
- **Modern UI**: Clean, responsive design with search functionality
- **Item Search**: Real-time search with autocomplete dropdown
- **Price Analytics**: Interactive charts showing price trends over time
- **Tier Detection**: Automatic detection and display of item tiers (T1, T2, T3)
- **Detailed Views**: Individual item pages with comprehensive statistics

### Data Management
- **PostgreSQL Database**: Robust data storage with proper indexing
- **Data Cleanup**: Automated outlier removal and data optimization
- **Backup System**: Comprehensive backup and restore functionality
- **Performance Optimization**: Efficient queries and caching

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **API Layer**: FastAPI-based REST API with CORS support
- **Data Fetching**: Blizzard API integration with OAuth2 authentication
- **Database Layer**: PostgreSQL with optimized schemas and indexes
- **Processing Pipeline**: Data cleaning, validation, and storage
- **Maintenance Tools**: Automated cleanup and backup utilities

### Frontend (Vanilla JavaScript/HTML/CSS)
- **Search Interface**: Real-time search with dropdown suggestions
- **Data Visualization**: Chart.js integration for price trends
- **Responsive Design**: Mobile-friendly interface
- **Interactive Elements**: Click-to-detail navigation and time filters

### Database Schema
- **auctions**: Current auction data (last hour)
- **auction_history**: Historical data for analytics
- **items**: Item metadata cache (names, icons)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Blizzard API credentials (Client ID and Secret)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wowauction
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   BLIZZARD_CLIENT_ID=your_client_id
   BLIZZARD_SECRET=your_secret
   DB_URI=postgresql://username:password@localhost:5432/wowauction
   ```

5. **Set up database**
   ```bash
   # Create database
   createdb wowauction
   
   # Run schema
   psql wowauction < backend/db/models.sql
   ```

6. **Start the application**
   ```bash
   # Start the API server
   uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the web interface**
   Open your browser to `http://localhost:8000`

## 📊 Usage

### Data Collection

**Manual Data Fetch**
```bash
# Fetch new auction data
python -m backend.fetcher

# Run automated update script (includes cleanup)
./update_data.sh
```

**Automated Updates**
Set up a cron job to run `update_data.sh` regularly:
```bash
# Run every hour
0 * * * * /path/to/wowauction/update_data.sh
```

### Data Management

**Cleanup Operations**
```bash
# Remove outliers
python -m backend.cleanup outliers

# Daily data cleanup (keep lowest price per day per item)
python -m backend.cleanup daily

# Remove old data (keep last 30 days)
python -m backend.cleanup old 30

# Run all cleanup operations
python -m backend.cleanup all

# View database statistics
python -m backend.cleanup stats
```

**Backup Management**
```bash
# Create backup
python -m backend.cleanup backup

# List available backups
python -m backend.cleanup backups

# Restore from backup
python -m backend.cleanup restore backup_table_name

# Delete backup
python -m backend.cleanup delete-backup backup_table_name
```

### Web Interface

1. **Search Items**: Use the search bar to find items by name
2. **View Results**: Browse current auction prices and quantities
3. **Item Details**: Click on any item to view detailed analytics
4. **Price Trends**: Analyze price history with interactive charts
5. **Time Filters**: Switch between different time periods (24h, 48h, 1 week, 1 month, all time)

## 🔧 Configuration

### Environment Variables
- `BLIZZARD_CLIENT_ID`: Your Blizzard API client ID
- `BLIZZARD_SECRET`: Your Blizzard API secret
- `DB_URI`: PostgreSQL connection string

### API Configuration
The system is configured for EU servers by default. To change regions, modify:
- `CONNECTED_REALM_ID` in `backend/fetch_auctions.py`
- `BASE_URL` and `NAMESPACE` for different regions

### Database Tuning
The system includes optimized indexes for performance. For large datasets, consider:
- Regular VACUUM and ANALYZE operations
- Partitioning the `auction_history` table by date
- Adjusting PostgreSQL memory settings

## 📁 Project Structure

```
wowauction/
├── backend/                 # Python backend
│   ├── api.py              # FastAPI application
│   ├── auth.py             # Blizzard API authentication
│   ├── config.py           # Configuration management
│   ├── fetcher.py          # Main data fetching orchestrator
│   ├── fetch_auctions.py   # Regular auction data fetching
│   ├── fetch_commodities.py # Commodity auction fetching
│   ├── process_data.py     # Data processing and cleaning
│   ├── to_database.py      # Database operations
│   ├── cleanup.py          # Data maintenance utilities
│   ├── tier_detector.py    # Item tier detection
│   ├── items.py            # Item metadata management
│   └── db/
│       └── models.sql      # Database schema
├── web/                    # Frontend files
│   ├── index.html          # Main search interface
│   ├── item.html           # Item detail page
│   ├── script.js           # Main page JavaScript
│   ├── item.js             # Item detail page JavaScript
│   └── style.css           # Styling (embedded in HTML)
├── venv/                   # Python virtual environment
├── requirements.txt        # Python dependencies
├── update_data.sh          # Automated update script
└── README.md              # This file
```

## 🔍 API Endpoints

### Public Endpoints
- `GET /` - Main web interface
- `GET /item.html` - Item detail page
- `GET /api/health` - Health check

### Data Endpoints
- `GET /api/auctions` - Get auction data (supports query and item_id parameters)
- `GET /api/auctions/history` - Get historical auction data
- `GET /api/auctions/trends` - Get price trends for specific items
- `GET /api/items` - Get all items
- `GET /api/items/search` - Search items with autocomplete

## 🛠️ Development

### Adding New Features
1. **Backend**: Add new endpoints in `backend/api.py`
2. **Frontend**: Update JavaScript files in `web/` directory
3. **Database**: Modify schema in `backend/db/models.sql`

### Testing
```bash
# Test API endpoints
curl http://localhost:8000/api/health

# Test data fetching
python -m backend.fetcher

# Test cleanup operations
python -m backend.cleanup preview
```

### Performance Monitoring
- Monitor database size with `python -m backend.cleanup stats`
- Check API response times in browser developer tools
- Review PostgreSQL logs for slow queries

## 📈 Data Insights

The system provides valuable insights into WoW's economy:
- **Price Trends**: Track how item prices change over time
- **Market Volume**: Monitor auction quantities and frequency
- **Tier Analysis**: Understand pricing differences between item tiers
- **Historical Data**: Analyze long-term market patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and personal use. Please respect Blizzard's API terms of service.

## ⚠️ Disclaimer

This tool is not affiliated with Blizzard Entertainment. World of Warcraft is a trademark of Blizzard Entertainment, Inc. Use at your own risk and in accordance with Blizzard's terms of service.

## 🆘 Troubleshooting

### Common Issues

**API Authentication Errors**
- Verify your Blizzard API credentials
- Check if your API key has the required permissions
- Ensure the credentials are correctly set in the `.env` file

**Database Connection Issues**
- Verify PostgreSQL is running
- Check the `DB_URI` connection string
- Ensure the database exists and is accessible

**Data Fetching Failures**
- Check your internet connection
- Verify Blizzard API is accessible
- Review the console output for specific error messages

**Performance Issues**
- Run cleanup operations to optimize the database
- Check database size and consider archiving old data
- Monitor system resources during data fetching

### Getting Help
- Check the console output for detailed error messages
- Review the database logs for connection issues
- Ensure all dependencies are properly installed
- Verify environment variables are correctly configured