# Texas Election Results Data Collection

This project collects statewide and legislative election results for Texas from 2014-2024.

## Election Types Covered

- **Statewide Races**:
  - Presidential (2016, 2020, 2024)
  - U.S. Senate
  - Governor
  - Lieutenant Governor
  - Attorney General
  - Comptroller
  - Land Commissioner
  - Agriculture Commissioner
  - Railroad Commissioner

- **Legislative Races**:
  - U.S. Congressional (36-38 districts)
  - Texas State Senate (31 districts)
  - Texas State House (150 districts)

## Data Sources

### Official Sources

1. **Texas Secretary of State** - Official election results
   - Website: https://elections.sos.state.tx.us/
   - Historical data: https://www.sos.state.tx.us/elections/historical/

2. **Texas Capitol Data Portal** - Comprehensive datasets
   - Website: https://data.capitol.texas.gov/topic/about/elections
   - Provides downloadable election data files

### Important Note

Data from the Capitol Data Portal may have small differences from official results. Always verify with the Texas Secretary of State for official results.

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Data Collection Script

```bash
python collect_texas_elections.py
```

## Current Status

The script currently creates a **framework with placeholder data**. To get actual election results, you need to:

### Option 1: Manual Download (Recommended for Official Data)

1. Visit the [Texas Secretary of State Historical Elections page](https://www.sos.state.tx.us/elections/historical/)
2. Download election results by year and race type
3. Place downloaded files in the `raw_data/` directory
4. The script can be modified to parse these downloaded files

### Option 2: Capitol Data Portal

1. Visit [Texas Capitol Data Portal - Elections](https://data.capitol.texas.gov/topic/about/elections)
2. Download the Comprehensive Election Datasets (compressed files)
3. Extract and process the data programmatically

### Option 3: Web Scraping (Advanced)

Modify the script to scrape data from:
- https://elections.sos.state.tx.us/index.htm
- Individual county election websites

**Note**: Web scraping should be done respectfully with appropriate delays and should comply with the website's terms of service.

## Output Files

The script generates CSV files in the `election_data/` directory:

- `texas_statewide_results.csv` - All statewide races
- `texas_congressional_results.csv` - U.S. House races
- `texas_state_senate_results.csv` - State Senate races
- `texas_state_house_results.csv` - State House races

## CSV Structure

### Statewide Results
```csv
year,office,candidate,party,votes,percentage,source_url
```

### Legislative Results
```csv
year,office,district,candidate,party,votes,percentage
```

## Next Steps

To complete the data collection:

1. **Review the data sources** and determine the best approach for your needs
2. **Download historical data** from Texas SOS or Capitol Data Portal
3. **Enhance the script** to parse the downloaded data files
4. **Validate results** against official sources

## Resources

- [Texas Secretary of State Elections](https://www.sos.state.tx.us/elections/)
- [Texas Capitol Data Portal](https://data.capitol.texas.gov/topic/about/elections)
- [Election Results Archive](https://www.sos.state.tx.us/elections/historical/elections-results-archive.shtml)

## License

This is a data collection tool for public election information. Please cite official sources when using the data.
