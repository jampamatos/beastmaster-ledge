from preswald import checkbox, connect, get_df, plotly, sidebar, slider, table, text, Workflow
import plotly.express as px
from fractions import Fraction
import pandas as pd

# Helper to parse CR into numeric
def parse_cr(cr):
    if isinstance(cr, str) and '/' in cr:
        return float(Fraction(cr))
    try:
        return float(cr)
    except:
        return None

SHOW_COLS = ['name','cr','type','size','ac','hp','speed','align','legendary']

# Boilerplate: Sidebar, Title & Data Load
sidebar(defaultopen=True)
text('# Beastmaster’s Ledge 📜')
text('***Lo, adventurer! Thou hast opened the Tome of Beasts…***')

connect()
df = get_df('monsters')

# Compute numeric fields once
df['cr_num']        = df['cr'].apply(parse_cr)
df['survivability'] = df['ac'] * df['hp']

# (Mezzo-)Interactive Filters
text("## Prologue: Scrying the Beast Scroll")
text("*Before we embark upon our deeper studies, filter these annals to your taste—adjust the scales of might and endurance…*")

min_ac = slider(
    "Min AC", 
    min_val=int(df["ac"].min()), 
    max_val=int(df["ac"].max()), 
    default=int(df["ac"].min()), 
    step=1, 
    size=0.25
)
max_ac = slider(
    "Max AC", 
    min_val=int(df["ac"].min()), 
    max_val=int(df["ac"].max()), 
    default=int(df["ac"].max()), 
    step=1, 
    size=0.25
)
min_hp = slider(
    "Min HP", 
    min_val=int(df["hp"].min()), 
    max_val=int(df["hp"].max()), 
    default=int(df["hp"].min()), 
    step=1, 
    size=0.25
)
max_hp = slider(
    "Max HP", 
    min_val=int(df["hp"].min()), 
    max_val=int(df["hp"].max()), 
    default=int(df["hp"].max()), 
    step=1, 
    size=0.25
)
min_cr = slider(
    "Min CR", 
    min_val=0.0, 
    max_val=df["cr_num"].max(), 
    default=0.0, 
    step=0.5, 
    size=0.25
)
max_cr = slider(
    "Max CR", 
    min_val=0.0, 
    max_val=df["cr_num"].max(), 
    default=df["cr_num"].max(), 
    step=0.5, 
    size=0.25
)
legendary_only = checkbox(
    "Legendary Only", 
    default=False, 
    size=0.25
)

# Apply interactive filters
df_filt = df.copy()
df_filt = df_filt[
    (df_filt["ac"]    >= min_ac) &
    (df_filt["ac"]    <= max_ac) &
    (df_filt["hp"]    >= min_hp) &
    (df_filt["hp"]    <= max_hp) &
    (df_filt["cr_num"]>= min_cr) &
    (df_filt["cr_num"]<= max_cr)
]
if legendary_only:
    df_filt = df_filt[df_filt["legendary"] == "Legendary"]

# Display filtered table
if df_filt.empty:
    text("*No creatures match these arcane parameters…*")
else:
    table(df_filt[SHOW_COLS], title="Filtered Bestiary")

# Chapter I: Survivability
text('## Chapter I: The Measure of Endurance')
text('*Behold, gentle scholar, the hardy and the frail alike—here we quantify '
     'each creature’s fortitude as the product of its defenses and vitality…*')
sv = (
    df
    .groupby('type', as_index=False)
    .agg(survivability=('survivability', 'mean'))
    .sort_values('survivability', ascending=False)
)
fig_sv = px.bar(
    sv, x='type', y='survivability',
    title='Average Survivability (AC × HP) by Type',
    labels={'type':'Creature Type','survivability':'Avg. Survivability'}
)
plotly(fig_sv)

# Chapter II: Stat Profiles by Size
text('## Chapter II: The Stat Profiles by Size')
text('*Next, we turn our gaze to the varied statures of these denizens—'
     'from the diminutive to the gargantuan, their abilities revealed in a radial tableau…*')
