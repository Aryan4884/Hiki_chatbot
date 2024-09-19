import streamlit as st
import pandas as pd
import nltk
import re

nltk.download('punkt')
nltk.download('punkt_tab')

# Load data from CSV files
products_data = pd.read_csv('products.csv')
customers_data = pd.read_csv('customers.csv')
orders_data = pd.read_csv('orders.csv')
stores_data = pd.read_csv('stores.csv')

# Clean and prepare data
products_data['Price'] = products_data['Price'].replace({'\? ': '', ',': ''}, regex=True).astype(float, errors='ignore')

# Initialize conversation state in session_state
if 'conversation_state' not in st.session_state:
    st.session_state.conversation_state = {
        'expecting_budget': False,
        'expecting_order_details': False,
        'product_function': None
    }

# Welcome message
def welcome_message():
    return "Hello! I am RetailX Assistant. How can I help you today?"

# Function to filter products by category
def filter_products_by_category(df, category):
    return df[df['Category'].str.contains(category, case=False, na=False)]

# Functions to get products based on specific categories
def get_computers(df, min_budget=None, max_budget=None):
    return filter_products_by_category_and_budget(df, 'Computers', min_budget, max_budget)

def get_electronics(df, min_budget=None, max_budget=None):
    return filter_products_by_category_and_budget(df, 'Electronics', min_budget, max_budget)

def get_home_appliances(df, min_budget=None, max_budget=None):
    return filter_products_by_category_and_budget(df, 'Home Appliances', min_budget, max_budget)

# Function to handle user input and return relevant products
def handle_user_input(user_input):
    user_input_lower = user_input.lower()
    response = process_query(user_input_lower)
    st.write(response)

# Process the user query
def process_query(user_input):
    tokens = nltk.word_tokenize(user_input)

    # Handle conversation states using session_state
    if st.session_state.conversation_state['expecting_budget']:
        return recommend_product_by_budget(user_input)

    if st.session_state.conversation_state['expecting_order_details']:
        return track_order_by_details(user_input)

    # Handle specific product queries with size or feature
    size_keywords = re.findall(r'\d+-inch', user_input, re.IGNORECASE)
    feature_keywords = ['4k', 'hdr', 'smart', 'wifi']  # Add more features as needed

    if any(size in user_input for size in size_keywords) and any(feature in user_input for feature in feature_keywords):
        st.session_state.conversation_state['expecting_budget'] = True
        return f"Yes, we have several options. Can you please specify your budget for a {user_input}?"
    

    elif 'computer' in user_input or 'computers' in user_input:
        st.session_state.conversation_state['expecting_budget'] = True
        st.session_state.conversation_state['product_function'] = get_computers
        return "Sure! You mentioned computers. Can you please specify your budget for the computers?"

    elif 'electronics' in user_input:
        st.session_state.conversation_state['expecting_budget'] = True
        st.session_state.conversation_state['product_function'] = get_electronics
        return "Sure! You mentioned electronics. Can you please specify your budget for the electronics?"

    elif 'appliance' in user_input:
        st.session_state.conversation_state['expecting_budget'] = True
        st.session_state.conversation_state['product_function'] = get_home_appliances
        return "Sure! You mentioned home appliances. Can you please specify your budget for the home appliances?"
    
   
    # Handle other queries
    if "return" in tokens or "returning" in tokens:
        return handle_return(user_input)
    
    elif "last order" in user_input.lower():
          return get_last_order_date(user_input)
        
    elif "order" in user_input.lower() or "status" in user_input.lower() or "received" in user_input.lower() or "ordered" in user_input.lower() or "receive" in user_input.lower():
        st.session_state.conversation_state['expecting_order_details'] = True
        return "Sure. Please provide your customer ID and product name to track your order."
    
    elif "cancel" in tokens or "cancellation" in tokens:
        return handle_cancellation(user_input)

    elif "stock" in tokens or "stocks" in tokens:
        return check_stock(user_input)
    
    elif "how many stores" in user_input.lower() or "number of stores" in user_input.lower():
        return store_count(user_input)

    elif "store" in tokens or "stores" in tokens or "location" in tokens or "branch" in tokens or "branches" in tokens:
        return store_locator(user_input)


    elif "find product" in user_input and "id" in user_input:
        return find_product_name_by_id(user_input)

    # Handle general queries about product types
    product_keywords = ['mobile', 'tv', 'laptop', 'tablet', 'camera']  # Add more as needed
    for keyword in product_keywords:
        if keyword in user_input:
            st.session_state.conversation_state['product_type'] = keyword.capitalize()  # Save product type
            st.session_state.conversation_state['expecting_budget'] = True
            return f"Yes, of course. Can you please specify your budget for the {keyword}?"
        
    # Handle product-specific queries based on previously saved product_type
    product_type = st.session_state.conversation_state.get('product_type')
    if product_type:
        st.session_state.conversation_state['expecting_budget'] = True
        return f"Yes, you are looking for {product_type}. Can you please specify your budget?"
    
        
    return "Sorry, I didn't understand that. Could you please rephrase?"

    
