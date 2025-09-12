#!/bin/bash

# WoW Auction House Data Update Script
# This script fetches new auction data and runs daily cleanup

set -e  # Exit on any error

echo "🚀 Starting WoW Auction House data update..."
echo "=============================================="

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Run the fetcher to get new auction data
echo ""
echo "📥 Fetching new auction data..."
echo "-------------------------------"
python -m backend.fetcher

# Check if fetcher was successful
if [ $? -eq 0 ]; then
    echo "✅ Auction data fetch completed successfully!"
else
    echo "❌ Auction data fetch failed!"
    exit 1
fi

# Run daily cleanup
echo ""
echo "🧹 Running daily cleanup..."
echo "---------------------------"
python -m backend.cleanup daily

# Check if cleanup was successful
if [ $? -eq 0 ]; then
    echo "✅ Daily cleanup completed successfully!"
else
    echo "❌ Daily cleanup failed!"
    exit 1
fi

# Show final statistics
echo ""
echo "📊 Final database statistics:"
echo "-----------------------------"
python -m backend.cleanup stats

echo ""
echo "🎉 Data update completed successfully!"
echo "======================================"