stats = ['str','dex','con','int','wis','cha']
radar_df = (
    df
    .dropna(subset=stats)
    .groupby('size')[stats]
    .mean()
    .reset_index()
    .melt(id_vars='size', var_name='stat', value_name='avg')
)
fig_radar = px.line_polar(
    radar_df, r='avg', theta='stat', color='size',
    line_close=True,
    title='Average Ability Scores by Size Category'
)
plotly(fig_radar)

# Chapter III: Alignment & Challenge
text('## Chapter III: Alignment & Challenge')
text('*Let us peer into the hearts of beasts and note how their moral alignments '
     'correlate with the perils they pose…*')
alig_df = df.dropna(subset=['align','cr_num'])
fig_align = px.violin(
    alig_df, x='align', y='cr_num',
    title='Challenge Rating by Alignment',
    labels={'align':'Alignment','cr_num':'Challenge Rating'}
)
plotly(fig_align)

# Chapter IV: Sourcebook Lore
text('## Chapter IV: Sourcebook Lore')
text('*From tomes old and scrolls newly penned, behold which grimoire '
     'yields the greatest variety of horrors…*')
src = (
    df
    .fillna({'source':'Unknown'})
    .groupby('source', as_index=False)
    .agg(count=('name','count'))
    .sort_values('count', ascending=False)
)
fig_src = px.pie(
    src, names='source', values='count',
    title='Distribution of Monsters Across Sourcebooks',
    hole=0.4
)
plotly(fig_src)

#  Chapter V: Legendary vs. Common
text('## Chapter V: Legendary vs. Common')
text('*Mark well the distinction betwixt those of famed legend and the common multitude—'
     'their might measured in wounds and resilience…*')
leg_df = df.assign(category=df['legendary'].fillna('Common'))
fig_cmp = px.box(
    leg_df, x='category', y=['hp','ac'],
    title='HP & AC: Legendary vs. Common Creatures',
    labels={'value':'Stat Value','category':'Category','variable':'Measure'}
)
plotly(fig_cmp)

# Chapter VI: Type Frequency by Size
text('## Chapter VI: Type Frequency by Size')
text('*Observe now how each size class harbors certain creatures most abundantly—'
     'a heatmap of form and function…*')
top10 = df['type'].value_counts().nlargest(10).index
freq = (
    df[df['type'].isin(top10)]
    .groupby(['size','type'], as_index=False)
    .agg(count=('name','count'))
    .pivot(index='size', columns='type', values='count')
    .fillna(0)
)
fig_heat = px.imshow(
    freq, text_auto=True,
    title='Heatmap of Top 10 Types Across Sizes',
    labels={'x':'Creature Type','y':'Size','color':'Count'}
)
plotly(fig_heat)

# Chapter VII: Correlations
text('## Chapter VII: Correlations of Core Stats')
text('*At last, we unveil the hidden bonds that tie a creature’s form to its function—'
     'a matrix of mutual influence…*')
numcols = ['cr_num','ac','hp','str','dex','con','int','wis','cha']
corr = df[numcols].corr()
fig_corr = px.imshow(
    corr, text_auto='.2f',
    title='Correlation Matrix of CR, AC, HP and Abilities'
)
plotly(fig_corr)

# Chapter VIII: Top & Bottom Survivability
text('## Chapter VIII: Top & Bottom Survivors')
text('*Finally, behold the mightiest of the mighty and the frailest of the frail—'
     'a roll call of triumph and tragedy…*')
top10 = df.nlargest(10, 'survivability')[SHOW_COLS + ['survivability']]
bot10 = df.nsmallest(10, 'survivability')[SHOW_COLS + ['survivability']]
text('### Top 10 Most Durable Creatures')
table(top10, title='Top 10 Survivors')
text('### Top 10 Least Durable Creatures')
table(bot10, title='Bottom 10 Survivors')

# Epilogue
text('## Epilogue')
text('*Thus ends our scholarly odyssey through the Beastmaster’s Ledge. '
     'Yet heed this warning: knowledge of these dread creatures is not without peril. '
     'Let not your curiosity stray too far into forbidden lore…*\n\n'
     'That is to say, if you are a player, **there may be spoilers**. 🐉')
text('Farewell, brave adventurer! May your journeys be filled with fortune and glory!')
