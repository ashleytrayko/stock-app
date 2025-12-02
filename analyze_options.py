import yfinance as yf
import pandas as pd
from datetime import datetime

googl = yf.Ticker('GOOGL')
current_price = googl.history(period='1d')['Close'].iloc[-1]
print(f'현재 GOOGL 주가: ${current_price:.2f}\n')

# 가장 가까운 만기일
expiry = googl.options[0]
print(f'분석 대상 만기일: {expiry}\n')

option_chain = googl.option_chain(expiry)
calls = option_chain.calls
puts = option_chain.puts

# 1. Max Pain 분석 (Open Interest 기반)
print('=== 1. Max Pain 분석 ===')
print('Open Interest가 가장 많은 행사가 = 만기일에 도달할 가능성이 높은 가격\n')

# 각 행사가별 총 Open Interest 계산
strikes = pd.concat([calls[['strike', 'openInterest']], puts[['strike', 'openInterest']]],
                     keys=['call', 'put'])
strike_oi = strikes.groupby('strike')['openInterest'].sum().sort_values(ascending=False)

print('Open Interest 상위 5개 행사가:')
print(strike_oi.head())

max_pain_strike = strike_oi.idxmax()
print(f'\n→ Max Pain 예상 가격: ${max_pain_strike:.2f}')
price_diff = ((max_pain_strike/current_price - 1) * 100)
print(f'   (현재가 대비: {price_diff:+.2f}%)\n')

# 2. Put-Call Ratio (PCR)
print('=== 2. Put-Call Ratio (PCR) ===')
total_call_oi = calls['openInterest'].sum()
total_put_oi = puts['openInterest'].sum()
pcr = total_put_oi / total_call_oi

print(f'총 콜 Open Interest: {total_call_oi:,}')
print(f'총 풋 Open Interest: {total_put_oi:,}')
print(f'Put-Call Ratio: {pcr:.2f}')
print(f'\n해석:')
if pcr > 1:
    print(f'  - PCR > 1: 풋 옵션이 많음 → 하락 예상 또는 헤지 목적')
elif pcr < 0.7:
    print(f'  - PCR < 0.7: 콜 옵션이 많음 → 상승 예상')
else:
    print(f'  - 0.7 < PCR < 1: 중립적\n')

# 3. ATM (At-The-Money) Implied Volatility
print('=== 3. ATM Implied Volatility (IV) ===')
print('현재 가격에 가장 가까운 행사가의 변동성 기대치\n')

# 현재가에 가장 가까운 행사가 찾기
calls['strike_diff'] = abs(calls['strike'] - current_price)
atm_call = calls.loc[calls['strike_diff'].idxmin()]

puts['strike_diff'] = abs(puts['strike'] - current_price)
atm_put = puts.loc[puts['strike_diff'].idxmin()]

print(f'ATM Strike: ${atm_call["strike"]:.2f}')
print(f'ATM Call IV: {atm_call["impliedVolatility"]:.2%}')
print(f'ATM Put IV: {atm_put["impliedVolatility"]:.2%}')
avg_iv = (atm_call['impliedVolatility'] + atm_put['impliedVolatility']) / 2
print(f'평균 IV: {avg_iv:.2%}')

print(f'\n해석:')
print(f'  - IV가 높을수록 큰 가격 변동 예상')
print(f'  - IV가 낮을수록 안정적인 흐름 예상')
