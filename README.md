<p align="center"><img src="https://raw.githubusercontent.com/anfederico/Stockeye/master/media/Stockeye.png" width=40%></p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[![PyPI version](https://badge.fury.io/py/stockeye.svg)](https://badge.fury.io/py/stockeye)
[![Build Status](https://travis-ci.org/anfederico/Stockeye.svg?branch=master)](https://travis-ci.org/anfederico/Stockeye)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)
[![GitHub Issues](https://img.shields.io/github/issues/anfederico/Stockeye.svg)](https://github.com/anfederico/stockeye/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)
[![License](https://img.shields.io/badge/license-MIT%20License-brightgreen.svg)](https://opensource.org/licenses/MIT)

## Install
```python
pip install stockeye
```

## Download Corpus
```python
stockeye-corpus
or
python -m nltk.downloader stopwords
python -m nltk.downloader punkt
```
## Code Examples

#### Watch News

```python
from stockeye import watch

# This gives your script access to your gmail account, may want to use a throwaway
# Make sure "Allow Access To Less Secure Apps" is turned on in gmail settings
# If using a throwaway, adjust email_to to your real email!

email_self = 'youremail@gmail.com'
email_password = 'yourpassword'    
email_from = email_self     
email_to = email_self
credentials = [email_self, email_password, email_from, email_to]


# Stocks to monitor (add up to 100 with each run)

ticks = ['MSFT', 'PFE', 'BOX', 'MNST', 'LLY', 'AAPL',
         'BBY', 'TSLA', 'WFG', 'AMZN', 'JNJ', 'NFLX', 
         'BIIB', 'GE', 'GILD', 'SHAK', 'VRTX', 'CMG']


# Properties included in statistics report (see below for more)

properties = ['Open',
              'DaysLow', 
              'DaysHigh', 
              'Ask', 
              'PercentChange', 
              'Volume', 
              'ShortRatio', 
              'DividendYield', 
              'PERatio']


threshold = 3      # Number of recent articles published before an email is sent (default = 3)
hourspast = 18     # Define....recent (default = 18)
sentences = 3      # Length of summary generated for each article (deafult = 3)
firstlast = False  # Include first/last sentence of the artice in its summary (default = False)


watch(credentials, ticks, properties, threshold, hourspast, sentences, firstlast)
```

```text
This run will take approximately 9 minutes
Finding news for MSFT
Finding news for PFE
Finding news for BOX
Finding news for MNST
Finding news for LLY
Finding news for AAPL
Finding news for BBY
Finding news for TSLA
Finding news for WFG
Finding news for AMZN
Finding news for JNJ
Finding news for NFLX
Finding news for BIIB
Finding news for GE
Finding news for GILD
Finding news for SHAK
Finding news for VRTX
Finding news for CMG
```
#### Email Example
<p align="center"><img src="https://raw.githubusercontent.com/anfederico/Stockeye/master/media/NewsAlert.png" width=90%></p>

#### More Properties
```text
- AfterHoursChangeRealtime                       - HoldingsValueRealtime                                
- AnnualizedGain                                 - LastTradeDate                                        
- Ask                                            - LastTradePriceOnly                                   
- AskRealtime                                    - LastTradeRealtimeWithTime                            
- AverageDailyVolume                             - LastTradeTime                                        
- Bid                                            - LastTradeWithTime                                    
- BidRealtime                                    - LowLimit                                             
- BookValue                                      - MarketCapRealtime                                    
- Change                                         - MarketCapitalization                                 
- ChangeFromFiftydayMovingAverage                - MoreInfo                                             
- ChangeFromTwoHundreddayMovingAverage           - Name                                                 
- ChangeFromYearHigh                             - Notes                                                
- ChangeFromYearLow                              - OneyrTargetPrice                                     
- ChangePercentRealtime                          - Open                                                 
- ChangeRealtime                                 - OrderBookRealtime                                    
- ChangeinPercent                                - PEGRatio                                             
- Commission                                     - PERatio                                              
- Currency                                       - PERatioRealtime                                      
- DaysHigh                                       - PercentChangeFromYearHigh                            
- DaysLow                                        - PercentChange                                        
- DaysRange                                      - PercentChangeFromFiftydayMovingAverage               
- DaysRangeRealtime                              - PercentChangeFromTwoHundreddayMovingAverage          
- DaysValueChange                                - PercentChangeFromYearLow                             
- DaysValueChangeRealtime                        - PreviousClose                                        
- DividendPayDate                                - PriceBook                                            
- DividendShare                                  - PriceEPSEstimateCurrentYear                          
- DividendYield                                  - PriceEPSEstimateNextYear                             
- EBITDA                                         - PricePaid                                            
- EPSEstimateCurrentYear                         - PriceSales                                           
- EPSEstimateNextQuarter                         - SharesOwned                                          
- EPSEstimateNextYear                            - ShortRatio                                           
- EarningsShare                                  - StockExchange                                        
- ExDividendDate                                 - Symbol                                               
- FiftydayMovingAverage                          - TickerTrend                                          
- HighLimit                                      - TradeDate                                            
- HoldingsGain                                   - TwoHundreddayMovingAverage                           
- HoldingsGainPercent                            - Volume                                               
- HoldingsGainPercentRealtime                    - YearHigh                                             
- HoldingsGainRealtime                           - YearLow                                              
- HoldingsValue                                  - YearRange  
```
