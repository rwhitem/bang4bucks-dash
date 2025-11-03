import streamlit as st, pandas as pd, numpy as np
st.set_page_config(page_title='Bang4Bucks Dash', layout='wide')
APP_TITLE='💥 Bang4Bucks Dash'
CATEGORIES=['Gas','Groceries','Internet','Utilities','Restaurants','Travel','Transit','Drugstores','Streaming','Wholesale','Everything Else']
@st.cache_data
def load_csv(p):
    try:
        return pd.read_csv(p) if isinstance(p,str) else pd.read_csv(p)
    except: return pd.DataFrame()
def eff(m,c):
    if m.empty or c.empty or 'Card Name' not in m.columns or ('Card Name' not in c.columns and 'Card' not in c.columns) or 'Point Value (¢)' not in c.columns: return pd.DataFrame()
    v=c.rename(columns={'Card':'Card Name'}) if 'Card' in c.columns else c
    d=m.merge(v[['Card Name','Point Value (¢)']],on='Card Name',how='inner')
    r=d[['Card Name']].copy()
    for cat in [x for x in d.columns if x in CATEGORIES]: r[cat]=d[cat]*(d['Point Value (¢)']/100.0)
    return r
def best(e):
    if e.empty: return pd.DataFrame()
    rows=[]
    for cat in [x for x in e.columns if x in CATEGORIES]:
        i=e[cat].idxmax(); rows.append({'Category':cat,'Best Card':e.loc[i,'Card Name'],'Best %':round(float(e.loc[i,cat])*100,2)})
    return pd.DataFrame(rows)
def pick(amt,cat,e):
    if e.empty or cat not in e.columns: return None
    t=e[['Card Name',cat]].copy(); t['Value_$']=amt*t[cat]; t=t.sort_values(['Value_$','Card Name'],ascending=[False,True]).head(5); t['Effective_%']=(t[cat]*100).round(2); t['Value_$']=t['Value_$'].round(2); return t[['Card Name','Effective_%','Value_$']]
def heloc(chunk,apr,months,main_rate,main_bal,years=None):
    heloc_cost=chunk*(apr/12.0)*months; years=5.0 if not years else max(0.5,float(years)); saved=chunk*main_rate*years; return {'HELOC_interest_cost':round(heloc_cost,2),'Main_interest_saved_est':round(saved,2),'Net_benefit_est':round(saved-heloc_cost,2),'Repay_months':months}
st.sidebar.title('Bang4Bucks Dash')
nav=st.sidebar.radio('Go to',['Overview','Income','Expenses','Rewards Optimizer','Investments','Net Worth','Debt Paydown','Ask Bang (AI)'],index=0)
income=load_csv(st.sidebar.file_uploader('Income CSV',type=['csv'],key='income') or 'data/income.csv')
expenses=load_csv(st.sidebar.file_uploader('Expenses CSV',type=['csv'],key='expenses') or 'data/expenses.csv')
cards=load_csv(st.sidebar.file_uploader('Rewards Cards CSV',type=['csv'],key='cards') or 'data/rewards_cards.csv')
mult=load_csv(st.sidebar.file_uploader('Rewards Multipliers CSV',type=['csv'],key='mult') or 'data/rewards_multipliers.csv')
holds=load_csv(st.sidebar.file_uploader('Investments Holdings CSV',type=['csv'],key='hold') or 'data/investments_holdings.csv')
tx=load_csv(st.sidebar.file_uploader('Investments Transactions CSV',type=['csv'],key='tx') or 'data/investments_transactions.csv')
assets=load_csv(st.sidebar.file_uploader('Net Worth Assets CSV',type=['csv'],key='assets') or 'data/networth_assets.csv')
liabs=load_csv(st.sidebar.file_uploader('Net Worth Liabilities CSV',type=['csv'],key='liabs') or 'data/networth_liabilities.csv')
debts=load_csv(st.sidebar.file_uploader('Debts CSV',type=['csv'],key='debts') or 'data/debts.csv')
heloc_df=load_csv(st.sidebar.file_uploader('HELOC Strategy CSV',type=['csv'],key='heloc') or 'data/heloc_strategy.csv')
st.title(APP_TITLE)
if nav=='Overview':
    ti=float(income['Amount'].sum()) if 'Amount' in income.columns else 0.0; te=float(expenses['Amount'].sum()) if 'Amount' in expenses.columns else 0.0; net=ti-te
    st.metric('Total Income',f'${ti:,.2f}'); st.metric('Total Expenses',f'${te:,.2f}'); st.metric('Net',f'${net:,.2f}',delta=f'{(net/ti*100 if ti else 0):.1f}% of income')
    st.divider(); e=eff(mult,cards); st.markdown('#### Rewards snapshot'); st.dataframe(best(e) if not e.empty else pd.DataFrame({'Tip':['Add your cards & multipliers']}),use_container_width=True)
