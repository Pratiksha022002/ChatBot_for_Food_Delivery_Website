from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}


@app.post("/")
async def handle_request(request: Request):
    try:
        # Log the raw request body
        raw_body = await request.body()
        print(f"Raw request body: {raw_body}")

        # Retrieve the JSON data from the request
        payload = await request.json()
        print(f"Received payload from Dialogflow: {payload}")

        # Extract information from the payload
        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']
        session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

        intent_handler_dict = {
            'order.add-context: ongoing-order': add_to_order,
            'order.remove-context: ongoing-order': remove_from_order,
            'order.complete-context: ongoing-order': complete_order,
            'track.order-context: ongoing-tracking': track_order
        }

        return intent_handler_dict[intent](parameters, session_id)

    except ValueError as e:
        print(f"JSON parsing error: {e}")
        return JSONResponse(content={"fulfillmentText": "Invalid JSON payload."}, status_code=400)
    except KeyError as e:
        print(f"Key error: {e}")
        return JSONResponse(content={"fulfillmentText": "Missing required data in request."}, status_code=400)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JSONResponse(content={"fulfillmentText": "An error occurred. Please try again."}, status_code=500)


def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)
        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id, "in progress")
    return next_order_id


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please try again."
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Order placed! Order ID: {order_id}. Total: {order_total} to be paid at delivery."

        del inprogress_orders[session_id]

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def add_to_order(parameters: dict, session_id: str):
    quantities = parameters.get("number", [])
    food_items = parameters.get("food_item", [])
    print(quantities,food_items)
    if len(food_items) != len(quantities):
        fulfillment_text = "Please specify food items and quantities clearly."
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Can you place a new order please?"
        })

    food_items = parameters.get("food_item", [])
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item in current_order:
            removed_items.append(item)
            del current_order[item]
        else:
            no_such_items.append(item)

    fulfillment_text = f'Removed {",".join(removed_items)} from your order.' if removed_items else ""
    if no_such_items:
        fulfillment_text += f' No such items: {",".join(no_such_items)}.'

    if current_order:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"
    else:
        fulfillment_text += " Your order is empty."

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def track_order(parameters: dict, session_id: str):
    order_id = int(parameters.get("number"))  # Ensure 'number' is the correct key
    print(f"Extracted order_id: {order_id}")  # Check what order_id is extracted

    if order_id is None:
        fulfillment_text = "No order ID found."
    else:
        order_status = db_helper.get_order_status(order_id)
        print(f"Order status retrieved from database: {order_status}")

        if order_status:
            fulfillment_text = f"The order status for ID {order_id} is: {order_status}."
        else:
            fulfillment_text = f"No order found with ID {order_id}."

    return JSONResponse(content={"fulfillmentText": fulfillment_text})
