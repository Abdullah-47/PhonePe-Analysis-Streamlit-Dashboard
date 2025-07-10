import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# SQLAlchemy database connection using Streamlit secrets
def get_engine():
    try:
        # Get database credentials from Streamlit secrets
        db_config = st.secrets["mysql"]
        connection_string = (
            f"mysql+pymysql://{db_config['username']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

# Test database connection
def test_db():
    engine = get_engine()
    if not engine:
        return
        
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1, 2"))
            row = result.fetchone()
            st.sidebar.success(f"Database test successful! Result: {row}")
    except Exception as e:
        st.sidebar.error(f"Database test failed: {str(e)}")
    finally:
        if engine:
            engine.dispose()

# Scenario 1: Transaction behavior analysis
def scenario_1():
    st.header("📊 Scenario 1: Transaction Behavior Analysis")
    engine = get_engine()
    if not engine:
        return
        
    try:
        # Year selection
        with engine.connect() as conn:
            years = pd.read_sql("SELECT DISTINCT year FROM aggregated_transaction ORDER BY year", conn)['year'].tolist()
        selected_year = st.selectbox("Select Year", years, index=len(years)-1)
        
        with st.spinner("Loading transaction data..."):
            # Query for category trends
            category_query = text(f"""
                SELECT quarter, category, 
                       SUM(count) as total_count, 
                       SUM(amount) as total_amount
                FROM aggregated_transaction
                WHERE year = {selected_year}
                GROUP BY quarter, category
            """)
            
            # Query for state-level trends
            state_query = text(f"""
                SELECT quarter, name AS state, 
                       SUM(count) as total_count, 
                       SUM(amount) as total_amount
                FROM map_transaction_hover
                WHERE year = {selected_year}
                GROUP BY quarter, name
            """)
            
            with engine.connect() as conn:
                category_df = pd.read_sql(category_query, conn)
                state_df = pd.read_sql(state_query, conn)
                
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Transactions", f"{category_df['total_count'].sum():,}")
            col2.metric("Total Amount", f"₹{category_df['total_amount'].sum():,.2f}")
            col3.metric("Regions Covered (States & Districts)", state_df['state'].nunique())
            
            # Category distribution
            st.subheader(f"Transaction Distribution by Category ({selected_year})")
            if not category_df.empty:
                fig = px.pie(
                    category_df.groupby('category')['total_amount'].sum().reset_index(),
                    names='category',
                    values='total_amount',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    title='Transaction Value by Category'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # State performance
            st.subheader(f"State Performance by Quarter ({selected_year})")
            if not state_df.empty:
                top_states = state_df.groupby('state')['total_amount'].sum().nlargest(10).index
                filtered_df = state_df[state_df['state'].isin(top_states)]
                
                fig = px.bar(
                    filtered_df,
                    x='quarter',
                    y='total_amount',
                    color='state',
                    barmode='group',
                    labels={'total_amount': 'Amount (₹)', 'quarter': 'Quarter'},
                    title='Top 10 States by Transaction Amount'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            # Growth trends
            st.subheader(f"Category Growth Trends ({selected_year})")
            if not category_df.empty:
                fig = px.line(
                    category_df,
                    x='quarter',
                    y='total_amount',
                    color='category',
                    markers=True,
                    labels={'total_amount': 'Amount (₹)', 'quarter': 'Quarter'},
                    title='Transaction Growth by Category'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            st.success("Transaction behavior analysis completed!")
            
    except Exception as e:
        st.error(f"Error in Scenario 1: {str(e)}")
    finally:
        if engine:
            engine.dispose()

# Scenario 2: Insurance growth analysis
def scenario_2():
    st.header("🛡️ Scenario 2: Insurance Growth Analysis")
    engine = get_engine()
    if not engine:
        return
        
    try:
        # Year range selection
        with engine.connect() as conn:
            years = pd.read_sql("SELECT DISTINCT year FROM aggregated_insurance ORDER BY year", conn)['year'].tolist()
        start_year, end_year = st.select_slider(
            "Select Year Range",
            options=years,
            value=(min(years), max(years)))
        
        with st.spinner("Loading insurance data..."):
            # Insurance growth query
            growth_query = text(f"""
                SELECT year, quarter, 
                       SUM(count) as total_policies, 
                       SUM(amount) as total_premium
                FROM aggregated_insurance
                WHERE year BETWEEN {start_year} AND {end_year}
                GROUP BY year, quarter
                ORDER BY year, quarter
            """)
            
            # State-level opportunities query
            state_query = text(f"""
                SELECT name AS state, 
                       SUM(count) as total_policies, 
                       SUM(amount) as total_premium
                FROM map_insurance_hover
                WHERE year BETWEEN {start_year} AND {end_year}
                GROUP BY name
            """)
            
            with engine.connect() as conn:
                growth_df = pd.read_sql(growth_query, conn)
                state_df = pd.read_sql(state_query, conn)
                
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Policies", f"{growth_df['total_policies'].sum():,}")
            col2.metric("Total Premium", f"₹{growth_df['total_premium'].sum():,.2f}")
            col3.metric("Regions Covered (States & Districts)", state_df['state'].nunique())
            
            # Growth trends
            st.subheader(f"Insurance Growth ({start_year}-{end_year})")
            if not growth_df.empty:
                growth_df['period'] = growth_df['year'].astype(str) + ' Q' + growth_df['quarter'].astype(str)
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(
                    go.Bar(
                        x=growth_df['period'],
                        y=growth_df['total_policies'],
                        name='Policies',
                        marker_color='#1f77b4'
                    ),
                    secondary_y=False
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=growth_df['period'],
                        y=growth_df['total_premium'],
                        name='Premium (₹)',
                        mode='lines+markers',
                        line=dict(color='#ff7f0e'),
                        marker=dict(size=8)
                    ),
                    secondary_y=True
                )
                
                fig.update_layout(
                    title='Insurance Policy and Premium Growth',
                    xaxis=dict(title='Quarter', tickangle=45),
                    yaxis=dict(title='Number of Policies', color='#1f77b4'),
                    yaxis2=dict(title='Total Premium (₹)', overlaying='y', side='right', color='#ff7f0e'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # State opportunities
            st.subheader("State-Level Opportunities")
            if not state_df.empty:
                # Top states and opportunity states
                top_states = state_df.nlargest(10, 'total_policies')
                opportunity_states = state_df.nsmallest(10, 'total_policies')
                
                fig = make_subplots(rows=1, cols=2, subplot_titles=('Top States by Policies', 'High Opportunity States'))
                
                fig.add_trace(
                    go.Bar(
                        x=top_states['total_policies'],
                        y=top_states['state'],
                        orientation='h',
                        marker_color='#1f77b4',
                        name='Policies'
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Bar(
                        x=opportunity_states['total_policies'],
                        y=opportunity_states['state'],
                        orientation='h',
                        marker_color='#ff7f0e',
                        name='Policies'
                    ),
                    row=1, col=2
                )
                
                fig.update_layout(
                    title='Insurance Market Analysis by State',
                    showlegend=False,
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            st.success("Insurance growth analysis completed!")
            
    except Exception as e:
        st.error(f"Error in Scenario 2: {str(e)}")
    finally:
        if engine:
            engine.dispose()

# Scenario 3: Transaction trends analysis
def scenario_3():
    st.header("📈 Scenario 3: Transaction Trends Analysis")
    engine = get_engine()
    if not engine:
        return
        
    try:
        # Filters
        with engine.connect() as conn:
            years = pd.read_sql("SELECT DISTINCT year FROM aggregated_transaction ORDER BY year", conn)['year'].tolist()
            categories = pd.read_sql("SELECT DISTINCT category FROM aggregated_transaction", conn)['category'].tolist()
        
        col1, col2 = st.columns(2)
        selected_year = col1.selectbox("Select Year", years, index=len(years)-1, key='sc3_year')
        selected_categories = col2.multiselect("Select Categories", categories, default=categories, key='sc3_cat')
        
        with st.spinner("Loading transaction trend data..."):
            # Category trends query
            category_query = text(f"""
                SELECT quarter, category, 
                       SUM(count) as total_count, 
                       SUM(amount) as total_amount
                FROM aggregated_transaction
                WHERE year = {selected_year}
                {'AND category IN (' + ','.join([f"'{cat}'" for cat in selected_categories]) + ')' if selected_categories else ''}
                GROUP BY quarter, category
            """)
            
            # Regional trends query
            region_query = text(f"""
                SELECT quarter, name AS region, 
                       SUM(count) as total_count, 
                       SUM(amount) as total_amount
                FROM map_transaction_hover
                WHERE year = {selected_year}
                GROUP BY quarter, name
            """)
            
            with engine.connect() as conn:
                category_df = pd.read_sql(category_query, conn)
                region_df = pd.read_sql(region_query, conn)
                
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Transactions", f"{category_df['total_count'].sum():,}")
            col2.metric("Total Amount", f"₹{category_df['total_amount'].sum():,.2f}")
            col3.metric("Regions Covered", region_df['region'].nunique())
            
            # Category trends
            st.subheader(f"Category Trends ({selected_year})")
            if not category_df.empty:
                fig = px.line(
                    category_df,
                    x='quarter',
                    y='total_amount',
                    color='category',
                    markers=True,
                    labels={'total_amount': 'Amount (₹)', 'quarter': 'Quarter'},
                    title='Transaction Value by Category'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Regional heatmap
            st.subheader(f"Regional Performance Heatmap ({selected_year})")
            if not region_df.empty:
                pivot_df = region_df.pivot(index='region', columns='quarter', values='total_amount').fillna(0)
                
                fig = px.imshow(
                    pivot_df,
                    labels=dict(x="Quarter", y="Region", color="Amount (₹)"),
                    color_continuous_scale='YlGnBu',
                    aspect="auto"
                )
                fig.update_layout(
                    title='Transaction Amount by Region and Quarter',
                    xaxis=dict(tickangle=0),
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Expansion opportunities
            st.subheader("Expansion Opportunity Analysis")
            if not region_df.empty:
                region_growth = region_df.groupby('region')['total_amount'].sum().reset_index()
                region_growth['growth_potential'] = region_growth['total_amount'].rank(pct=True)
                
                fig = px.scatter(
                    region_growth,
                    x='total_amount',
                    y='growth_potential',
                    size='total_amount',
                    color='growth_potential',
                    hover_name='region',
                    color_continuous_scale='RdYlGn',
                    labels={'total_amount': 'Total Amount (₹)', 'growth_potential': 'Growth Potential'},
                    title='Region Growth Potential Analysis'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            st.success("Transaction trend analysis completed!")
            
    except Exception as e:
        st.error(f"Error in Scenario 3: {str(e)}")
    finally:
        if engine:
            engine.dispose()

# Scenario 4: Top-performing locations
def scenario_4():
    st.header("🏆 Scenario 4: Top-Performing Locations")
    engine = get_engine()
    if not engine:
        return
        
    try:
        # Entity level selection
        entity_level = st.radio("Select Entity Level", ['state', 'district', 'pincode'], index=0, horizontal=True)
        
        with st.spinner("Loading top location data..."):
            # Top locations query
            query = text(f"""
                SELECT entity_name, 
                       SUM(count) as total_count, 
                       SUM(amount) as total_amount
                FROM top_transaction
                WHERE entity_level = '{entity_level}'
                GROUP BY entity_name
                ORDER BY total_amount DESC
                LIMIT 20
            """)
            
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
                
            # Metrics
            col1, col2 = st.columns(2)
            col1.metric("Total Transactions", f"{df['total_count'].sum():,}")
            col2.metric("Total Amount", f"₹{df['total_amount'].sum():,.2f}")
            
            # Top locations
            st.subheader(f"Top 20 {entity_level.capitalize()}s by Transaction Amount")
            if not df.empty:
                df = df.sort_values('total_amount', ascending=False)
                
                fig = px.bar(
                    df,
                    x='entity_name',
                    y='total_amount',
                    color='total_amount',
                    color_continuous_scale='Viridis',
                    labels={'total_amount': 'Amount (₹)', 'entity_name': entity_level.capitalize()},
                    title=f'Top {entity_level.capitalize()}s by Transaction Value'
                )
                fig.update_layout(xaxis=dict(tickangle=45))
                st.plotly_chart(fig, use_container_width=True)
            
            # Performance distribution
            st.subheader("Performance Distribution")
            if not df.empty:
                fig = px.box(
                    df,
                    y='total_amount',
                    points='all',
                    labels={'total_amount': 'Amount (₹)'},
                    title='Transaction Amount Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            st.success("Top location analysis completed!")
            
    except Exception as e:
        st.error(f"Error in Scenario 4: {str(e)}")
    finally:
        if engine:
            engine.dispose()

# Scenario 5: Top user registration locations
def scenario_5():
    st.header("👥 Scenario 5: Top User Registration Locations")
    engine = get_engine()
    if not engine:
        return
        
    try:
        # Year-quarter selection
        with engine.connect() as conn:
            year_quarters = pd.read_sql("""
                SELECT DISTINCT CONCAT(year, ' Q', quarter) AS yq 
                FROM top_user 
            """, conn)['yq'].tolist()
        
        selected_yq = st.selectbox("Select Year-Quarter", year_quarters, index=0)
        year, quarter = selected_yq.split(' Q')
        
        with st.spinner("Loading user registration data..."):
            # Registration locations query
            query = text(f"""
                SELECT entity_level, entity_name, 
                       SUM(registered_users) as total_users
                FROM top_user
                WHERE year = {year} AND quarter = {quarter}
                GROUP BY entity_level, entity_name
                ORDER BY total_users DESC
                LIMIT 20
            """)
            
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
                
            # Metrics
            col1, col2 = st.columns(2)
            col1.metric("Total Registered Users", f"{df['total_users'].sum():,}")
            col2.metric("Locations Covered", df['entity_name'].nunique())
            
            # Top locations
            st.subheader(f"Top 20 Registration Locations ({selected_yq})")
            if not df.empty:
                df = df.sort_values('total_users', ascending=False)
                
                fig = px.bar(
                    df,
                    x='entity_name',
                    y='total_users',
                    color='entity_level',
                    labels={'total_users': 'Registered Users', 'entity_name': 'Location'},
                    title='Top Registration Locations'
                )
                fig.update_layout(xaxis=dict(tickangle=45))
                st.plotly_chart(fig, use_container_width=True)
            
            # Geographical distribution
            st.subheader("Geographical Distribution")
            if not df.empty:
                fig = px.treemap(
                    df,
                    path=['entity_level', 'entity_name'],
                    values='total_users',
                    color='total_users',
                    color_continuous_scale='RdBu',
                    title='User Registration Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
                
            st.success("User registration analysis completed!")
            
    except Exception as e:
        st.error(f"Error in Scenario 5: {str(e)}")
    finally:
        if engine:
            engine.dispose()

# Streamlit app configuration
st.set_page_config(
    page_title="PhonePe Data Analysis Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main dashboard
st.title("📱 PhonePe Data Analysis Dashboard")
st.markdown("""
    Comprehensive analysis of PhonePe transaction, insurance, and user data 
    to identify growth opportunities and strategic insights.
""")

# Sidebar configuration
with st.sidebar:
    st.header("Database Status")
    if st.button("Test Database Connection"):
        test_db()
    
    st.divider()
    
    st.header("Analysis Scenarios")
    scenario = st.selectbox(
        "Select Analysis Scenario",
        ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4", "Scenario 5"]
    )
    
    st.divider()
    
    st.header("About")
    st.info("""
        This dashboard provides insights into PhonePe's transaction patterns, 
        insurance growth, user registrations, and top-performing locations.
        Data is sourced from PhonePe's internal databases.
    """)
    
    st.divider()
    st.caption("PhonePe Data Analysis | v1.0 | 2023")

# Execute selected scenario
if scenario == "Scenario 1":
    scenario_1()
elif scenario == "Scenario 2":
    scenario_2()
elif scenario == "Scenario 3":
    scenario_3()
elif scenario == "Scenario 4":
    scenario_4()
elif scenario == "Scenario 5":
    scenario_5()