elif nav=='Income':
    if 'Date' in income.columns: income['Date']=pd.to_datetime(income['Date'],errors='coerce'); st.dataframe(income.sort_values('Date'),use_container_width=True)
elif nav=='Expenses':
    if 'Date' in expenses.columns: expenses['Date']=pd.to_datetime(expenses['Date'],errors='coerce'); st.dataframe(expenses.sort_values('Date'),use_container_width=True)
elif nav=='Rewards Optimizer':
    st.dataframe(cards,use_container_width=True); st.dataframe(mult,use_container_width=True); e=eff(mult,cards)
    if not e.empty:
        show=e.copy(); 
        for c in [c for c in show.columns if c in CATEGORIES]: show[c]=(show[c]*100).round(2)
        st.dataframe(show,use_container_width=True); st.dataframe(best(e),use_container_width=True)
        amt=st.number_input('Purchase amount ($)',1.0,100000.0,120.0,1.0); cat=st.selectbox('Category',CATEGORIES,index=4)
        if st.button('Find best card'): p=pick(amt,cat,e); st.dataframe(p,use_container_width=True) if p is not None else st.info('No match')
elif nav=='Investments':
    if not holds.empty:
        h=holds.copy(); h['Market Value']=h.get('Quantity',0)*h.get('Current Price',0); h['Unrealized Gain $']=h['Market Value']-h.get('Cost Basis',0); h['Unrealized Gain %']=np.where(h.get('Cost Basis',0)>0,100*h['Unrealized Gain $']/h['Cost Basis'],np.nan); st.dataframe(h,use_container_width=True)
elif nav=='Net Worth':
    a=float(assets['Value'].sum()) if 'Value' in assets.columns else 0.0; l=float(liabs['Balance'].sum()) if 'Balance' in liabs.columns else 0.0; st.metric('Total Assets',f'${a:,.2f}'); st.metric('Total Liabilities',f'${l:,.2f}'); st.metric('Net Worth',f'${(a-l):,.2f}'); st.dataframe(assets,use_container_width=True); st.dataframe(liabs,use_container_width=True)
elif nav=='Debt Paydown':
    st.dataframe(debts,use_container_width=True); st.dataframe(heloc_df,use_container_width=True); chunk=st.number_input('Chunk amount ($)',100.0,1e6,5000.0,100.0); apr=st.number_input('HELOC/PLOC APR (%)',0.0,100.0,9.0,0.1)/100.0; months=int(st.number_input('Repay months',1,360,3,1)); main_bal=st.number_input('Main debt balance ($)',1000.0,1e9,65000.0,100.0); main_rate=st.number_input('Main debt APR (%)',0.0,100.0,6.0,0.1)/100.0; years=st.number_input('Remaining term (years) (optional)',0.0,100.0,0.0,0.5); years=None if years==0 else years
    if st.button('Simulate chunk'): r=heloc(chunk,apr,months,main_rate,main_bal,years); st.write(f"**HELOC interest:** ${r['HELOC_interest_cost']:,.2f}"); st.write(f"**Main-loan interest saved (est):** ${r['Main_interest_saved_est']:,.2f}"); st.success(f"**Net benefit (est):** ${r['Net_benefit_est']:,.2f}")
elif nav=='Ask Bang (AI)':
    st.caption('Tier-1 AI/web lookups are off until you add API keys to .streamlit/secrets.toml.'); st.write('Try: "Best card for $120 at restaurants" or "HELOC chunk $5k for 3 months vs mortgage 6%"')
st.caption('© Bang4Bucks Dash — informational only.')