def filter_products_by_category_and_budget(df, category, min_budget=None, max_budget=None):
    filtered_df = filter_products_by_category(df, category)
    
    if min_budget is not None and max_budget is not None:
        filtered_df = filtered_df[
            (filtered_df['Price'] >= min_budget) &
            (filtered_df['Price'] <= max_budget)
        ]
    
    return filtered_df

# Feature 1: Recommend mobile based on budget
import pandas as pd

# Example data
data = {
    'ProductName': [
        'Lenovo Fugit Pariatur', 'Godrej Praesentium Dolorum', 'Samsung Voluptatibus Ipsa',
        'Sony Ex Unde', 'Samsung Sint Commodi', 'Samsung Possimus Magnam', 'Dell Eaque Maiores',
        'Whirlpool Officiis Aspernatur', 'Xiaomi Totam Facere', 'Apple Eaque Voluptatem',
        'Samsung Rerum Quidem', 'Xiaomi Magni Labore', 'LG At Dolores', 'Apple Ad Minima',
        'Godrej Mollitia Placeat', 'Lenovo Perferendis Perspiciatis', 'Samsung Eos Voluptas',
        'Acer Assumenda Eius', 'HP Ut Doloremque', 'Samsung Cumque Odio', 'Dell Dolore Soluta',
        # Add more products here
    ],
    'Price': [
        15000, 12000, 30000, 25000, 18000, 21000, 24000, 27000, 19000, 22000,
        23000, 20000, 26000, 24000, 22000, 25000, 23000, 26000, 28000, 27000,
        # Add more prices here
    ]
}

# Define company to product type mapping
company_to_product_type = {
    'Whirlpool': 'Appliance',
    'Xiaomi': 'Mobile',
    'Acer': 'Laptop',
    'Samsung': 'Mobile',
    'Godrej': 'Appliance',
    'HP': 'Laptop',
    'Sony': 'Electronics',
    'Apple': 'Mobile',
    'Dell': 'Laptop',
    'Lenovo': 'Laptop',
    'Panasonic': 'Electronics',
    'OnePlus': 'Mobile'
}

# Define a list of supported product types
supported_product_types = ['mobile', 'laptop', 'appliance', 'electronics', 'tv']

def extract_company_from_product_name(product_name):
    for company in company_to_product_type.keys():
        if company.lower() in product_name.lower():
            return company
    return None

def extract_product_type_from_input(user_input):
    """Extract product type from user input by checking against the supported product types."""
    for product_type in supported_product_types:
        if product_type in user_input.lower():
            return product_type.capitalize()  # Capitalize to match the format in `company_to_product_type`
    return None

