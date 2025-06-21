def form_response(data):
    return {
            "user_role": data[0],
            "user_name": data[1],
            "email": data[2],
            "phone": data[3],
            "photo": data[4],
            "rating": float(data[5]),
            "xp": data[6],
            "organization_name": data[7]
        }