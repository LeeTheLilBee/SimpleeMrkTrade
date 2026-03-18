from engine.exit_engine import check_exit

def review_exit(current_price, stop_price, target_price):
    return check_exit(current_price, stop_price, target_price)