def recommend_product_by_budget(user_input):
    # Extract budget range from user input
    budget_tokens = [int(s) for s in user_input.split() if s.isdigit()]

    if len(budget_tokens) == 2:
        budget_min, budget_max = budget_tokens
    else:
        return "Please specify a valid budget range."

    # Extract the product type from the user input
    product_type = extract_product_type_from_input(user_input)
    if not product_type:
        return "Sorry, we currently can't handle your request. Please specify a valid product type (e.g. Mobile, Laptop, Appliance, etc. along with the budget range like, laptop ranging between 20000 to 40000)."

    # Filter products based on extracted budget
    filtered_products = products_data[
        (products_data['Price'] >= budget_min) & 
        (products_data['Price'] <= budget_max)
    ]

    # Further filter to include only the specified product type
    filtered_products = filtered_products[
        filtered_products['ProductName'].apply(
            lambda name: company_to_product_type.get(extract_company_from_product_name(name), '') == product_type
        )
    ]

    if not filtered_products.empty:
        product_list = '\n '.join(filtered_products['ProductName'].tolist())
        return f"Here are the {product_type.lower()} options in your budget:\n{product_list}"
    else:
        return f"Sorry, no {product_type.lower()}s are available in your specified budget."

def recommend_laptops_by_budget(user_input):
    # Extract budget range from user input
    min_budget, max_budget = extract_budget_from_input(user_input)
    
    if min_budget is None or max_budget is None:
        return "Please specify a valid budget range."

    # Filter products based on extracted company and budget
    filtered_products = products_data[
        (products_data['Price'] >= min_budget) &
        (products_data['Price'] <= max_budget)
    ]
    
    # Further filter to include only laptops
    filtered_products = filtered_products[
        filtered_products['ProductName'].apply(
            lambda name: company_to_product_type.get(extract_company_from_product_name(name), '') == 'Laptop'
        )
    ]

    if not filtered_products.empty:
        product_list = '\n '.join(filtered_products['ProductName'].tolist())
        return f"Here are the laptop options in your budget: \n{product_list}"
    else:
        return "Sorry, no laptops are available in your specified budget."

def recommend_tvs_by_budget(user_input):
    # Extract budget range from user input
    min_budget, max_budget = extract_budget_from_input(user_input)
    
    if min_budget is None or max_budget is None:
        return "Please specify a valid budget range."

    # Filter products based on extracted company and budget
    filtered_products = products_data[
        (products_data['Price'] >= min_budget) &
        (products_data['Price'] <= max_budget)
    ]
    
    # Further filter to include only TVs (Electronics in this example)
    filtered_products = filtered_products[
        filtered_products['ProductName'].apply(
            lambda name: company_to_product_type.get(extract_company_from_product_name(name), '') == 'Electronics'
        )
    ]

    if not filtered_products.empty:
        product_list = '\n '.join(filtered_products['ProductName'].tolist())
        return f"Here are the TV options in your budget: \n{product_list}"
    else:
        return "Sorry, no TVs are available in your specified budget."

def recommend_cameras_by_budget(user_input):
    # Extract budget range from user input
    min_budget, max_budget = extract_budget_from_input(user_input)
    
    if min_budget is None or max_budget is None:
        return "Please specify a valid budget range."

    # Filter products based on extracted company and budget
    filtered_products = products_data[
        (products_data['Price'] >= min_budget) &
        (products_data['Price'] <= max_budget)
    ]
    
    # Further filter to include only cameras (Electronics in this example)
    filtered_products = filtered_products[
        filtered_products['ProductName'].apply(
            lambda name: company_to_product_type.get(extract_company_from_product_name(name), '') == 'Electronics'
        )
    ]

    if not filtered_products.empty:
        product_list = '\n '.join(filtered_products['ProductName'].tolist())
        return f"Here are the camera options in your budget: \n{product_list}"
    else:
        return "Sorry, no cameras are available in your specified budget."

