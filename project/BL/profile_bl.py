def form_response(data):
    return {
            "user_role": data[0],
            "user_name": data[1],
            "tg_username": data[2],
            "phone": data[3],
            "photo": data[4],
            "rating": float(data[5]),
            "review_count": data[6]
        }