def recommend_refrigerators_by_budget(user_input):
    # Extract budget range from user input
    min_budget, max_budget = extract_budget_from_input(user_input)
    
    if min_budget is None or max_budget is None:
        return "Please specify a valid budget range."

    # Filter products based on extracted company and budget
    filtered_products = products_data[
        (products_data['Price'] >= min_budget) &
        (products_data['Price'] <= max_budget)
    ]
    
    # Further filter to include only refrigerators (Appliance in this example)
    filtered_products = filtered_products[
        filtered_products['ProductName'].apply(
            lambda name: company_to_product_type.get(extract_company_from_product_name(name), '') == 'Appliance'
        )
    ]

    if not filtered_products.empty:
        product_list = '\n '.join(filtered_products['ProductName'].tolist())
        return f"Here are the refrigerator options in your budget: \n{product_list}"
    else:
        return "Sorry, no refrigerators are available in your specified budget."


# Feature 2: Check stock availability for a product
def check_stock(user_input):
    for product_name in products_data['ProductName']:
        if product_name.lower() in user_input.lower():
            stock_level = products_data[products_data['ProductName'].str.lower() == product_name.lower()]['Stock'].values[0]
            # Example recommendation logic; adjust based on actual sales data
            if stock_level < 10:
                recommendation = "Based on recent sales trends, I recommend reordering in the next week to avoid stockouts."
            else:
                recommendation = "Stock levels are sufficient. However, consider monitoring sales trends for any changes."

            return f"We currently have {stock_level} units of {product_name} in stock. {recommendation} Would you like me to place an order for you?"

    return "Sorry, I couldn't find stock information for that product."

# Feature 3: Locate store by city or state
def store_locator(user_input):
    for city in stores_data['City']:
        if city.lower() in user_input.lower():
            store_info = stores_data[stores_data['City'].str.lower() == city.lower()].iloc[0]
            return f"Yes, we have a branch in {city}. Store Name: {store_info['StoreName']}, Address: {store_info['Address']}, Phone: {store_info['Phone']}"

    for state in stores_data['State']:
        if state.lower() in user_input.lower():
            store_info = stores_data[stores_data['State'].str.lower() == state.lower()].iloc[0]
            return f"Yes, we have a branch in {store_info['City']}, {state}. Store Name: {store_info['StoreName']}, Address: {store_info['Address']}, Phone: {store_info['Phone']}"

    return "Sorry, no store found in the location mentioned."

# Feature 4: Count stores in a state or city
def store_count(user_input):
    for state in stores_data['State']:
        if state.lower() in user_input.lower():
            store_count = len(stores_data[stores_data['State'].str.lower() == state.lower()])
            return f"We have {store_count} stores in {state}."

    for city in stores_data['City']:
        if city.lower() in user_input.lower():
            store_count = len(stores_data[stores_data['City'].str.lower() == city.lower()])
            return f"We have {store_count} stores in {city}."

    return "Sorry, I couldn't find store information for that location."

# Feature 5: Track order by customer ID and product name
def track_order_by_details(user_input):
    global conversation_state
    st.session_state.conversation_state['expecting_order_details'] = False

    # Convert CustomerID and ProductID columns to integers
    products_data['ProductID'] = pd.to_numeric(products_data['ProductID'], errors='coerce')
    orders_data['CustomerID'] = pd.to_numeric(orders_data['CustomerID'], errors='coerce')

    # Tokenize the input
    tokens = nltk.word_tokenize(user_input.lower())

    # Extract numeric tokens using regular expressions
    numeric_tokens = re.findall(r'\b\d+\b', user_input)
    numeric_values = [int(token) for token in numeric_tokens]

    customer_id = None
    product_id = None
    product_name = "the respective product"

    # Try to find a valid customer ID from the numeric values
    for value in numeric_values:
        if value in orders_data['CustomerID'].values:
            customer_id = value
            break

    # Try to find a valid product ID from the numeric values
    for value in numeric_values:
        if value in orders_data['ProductID'].values:
            product_id = value
            break

    # Extract the product name from the input by comparing with product names in the data
    for product in products_data['ProductName']:
        if product.lower() in user_input.lower():
            product_name = product
            break

    # Check if customer ID is found
    if customer_id is None:
        return "Sorry, I couldn't find the customer ID. Please provide a valid customer ID."

    # Check if product name is found
    if product_name is None and product_id is None:
        return "Sorry, I couldn't find the product name or product ID. Please provide the correct product details."

    # If product ID is not provided, try to find it from the product name
    if product_id is None and product_name is not None:
        product_id_series = products_data[products_data['ProductName'].str.lower() == product_name.lower()]['ProductID']
        if not product_id_series.empty:
            product_id = product_id_series.values[0]

    # Check if product ID is found
    if product_id is None:
        return "Sorry, I couldn't find the product ID for the given product name."

    # Filter the orders_data using customer ID and product ID
    order = orders_data[(orders_data['CustomerID'] == customer_id) | (orders_data['ProductID'] == product_id)]

    # Check if any matching order is found
    if not order.empty:
        order_status = order['Status'].values[0]

        return f"The status of your order for {product_name} is {order_status}. Please wait for its delivery."

    return "Sorry, I couldn't find any order for that customer ID and product."

# Feature 6: Get last order date by customer name
def get_last_order_date(user_input):
    for customer_name in customers_data['Name']:
        if customer_name.lower() in user_input.lower():
            last_order_date = customers_data[customers_data['Name'] == customer_name]['LastOrderDate'].values[0]
            return f"Your last order date was {last_order_date}."

    return "Sorry, I couldn't find your last order date."

# Feature 7: Handle product returns
def handle_return(user_input):
    # Extract order number if provided
    order_number = re.findall(r'\b\d+\b', user_input)

    if order_number:
        order_number = order_number[0]
        # Check if the order number exists in the orders data
        if order_number in orders_data['OrderID'].values:
            return f"I've found your order with number {order_number}. You can initiate the return by following our return policy. If you need further assistance, please let me know."
        else:
            return "Sorry, I couldn't find an order with that number. Please make sure the order number is correct."

    return "Please provide your order number so I can assist you with the return process."

# Feature 8: Handle order cancellation
def handle_cancellation(user_input):
    # Extract order number from user input
    order_number = re.findall(r'\b\d+\b', user_input)

    if order_number:
        order_number = order_number[0]
        # Check if the order number exists in the orders data
        if order_number in orders_data['OrderID'].values:
            # Assuming you have a column 'Status' to check if the order can be canceled
            order_status = orders_data[orders_data['OrderID'] == order_number]['Status'].values[0]
            if order_status in ['Pending', 'Processing']:
                # Update status to 'Cancelled' or similar, depending on your system
                orders_data.loc[orders_data['OrderID'] == order_number, 'Status'] = 'Cancelled'
                return f"Your order with number {order_number} has been successfully canceled. If you need any further assistance, please let me know."
            else:
                return f"Sorry, your order with number {order_number} cannot be canceled as it is already {order_status}."
        else:
            return "Sorry, I couldn't find an order with that number. Please make sure the order number is correct."

    return "Please provide your order number so I can assist you with the cancellation process."



def find_product_name_by_id(user_input):
    # Extract product ID from the user input
    product_id_tokens = re.findall(r'\b\d+\b', user_input)
    if product_id_tokens:
        product_id = int(product_id_tokens[0])
        product_info = products_data[products_data['ProductID'] == product_id]
        if not product_info.empty:
            product_name = product_info['ProductName'].values[0]
            return f"The product name for ID {product_id} is {product_name}."
        else:
            return "Sorry, no product found with that ID."
    else:
        return "Please provide a valid product ID."

# Main function to run the app
def main():
    st.title("RetailX Assistant")
    st.write(welcome_message())

    user_input = st.text_input("How can I assist you today?")

    if user_input:
        handle_user_input(user_input)

if __name__ == "__main__":
    main()
